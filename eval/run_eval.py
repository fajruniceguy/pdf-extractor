"""Minimal eval: 15 labeled questions against document 3 (POL Whitepaper).

    python eval/run_eval.py

Reports answer accuracy, citation accuracy and correct-refusal rate, and saves
raw results to eval/results.json. Answers are graded by checking that the
expected facts appear in the answer text (numbers normalised, so 10 billion,
10,000,000,000 and 10B all match). Partial matches are UNSURE, never guessed.
"""
from __future__ import annotations

import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from extractor.answer import MODEL, answer  # noqa: E402

DOCUMENT_ID = 3
QUESTIONS_PATH = ROOT / "eval" / "questions.json"
RESULTS_PATH = ROOT / "eval" / "results.json"

# Facts an answerable question's answer must contain, keyed by question id.
#   ("num", value, unit)  a quantity equal to value; unit "$" or "%" must be attached, None = any
#   ("re", pattern)       a case-insensitive regex that must match the answer text
# All facts present -> PASS, none -> FAIL, some -> UNSURE.
FACTS: dict[int, list[tuple]] = {
    1: [("num", 10e9, None)],
    2: [("re", r"validator"), ("re", r"treasury"), ("num", 1, "%")],
    3: [("num", 10, None), ("re", r"year")],
    4: [("num", 100e6, None)],
    5: [("num", 30, "%"), ("num", 40, "%")],
    6: [("num", 4, "%"), ("num", 5, "%")],
    7: [("num", 5, "$")],
    8: [("num", 6000, "$")],
    9: [("re", r"activation"), ("re", r"subscription"), ("re", r"validation"), ("re", r"retire")],
    10: [("re", r"\blend\b"), ("re", r"migrat"), ("re", r"governance")],
}

_SCALE = {"billion": 1e9, "bn": 1e9, "b": 1e9, "million": 1e6, "mn": 1e6, "m": 1e6,
          "thousand": 1e3, "k": 1e3}
_QTY = re.compile(
    r"(?P<cur>\$|usd\s*)?\s*(?P<num>\d+(?:\.\d+)?)"
    r"(?:\s*(?P<word>billion|million|thousand|bn|mn)\b|(?P<letter>[bmk])\b)?"
    r"(?:\s*(?P<pct>%|percent\b))?(?P<cur2>\s*(?:usd|dollars?)\b)?",
    re.IGNORECASE,
)
_RANGE_GAP = re.compile(r"^\s*(?:-|–|—|to)\s*$", re.IGNORECASE)
_CITATION = re.compile(r"\[[^\[\]]*?page\s+\d+\]", re.IGNORECASE)


def _clean(text: str) -> str:
    text = _CITATION.sub(" ", text)  # filenames/pages inside citations are not facts
    return re.sub(r"(?<=\d),(?=\d{3}\b)", "", text)  # 6,000 -> 6000


def _quantities(text: str) -> list[dict]:
    found = []
    matches = list(_QTY.finditer(text))
    for m in matches:
        scale = _SCALE[(m.group("word") or m.group("letter") or "").lower()] if (
            m.group("word") or m.group("letter")
        ) else 1
        found.append({
            "value": float(m.group("num")) * scale,
            "cur": bool(m.group("cur") or m.group("cur2")),
            "pct": bool(m.group("pct")),
        })
    for i in range(len(matches) - 1):  # "30-40%": the unit applies to the whole range
        gap = text[matches[i].end():matches[i + 1].start()]
        if _RANGE_GAP.match(gap):
            found[i]["pct"] = found[i]["pct"] or found[i + 1]["pct"]
            found[i]["cur"] = found[i]["cur"] or found[i + 1]["cur"]
    return found


def _fact_present(fact: tuple, text: str, quantities: list[dict]) -> bool:
    if fact[0] == "re":
        return re.search(fact[1], text, re.IGNORECASE) is not None
    _, value, unit = fact
    return any(
        math.isclose(q["value"], value, rel_tol=1e-9)
        and (unit != "$" or q["cur"])
        and (unit != "%" or q["pct"])
        for q in quantities
    )


def grade_answerable(q: dict, result) -> tuple[str, str]:
    if not result.stated:
        return "FAIL", "refused an answerable question"
    text = _clean(result.answer)
    quantities = _quantities(text)
    facts = FACTS[q["id"]]
    hits = [_fact_present(f, text, quantities) for f in facts]
    detail = f"{sum(hits)}/{len(facts)} expected facts found"
    if all(hits):
        return "PASS", detail
    if not any(hits):
        return "FAIL", detail + " (answer was stated but contains none of them)"
    missing = [f for f, h in zip(facts, hits) if not h]
    return "UNSURE", detail + f"; missing {missing}"


def main() -> int:
    sys.stdout.reconfigure(errors="replace")
    questions = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    rows = []

    for q in questions:
        row = {"id": q["id"], "category": q["category"], "question": q["question"],
               "expected_answer": q["expected_answer"], "expected_pages": q["expected_pages"]}
        try:
            result = answer(q["question"], document_id=DOCUMENT_ID)
        except RuntimeError as e:
            row.update(grade="ERROR", detail=str(e))
            rows.append(row)
            print(f"[{q['id']:>2}] ERROR: {e}", file=sys.stderr)
            continue

        cited_pages = sorted({page for _, page in result.citations})
        if q["category"] == "absent":
            grade = "PASS" if not result.stated else "FAIL"
            detail = "refused" if grade == "PASS" else "answered a question whose answer is absent"
        else:
            grade, detail = grade_answerable(q, result)

        retrieved_pages = [r.page_number for r in result.retrieved]
        row.update(
            grade=grade, detail=detail, stated=result.stated, answer=result.answer,
            raw_output=result.raw_output, note=result.note,
            cited_pages=cited_pages,
            citation_hit=bool(set(cited_pages) & set(q["expected_pages"])) if q["expected_pages"] else None,
            expected_page_retrieved=bool(set(retrieved_pages) & set(q["expected_pages"])) if q["expected_pages"] else None,
            retrieved=[{"page": r.page_number, "score": round(r.similarity, 4)} for r in result.retrieved],
            top_score=round(result.retrieved[0].similarity, 3) if result.retrieved else None,
            input_tokens=result.input_tokens, output_tokens=result.output_tokens,
            cost_usd=result.cost_usd, stop_reason=result.stop_reason,
        )
        rows.append(row)

    answerable = [r for r in rows if r["category"] == "answerable"]
    absent = [r for r in rows if r["category"] == "absent"]
    passed = [r for r in answerable if r["grade"] == "PASS"]
    unsure = [r for r in answerable if r["grade"] == "UNSURE"]
    failed = [r for r in answerable if r["grade"] in ("FAIL", "ERROR")]
    cite_ok = [r for r in passed if r.get("citation_hit")]
    refused = [r for r in absent if r["grade"] == "PASS"]
    tokens_in = sum(r.get("input_tokens", 0) for r in rows)
    tokens_out = sum(r.get("output_tokens", 0) for r in rows)
    cost = sum(r.get("cost_usd", 0.0) for r in rows)

    print(f"{'id':>3} {'category':<10} {'grade':<7} {'stated':<7} {'pages cited':<12} {'expected':<9} {'cite':<5} top score")
    for r in rows:
        if r["grade"] == "ERROR":
            print(f"{r['id']:>3} {r['category']:<10} ERROR")
            continue
        cited = ",".join(map(str, r["cited_pages"])) or "-"
        expected = ",".join(map(str, r["expected_pages"])) or "-"
        cite = "-" if r["citation_hit"] is None or r["grade"] != "PASS" else ("ok" if r["citation_hit"] else "MISS")
        print(f"{r['id']:>3} {r['category']:<10} {r['grade']:<7} {str(r['stated']):<7} {cited:<12} {expected:<9} {cite:<5} {r['top_score']}")

    print()
    print(f"Answer accuracy:        {len(passed)}/{len(answerable)} correct  "
          f"({len(unsure)} UNSURE, {len(failed)} wrong or refused)")
    print(f"Citation accuracy:      {len(cite_ok)}/{len(passed)} of the correct answers cited an expected page")
    print(f"Correct-refusal rate:   {len(refused)}/{len(absent)} absent questions returned 'not stated'")
    print(f"Total tokens: {tokens_in} in / {tokens_out} out   Total cost: ${cost:.6f}   Model: {MODEL}")

    review = [r for r in rows if r["grade"] in ("UNSURE", "FAIL", "ERROR")]
    if review:
        print("\n===== needs review (UNSURE / FAIL / ERROR) =====")
        for r in review:
            print(f"\n[{r['id']}] {r['grade']}: {r['question']}")
            print(f"  expected: {r['expected_answer']!r}  pages {r['expected_pages']}")
            print(f"  detail:   {r['detail']}")
            if "raw_output" in r:
                print(f"  output:   {r['raw_output']!r}")
                print(f"  retrieved: {r['retrieved']}")

    summary = {
        "answerable": len(answerable), "correct": len(passed), "unsure": len(unsure),
        "wrong_or_refused": len(failed), "citation_ok": len(cite_ok),
        "absent": len(absent), "correctly_refused": len(refused),
        "input_tokens": tokens_in, "output_tokens": tokens_out, "cost_usd": round(cost, 6),
    }
    RESULTS_PATH.write_text(
        json.dumps({"run_at": datetime.now(timezone.utc).isoformat(), "model": MODEL,
                    "document_id": DOCUMENT_ID, "summary": summary, "results": rows},
                   indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\nSaved {RESULTS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

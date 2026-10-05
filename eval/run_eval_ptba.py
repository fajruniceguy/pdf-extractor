"""PTBA diagnostic eval on document 4 (ptba-quarterly-report.pdf, ingested column-aware).

    python eval/run_eval_ptba.py

Runs eval/questions_ptba.json through answer(document_id=4), grades each answer,
records whether the gold substring is in the top-5 retrieved chunks, and saves
raw results to eval/results_ptba.json. Anything ambiguous is UNSURE, never guessed.
Page numbers are PDF indices. Amounts are millions of Rupiah; dots are thousands separators.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from extractor.answer import MODEL, answer  # noqa: E402

DOCUMENT_ID = 4
QUESTIONS_PATH = ROOT / "eval" / "questions_ptba.json"
RESULTS_PATH = ROOT / "eval" / "results_ptba.json"

_CITATION = re.compile(r"\[[^\[\]]*?page\s+\d+\]", re.IGNORECASE)
# grouped amounts (567.618 / 567,618) or plain integers of 5+ digits; years and day numbers never match
_AMOUNT = re.compile(r"(?<![\d.,])(\d{1,3}(?:[.,]\d{3})+|\d{5,})(?!\d)")
_MONTHS_EN = "January|February|March|April|May|June|July|August|September|October|November|December"
_MONTHS_ID = "Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember"
_MONTH_YEAR = rf"(?:{_MONTHS_EN}|{_MONTHS_ID})\s+\d{{4}}"
_FULL_DATE = rf"(?:{_MONTHS_EN})\s+\d{{1,2}},?\s+\d{{4}}|\d{{1,2}}\s+(?:{_MONTHS_ID})\s+\d{{4}}"

# Narrative grading rules, fixed before the run.
#   ("facts", [regex, ...])        all present -> CORRECT, none -> WRONG, some -> UNSURE
#   ("pointer", required, other)   required present and no other match of `other` -> CORRECT;
#                                  both -> UNSURE; only other -> WRONG; neither -> UNSURE
#   ("notes", number)              same logic over note numbers ("Note 19", "Notes 19 and 20")
NARRATIVE_RULES: dict[str, tuple] = {
    "N1": ("facts", [r"government bonds?|obligasi pemerintah", r"corporate bonds?|obligasi korporat"]),
    "N2": ("notes", "19"),
    "N3": ("facts", [
        r"higher of|lebih tinggi",
        r"fair value less (?:the )?costs? (?:of disposal|to sell)|nilai wajar dikurangi biaya",
        r"value[- ]in[- ]use|nilai pakai",
    ]),
    "N4": ("pointer", r"(?:July|Juli)\s+2022", _MONTH_YEAR),
    "N5": ("pointer", r"(?:August|Agustus)\s+2022", _MONTH_YEAR),
    "N6": ("facts", [r"construction (?:costs?|expenses?)|biaya konstruksi", r"operational (?:costs?|expenses?)|biaya operasional"]),
    "N7": ("facts", [
        r"discount rate|tingkat diskonto", r"salary increase|kenaikan gaji", r"remuneration|remunerasi",
        r"attrition|pengurangan karyawan", r"life expectancy|harapan hidup",
        r"remaining periods? of service|periode sisa", r"medical cost trend|tren biaya kesehatan",
        r"average medical cost|biaya rata-rata kesehatan",
    ]),
    "N8": ("pointer", r"May\s+17,?\s+2018|17\s+Mei\s+2018", _FULL_DATE),
    "N9": ("pointer", r"October\s+7,?\s+2023|7\s+Oktober\s+2023", _FULL_DATE),
}


def squash(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def amounts(text: str) -> set[int]:
    return {int(re.sub(r"[.,]", "", t)) for t in _AMOUNT.findall(_CITATION.sub(" ", text))}


def _power_of_ten_apart(a: int, b: int) -> bool:
    lo, hi = sorted((a, b))
    if lo <= 0 or lo == hi or hi % lo:
        return False
    ratio = hi // lo
    return any(ratio == 10**k for k in range(1, 10))


def grade_table(q: dict, text: str) -> tuple[str, str]:
    expected = amounts(q["expected_answer"])
    row = amounts(q["gold_substring"])
    mates = row - expected
    got = amounts(text)
    if expected <= got:
        if got & mates:
            return "UNSURE", f"expected {sorted(expected)} and another number from the same table row {sorted(got & mates)}"
        if got - expected:
            return "UNSURE", f"expected {sorted(expected)} plus other amounts {sorted(got - expected)}"
        return "CORRECT", f"contains {sorted(expected)} and no other amount"
    if not got:
        return "UNSURE", "no amount in the answer"
    if any(_power_of_ten_apart(g, e) for g in got for e in expected):
        return "UNSURE", f"amount(s) {sorted(got)} differ from {sorted(expected)} by a power of ten (possible unit rewording)"
    return "WRONG", f"expected {sorted(expected)} not present; answer contains {sorted(got)}"


def grade_narrative(q: dict, text: str) -> tuple[str, str]:
    kind, *args = NARRATIVE_RULES[q["id"]]
    body = _CITATION.sub(" ", text)
    if kind == "facts":
        hits = [bool(re.search(p, body, re.IGNORECASE)) for p in args[0]]
        detail = f"{sum(hits)}/{len(hits)} expected facts found"
        if all(hits):
            return "CORRECT", detail
        if not any(hits):
            return "WRONG", detail
        return "UNSURE", detail + f"; missing {[p for p, h in zip(args[0], hits) if not h]}"
    if kind == "notes":
        numbers = []
        for m in re.finditer(r"(?:Notes?|Catatan)\s*(\d+(?:\s*(?:,|and|dan|&)\s*\d+)*)", body, re.IGNORECASE):
            numbers += re.findall(r"\d+", m.group(1))
        has = args[0] in numbers
        others = [f"Note {n}" for n in numbers if n != args[0]]
    else:
        required, other = args
        has = bool(re.search(required, body, re.IGNORECASE))
        others = [m.group(0) for m in re.finditer(other, body, re.IGNORECASE) if not re.fullmatch(required, m.group(0), re.IGNORECASE)]
    if has and not others:
        return "CORRECT", "expected value present, nothing conflicting"
    if has and others:
        return "UNSURE", f"expected value present together with {others}"
    if others:
        return "WRONG", f"expected value absent; answer states {others}"
    return "UNSURE", "neither the expected value nor a conflicting one"


def grade(q: dict, result) -> tuple[str, str]:
    if q["category"] == "absent":
        return ("PASS", "refused") if not result.stated else ("WRONG", "answered a question whose answer is absent")
    if not result.stated:
        return "REFUSED", "answerable question returned not stated"
    if q["category"] == "table":
        return grade_table(q, result.answer)
    return grade_narrative(q, result.answer)


def main() -> int:
    sys.stdout.reconfigure(errors="replace")
    questions = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    rows = []
    for q in questions:
        row = {k: q[k] for k in ("id", "category", "question", "expected_answer", "expected_pages", "gold_substring", "seen_before")}
        try:
            result = answer(q["question"], document_id=DOCUMENT_ID)
        except RuntimeError as e:
            row.update(result="ERROR", detail=str(e))
            rows.append(row)
            print(f"[{q['id']}] ERROR: {e}", file=sys.stderr)
            continue
        verdict, detail = grade(q, result)
        cited = sorted({page for _, page in result.citations})
        gold = squash(q["gold_substring"]) if q["gold_substring"] else None
        gold_ranks = [i for i, r in enumerate(result.retrieved, 1) if gold and gold in squash(r.content)]
        row.update(
            result=verdict, detail=detail, stated=result.stated, answer=result.answer, raw_output=result.raw_output,
            cited_pages=cited,
            citation_hit=bool(set(cited) & set(q["expected_pages"])) if q["expected_pages"] else None,
            retrieved=[{"rank": i, "chunk_id": r.chunk_id, "page": r.page_number, "score": round(r.similarity, 4)}
                       for i, r in enumerate(result.retrieved, 1)],
            retrieval_hit=bool(gold_ranks) if gold else None,
            gold_rank=gold_ranks[0] if gold_ranks else None,
            gold_hit_pages=sorted({result.retrieved[i - 1].page_number for i in gold_ranks}),
            warning=result.unreadable_pages_warning, note=result.note,
            input_tokens=result.input_tokens, output_tokens=result.output_tokens, cost_usd=result.cost_usd,
            stop_reason=result.stop_reason,
        )
        rows.append(row)

    print(f"{'id':<3} {'category':<9} {'result':<8} {'stated':<6} {'cited':<7} {'hit':<4} rank")
    for r in rows:
        if r["result"] == "ERROR":
            print(f"{r['id']:<3} {r['category']:<9} ERROR")
            continue
        hit = "-" if r["retrieval_hit"] is None else ("Y" if r["retrieval_hit"] else "N")
        rank = "-" if r["gold_rank"] is None else str(r["gold_rank"])
        print(f"{r['id']:<3} {r['category']:<9} {r['result']:<8} {str(r['stated']):<6} {','.join(map(str, r['cited_pages'])) or '-':<7} {hit:<4} {rank}")

    print()
    print("category   n  correct  unsure  refused  WRONG-AND-CONFIDENT  citation-correct  retrieval-hit")
    summary = {}
    for cat in ("narrative", "table", "absent"):
        grp = [r for r in rows if r["category"] == cat and r["result"] != "ERROR"]
        ok = [r for r in grp if r["result"] in ("CORRECT", "PASS")]
        wrong = [r for r in grp if r["result"] == "WRONG" and r["stated"]]
        cite = [r for r in ok if r.get("citation_hit")] if cat != "absent" else None
        hits = [r for r in grp if r.get("retrieval_hit")] if cat != "absent" else None
        s = dict(n=len(grp), correct=len(ok), unsure=sum(r["result"] == "UNSURE" for r in grp),
                 refused=sum(not r["stated"] for r in grp), wrong_and_confident=len(wrong),
                 citation_correct=None if cite is None else len(cite), retrieval_hit=None if hits is None else len(hits))
        summary[cat] = s
        print(f"{cat:<9} {s['n']:>2} {s['correct']:>8} {s['unsure']:>7} {s['refused']:>8} {s['wrong_and_confident']:>20} "
              f"{'-' if cite is None else f'{len(cite)}/{len(ok)}':>17} {'-' if hits is None else f'{len(hits)}/{len(grp)}':>14}")

    off_page = [r["id"] for r in rows if r.get("retrieval_hit") and not set(r["gold_hit_pages"]) & set(r["expected_pages"])]
    if off_page:
        print(f"\nretrieval hit came only from a page other than the expected one: {off_page}")

    review = [r for r in rows if r["result"] == "UNSURE" or (r["result"] == "WRONG" and r["stated"])]
    for r in review:
        label = "WRONG-AND-CONFIDENT" if r["result"] == "WRONG" else "UNSURE"
        print(f"\n===== {r['id']} {label}: {r['question']}")
        print(f"expected: {r['expected_answer']!r} pages {r['expected_pages']}; grader: {r['detail']}")
        print("answer (verbatim):")
        print(r["raw_output"])
        print("top-5: " + "; ".join(f"#{x['rank']} chunk {x['chunk_id']} p{x['page']} {x['score']:.3f}" for x in r["retrieved"]))

    tin = sum(r.get("input_tokens", 0) for r in rows)
    tout = sum(r.get("output_tokens", 0) for r in rows)
    cost = sum(r.get("cost_usd", 0.0) for r in rows)
    print(f"\nTotal: {len(rows)} questions, {tin} tokens in / {tout} out, cost ${cost:.6f}, model {MODEL}")

    RESULTS_PATH.write_text(
        json.dumps({"run_at": datetime.now(timezone.utc).isoformat(), "model": MODEL, "document_id": DOCUMENT_ID,
                    "summary": summary, "input_tokens": tin, "output_tokens": tout, "cost_usd": round(cost, 6),
                    "results": rows}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Saved {RESULTS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

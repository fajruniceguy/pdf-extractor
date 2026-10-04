# M4 findings: raw material

Generated 2026-10-04T13:15:31+07:00. Facts only. Sources are tagged: [DB] stored data queried at generation time, [results.json] eval/results.json, [live] retrieval re-run against the DB at generation time, [transcript] printed in the session but not stored in any file or table.

## 1. What was run

- Document 1: `Ethereum Yellow Paper_ a formal specification of Ethereum, a programmable blockchain.pdf`
  - pages: 42 [DB]
  - chunks: 253 [DB]
  - ingested at: 2026-10-03T22:21:19+00:00 [DB]
  - zero_chunk_pages: {} [DB]
  - embedding tokens: 62434 [transcript: printed by the ingest command; not stored in the DB or any file]
  - ingest cost: $0.001249 (tokens x $0.02 per 1M; price read from developers.openai.com/api/docs/models/text-embedding-3-small on 2026-10-04; not read from a bill)
  - M1 (ingest): run. M2 (retrieval): run (2 distinct questions: the intrinsic gas question, run unfiltered while only this document existed and later re-run with --doc 1; and the nonsense question). M3 (answer): not run. [transcript]
- Document 2: `AC_Research_Bitget_Token_BGB.pdf`
  - pages: 7 [DB]
  - chunks: 19 [DB]
  - ingested at: 2026-10-03T23:09:37+00:00 [DB]
  - zero_chunk_pages: {} [DB]
  - embedding tokens: 3597 [transcript: printed by the ingest command; not stored in the DB or any file]
  - ingest cost: $0.000072 (tokens x $0.02 per 1M; price read from developers.openai.com/api/docs/models/text-embedding-3-small on 2026-10-04; not read from a bill)
  - M1 (ingest): run. M2 (retrieval): run (3 questions, --doc 2). M3 (answer): not run. [transcript]
- Document 3: `POL Whitepaper v0.2.pdf`
  - pages: 25 [DB]
  - chunks: 77 [DB]
  - ingested at: 2026-10-03T23:27:30+00:00 [DB]
  - zero_chunk_pages: {} [DB]
  - embedding tokens: 11562 [transcript: printed by the ingest command; not stored in the DB or any file]
  - ingest cost: $0.000231 (tokens x $0.02 per 1M; price read from developers.openai.com/api/docs/models/text-embedding-3-small on 2026-10-04; not read from a bill)
  - M1 (ingest): run. M2 (retrieval): run (many questions, --doc 3; also the 15-question S1 eval). M3 (answer): run (--doc 3, plus one run without --doc; the same question re-run now without a filter [live] returned top-5 chunks from these files: POL Whitepaper v0.2.pdf). [transcript]
- Total embedding tokens across the three documents: 77593; total ingest cost: $0.001552
- Answer-layer model: claude-haiku-4-5-20251001; S1 eval spend: $0.022266 [results.json]

## 2. Extraction defects observed

Quotes are taken from stored chunk text. Whitespace is collapsed to single spaces. `chunk` is chunks.id. Counts use the definitions stated on each line.

- Document 1: `Ethereum Yellow Paper_ a formal specification of Ethereum, a programmable blockchain.pdf`
  - Column interleaving: chunk 75, page 9: `ionisthemostcomplexpart 6.2. Execution. Wedefineintrinsicgasg ,theamountof of the Ethereum protocol: it defines the state transition 0 gas this transaction requires to be paid prior to execu`
  - Column interleaving / run-together words: chunk 39, page 5: ` the maxi- The address hash T is slightly different: it is either a t mumnumberofWeitobepaidperunitofgas for 20-byt`
  - Run-together words: chunk 1, page 1: `nteractthroughamessage-passingframeworkwithothers. Wediscussitsdesign,implementationissues,theopport`
  - Run-together words, count: 140 of 253 chunks contain a token of 25 or more consecutive letters; longest token: `whichcandifferfromthesenderinthecaseofamessagecallorcontractcreationnotdirectlytriggeredbyatransactionbutcoming`
  - Unresolved glyph tokens `(cid:N)`: 152 of 253 chunks contain the string `(cid:`; example chunk 24, page 3: ` unmodified ‘input’ value be denoted by theplaceholder(cid:3)thenthemodifiedandutilisablevalueis 3. Conventions denoted as (cid:3)(cid:48), and intermediate val`
  - Mirrored text: not systematically searched in this document.
  - Mid-number chunk splits, definition: a chunk and its successor on the same page where the boundary falls between two digits (chunk size 800, overlap 150). Pairs checked: 211. Number cut at the end of a chunk: 4. Number cut at the start of a chunk: 4.
    - End-cut example: chunk 26, page 3, tail `rksactivatedatagivenblocknumber(e.g. 15,537,3`; successor chunk 27 continues `. 15,537,394forParis),thetrigger wa`
    - End-cut example: chunk 174, page 22, tail `2..63] (220) r = d[64..95] (221) s = d[96..12`; successor chunk 175 continues `= d[96..127]`
    - End-cut example: chunk 179, page 23, tail `297823662689037894645226208583 (248) q ≡ 2188`; successor chunk 180 continues `) q ≡ 21888242871839275222246405745`
    - Start-cut example: chunk 175, page 22, begins `07)I (cid:107)−1)] = I d d (21`; preceding chunk 174 had `0..((cid:107)I (cid:107)−`
    - Start-cut example: chunk 183, page 24, begins `320329863871079910040213922857`; preceding chunk 182 had `≡ (115597320329863871079`
    - Start-cut example: chunk 186, page 25, begins `4..95]) 1 p (267) y ≡ δ (x[96.`; preceding chunk 185 had `x ≡ δ (x[64..95]) 1 p (26`
  - Table-of-contents noise: no chunk contains the word `Contents` (0 found). The dotted-leader pattern appears in chunks [228, 229, 230] (pages [36, 37]), as a row of `. . . .` inside the opcode tables.
  - Chunks that begin mid-word: 116 of 211 pairs checked. Examples: chunk 2 page 1 begins `oughamessage-passingframeworkwithothers. Wediscuss`; chunk 3 page 1 begins `ssible outcomes consensus mechanisms, and voluntar`
- Document 2: `AC_Research_Bitget_Token_BGB.pdf`
  - Mirrored text: chunk 255, page 2: `AEDI GNITSEVNI | )BGB$( NEKOT TEGTIB AKADEMI CRYPTO RESEARCH BITGET TOKEN ($BGB) 09 FEB 2024 RESULTS NOTE HOLD | INVESTING IDEA BITGET TOKEN Narrative`
  - Column interleaving (figure caption inside a sentence): chunk 256, page 2: `membuat CEX lebih diminati daripada DEX (decentralized Source : Crypto Slate exchange). Selain alasan kenyamanan penggunaan, para trader dan investor cenderungan memilih CEX dibandingkan DEX`
  - Run-together words, count: 0 of 19 chunks contain a token of 25 or more consecutive letters.
  - Repeated page footer: 5 of 19 chunks contain `Refer to Important disclosure in the last page of this report`; pages [2, 3, 4, 5, 6]
  - Mid-number chunk splits, same definition as document 1: pairs checked: 12; number cut at end of a chunk: 0; at start of a chunk: 0.
  - Checked, not found: a chunk ending at `mencapai angka $3.`. A 300-character display truncation earlier in the session (SQL `left(content, 300)`) made chunk 259 (page 3) look like it ended there; the stored chunk is 705 characters long and ends with: `-2024 Refer to Important disclosure in the last page of this report 02`. No stored chunk of this document ends with `menebak`.
  - Table-of-contents noise: dotted-leader pattern found in 0 chunks.
  - Interleaving in the other documents and mirrored text in documents 1 and 3: not systematically searched.
  - Chunks that begin mid-word: 11 of 12 pairs checked. Examples: chunk 256 page 2 begins `ce yang dimiliki, serta berbagai fitur “all- in-on`; chunk 257 page 2 begins `si pada CEX native token yang mana memiliki berbag`
- Document 3: `POL Whitepaper v0.2.pdf`
  - Table-of-contents noise: chunk 276, page 2: `Contents 1. Polygon vision ………………………………………………………………………………… 3 2. Relevant work …………………………………………………………………………………. 4 2.1 Bitcoin (BTC) …………………………………………………………………………..…… 4 2.2 Etherum (ETH) …………………………………………`
  - Dotted-leader pattern (6 or more consecutive dots, or 3 or more ellipsis characters): chunks [276, 277], pages [2]
  - Run-together words, count: 0 of 77 chunks contain a token of 25 or more consecutive letters.
  - `(cid:` tokens: 0 chunks.
  - Mid-number chunk splits, same definition as document 1: pairs checked: 52; number cut at end of a chunk: 0; at start of a chunk: 0.
  - Column interleaving and mirrored text: not systematically searched in this document.
  - Chunks that begin mid-word: 28 of 52 pairs checked. Examples: chunk 274 page 1 begins `ropose design, utility and tokenomics of POL that`; chunk 275 page 1 begins `esigned to provide ongoing economic support for fu`

## 3. Retrieval behaviour: cases where the best chunk was not rank 1

All figures re-run live against the DB (k=5, filtered to one document). Definition of the best chunk: for document 3, a chunk whose text satisfies every grader fact for that question (the FACTS rules in eval/run_eval.py); for documents 1 and 2, the chunk containing the literal string stated on that line. `facts n/m` = grader facts found in that chunk.

- Q1 `What is the initial supply of POL?` expected pages [9]: r1 chunk 296 p9 0.662 facts 1/1; r2 chunk 298 p10 0.656 facts 0/1; r3 chunk 297 p9 0.613 facts 0/1; r4 chunk 304 p11 0.584 facts 0/1; r5 chunk 327 p18 0.576 facts 0/1
  - first rank with all facts in one chunk: 1; first rank on an expected page: 1
- Q2 `What are the two purposes POL is emitted for, and at what rate each?` expected pages [10]: r1 chunk 298 p10 0.608 facts 2/3; r2 chunk 300 p10 0.588 facts 1/3; r3 chunk 299 p10 0.534 facts 3/3; r4 chunk 304 p11 0.517 facts 0/3; r5 chunk 305 p12 0.500 facts 0/3
  - first rank with all facts in one chunk: 3; first rank on an expected page: 1
- Q3 `For how many years can the POL emission rate not be changed?` expected pages [10]: r1 chunk 299 p10 0.573 facts 2/2; r2 chunk 298 p10 0.544 facts 2/2; r3 chunk 304 p11 0.536 facts 2/2; r4 chunk 300 p10 0.533 facts 1/2; r5 chunk 305 p12 0.459 facts 0/2
  - first rank with all facts in one chunk: 1; first rank on an expected page: 1
- Q4 `In absolute terms, how much POL per year goes to the Community Treasury?` expected pages [17]: r1 chunk 323 p17 0.591 facts 1/1; r2 chunk 346 p24 0.579 facts 1/1; r3 chunk 324 p17 0.563 facts 0/1; r4 chunk 339 p21 0.540 facts 0/1; r5 chunk 299 p10 0.520 facts 0/1
  - first rank with all facts in one chunk: 1; first rank on an expected page: 1
- Q5 `What is the minimal satisfactory POL staking ratio?` expected pages [19]: r1 chunk 330 p19 0.664 facts 2/2; r2 chunk 345 p23 0.564 facts 1/2; r3 chunk 294 p8 0.552 facts 0/2; r4 chunk 298 p10 0.549 facts 0/2; r5 chunk 313 p14 0.545 facts 0/2
  - first rank with all facts in one chunk: 1; first rank on an expected page: 1
- Q6 `What is the minimal satisfactory Return on Work?` expected pages [19]: r1 chunk 331 p19 0.409 facts 2/2; r2 chunk 345 p23 0.398 facts 2/2; r3 chunk 330 p19 0.384 facts 2/2; r4 chunk 342 p22 0.353 facts 0/2; r5 chunk 346 p24 0.331 facts 0/2
  - first rank with all facts in one chunk: 1; first rank on an expected page: 1
- Q7 `What average POL price is used as a model input?` expected pages [21]: r1 chunk 339 p21 0.602 facts 0/1; r2 chunk 337 p21 0.572 facts 1/1; r3 chunk 338 p21 0.530 facts 0/1; r4 chunk 343 p23 0.523 facts 0/1; r5 chunk 330 p19 0.510 facts 0/1
  - first rank with all facts in one chunk: 2; first rank on an expected page: 1
- Q8 `What is the average yearly running cost per validator?` expected pages [21]: r1 chunk 341 p22 0.598 facts 0/1; r2 chunk 338 p21 0.523 facts 1/1; r3 chunk 342 p22 0.512 facts 0/1; r4 chunk 343 p23 0.490 facts 0/1; r5 chunk 337 p21 0.445 facts 0/1
  - first rank with all facts in one chunk: 2; first rank on an expected page: 2
- Q9 `What are the four phases of the validator lifecycle?` expected pages [15, 16]: r1 chunk 318 p15 0.674 facts 3/4; r2 chunk 320 p16 0.561 facts 3/4; r3 chunk 319 p15 0.495 facts 2/4; r4 chunk 322 p16 0.473 facts 1/4; r5 chunk 295 p9 0.469 facts 0/4
  - first rank with all facts in one chunk: none within top 5; first rank on an expected page: 1
- Q10 `Why is AAVE relevant to POL's design?` expected pages [7]: r1 chunk 290 p7 0.542 facts 3/3; r2 chunk 289 p7 0.395 facts 1/3; r3 chunk 326 p17 0.365 facts 1/3; r4 chunk 273 p1 0.361 facts 0/3; r5 chunk 279 p3 0.353 facts 0/3
  - first rank with all facts in one chunk: 1; first rank on an expected page: 1
- Summary for document 3: Q2 (all-facts chunk rank 3, expected-page rank 1), Q7 (all-facts chunk rank 2, expected-page rank 1), Q8 (all-facts chunk rank 2, expected-page rank 2), Q9 (all-facts chunk rank none, expected-page rank 1) did not have both at rank 1.
- Document 2, `What is the current valuation and circulating supply of Bitget Token?` (answer strings `$900M` and `1.4B`): r1 chunk 259 p3 0.608 contains neither; r2 chunk 255 p2 0.588 contains ['$900M', '1.4B']; r3 chunk 258 p3 0.558 contains neither; r4 chunk 260 p4 0.533 contains neither; r5 chunk 270 p6 0.516 contains neither
- Document 1, `What is the intrinsic gas of a transaction?` (string `Wedefineintrinsicgas` or `We define intrinsic gas`): r1 chunk 76 p9 0.687 contains the definition sentence: True; r2 chunk 40 p5 0.566 contains the definition sentence: False; r3 chunk 75 p9 0.558 contains the definition sentence: True; r4 chunk 77 p9 0.545 contains the definition sentence: False; r5 chunk 83 p10 0.542 contains the definition sentence: False

## 4. Score ranges measured

Similarity = 1 - cosine distance. `top` = rank 1, `5th` = rank 5. Live re-runs use the exact query strings used earlier in the session.

- Document 1 (Yellow Paper) [live]
  - in-document: `What is the intrinsic gas of a transaction?`: top 0.687, 5th 0.542; scores 0.687, 0.566, 0.558, 0.545, 0.542; pages [9, 5, 9, 9, 10]
  - related-but-absent: not measured for this document.
  - nonsense: `what is the airspeed velocity of a swallow`: top 0.142, 5th 0.127; scores 0.142, 0.132, 0.132, 0.129, 0.127; pages [35, 32, 15, 39, 5]
- Document 2 (Bitget) [live]
  - in-document (English): `What is the current valuation and circulating supply of Bitget Token?`: top 0.608, 5th 0.516; scores 0.608, 0.588, 0.558, 0.533, 0.516; pages [3, 2, 3, 4, 6]
  - in-document (Indonesian): `Berapa valuasi saat ini dan circulating supply Bitget Token?`: top 0.653, 5th 0.582; scores 0.653, 0.613, 0.603, 0.583, 0.582; pages [3, 2, 3, 4, 6]
  - related-but-absent: not measured for this document.
  - nonsense: `what is the airspeed velocity of a swallow`: top 0.083, 5th 0.071; scores 0.083, 0.078, 0.077, 0.076, 0.071; pages [7, 6, 3, 4, 5]
- Document 3 (POL Whitepaper)
  - in-document, S1 questions Q1-Q10 [results.json]:
    - Q1 `What is the initial supply of POL?`: top 0.662, 5th 0.576; scores 0.662, 0.656, 0.613, 0.584, 0.576
    - Q2 `What are the two purposes POL is emitted for, and at what rate each?`: top 0.608, 5th 0.500; scores 0.608, 0.588, 0.534, 0.517, 0.500
    - Q3 `For how many years can the POL emission rate not be changed?`: top 0.573, 5th 0.459; scores 0.573, 0.544, 0.536, 0.533, 0.459
    - Q4 `In absolute terms, how much POL per year goes to the Community Treasury?`: top 0.591, 5th 0.520; scores 0.591, 0.579, 0.563, 0.540, 0.520
    - Q5 `What is the minimal satisfactory POL staking ratio?`: top 0.664, 5th 0.545; scores 0.664, 0.564, 0.552, 0.549, 0.545
    - Q6 `What is the minimal satisfactory Return on Work?`: top 0.409, 5th 0.331; scores 0.409, 0.398, 0.384, 0.353, 0.331
    - Q7 `What average POL price is used as a model input?`: top 0.602, 5th 0.510; scores 0.602, 0.573, 0.530, 0.523, 0.510
    - Q8 `What is the average yearly running cost per validator?`: top 0.598, 5th 0.445; scores 0.598, 0.523, 0.512, 0.490, 0.445
    - Q9 `What are the four phases of the validator lifecycle?`: top 0.674, 5th 0.469; scores 0.674, 0.561, 0.495, 0.473, 0.469
    - Q10 `Why is AAVE relevant to POL's design?`: top 0.542, 5th 0.353; scores 0.542, 0.395, 0.365, 0.361, 0.353
  - absent, S1 questions Q11-Q15 [results.json]:
    - Q11 `What is the current market price of POL in US dollars?`: top 0.451, 5th 0.420; scores 0.451, 0.446, 0.445, 0.423, 0.420
    - Q12 `How long is the waiting period before a retired validator can withdraw their stake?`: top 0.523, 5th 0.381; scores 0.523, 0.446, 0.400, 0.389, 0.381
    - Q13 `What block time do Polygon chains use?`: top 0.655, 5th 0.531; scores 0.655, 0.569, 0.546, 0.535, 0.531
    - Q14 `What percentage of transaction fees do Polygon chains pass to validators?`: top 0.672, 5th 0.608; scores 0.672, 0.662, 0.650, 0.618, 0.608
    - Q15 `How much POL does the Polygon Foundation hold?`: top 0.667, 5th 0.616; scores 0.667, 0.653, 0.640, 0.625, 0.616
  - nonsense [live]:
    - `what is the airspeed velocity of a swallow`: top 0.144, 5th 0.079; scores 0.144, 0.106, 0.098, 0.092, 0.079; pages [24, 10, 23, 20, 20]
    - `What is the airspeed velocity of a swallow?`: top 0.114, 5th 0.082; scores 0.114, 0.113, 0.084, 0.083, 0.082; pages [10, 24, 23, 20, 21]
  - Document 3 top-score ranges [results.json]: answerable min 0.409, max 0.674; absent min 0.451, max 0.672

## 5. S1 result

- Answer accuracy: 10/10 correct; 0 UNSURE; 0 wrong or refused [results.json]
- Citation accuracy: 10/10 of the correct answers cited an expected page [results.json]
- Correct-refusal rate: 5/5 absent questions returned `not stated` [results.json]
- Tokens: 17791 in / 895 out; cost $0.022266; model claude-haiku-4-5-20251001; document_id 3; run_at 2026-10-04T03:16:57.463785+00:00 [results.json]
- Conditions:
  - one run; results.json holds a single execution
  - one document (document 3)
  - two of the 15 questions were run during prompt tuning before the eval: Q1 `What is the initial supply of POL?` and Q11 `What is the current market price of POL in US dollars?` [transcript]
  - no temperature control: the installed anthropic SDK (1.11.0) `messages.create` has no `temperature` parameter [transcript: signature listing]
  - answers graded automatically by the FACTS rules in eval/run_eval.py; the assistant read all 15 outputs in the session [transcript]
  - citation hit = at least one cited page is in expected_pages; in 10 of 10 correct answers the cited pages equalled the expected pages [results.json]
  - Stored text near the topics of the absent questions [DB]:
    - Q12 (waiting period): chunk 320, page 16: `t any point. Once the retirement is initiated, a predefined waiting period commences, allowing for potential pending slashing. After the waiting period, validators are able to withdraw their POL stake from the deposit contract. In return for validati`
    - Q13 (block time): chunk 315, page 14: `Block time and size: It is possible to configure the frequency and size, i.e. gas limit of blocks. ● Checkpoint time: Validator sets provide fast, local finality for Polygon chains. In addition to thi`
    - Q14 (fees): chunk 321, page 16: `Transaction fees: Validators are allowed to validate any number of Polygon chains. In return, these chains will normally award the entirety or a portion of transaction fees to validators. 3. Additional rewards: As mentioned above, some Polygon chains can choose to introduce additional rewards to attract more validators. These re`
    - Q15 (foundation): chunk 323, page 17: `pport for as long as required; ● Increased decentralization by reducing dependency on the Polygon Foundation; ● Achieving the next level of transparency and community inclusion. As described in § 5.2, the Commu`

## 6. S1 retrieval finding

- Q6 (answerable, correct, expected page 19) top score: 0.409 [results.json]
- Q13 (absent, refused) top score: 0.655 [results.json]
- Q14 (absent, refused) top score: 0.672 [results.json]
- Q15 (absent, refused) top score: 0.667 [results.json]
- All top scores [results.json]: Q1 0.662 (answerable, grade PASS); Q2 0.608 (answerable, grade PASS); Q3 0.573 (answerable, grade PASS); Q4 0.591 (answerable, grade PASS); Q5 0.664 (answerable, grade PASS); Q6 0.409 (answerable, grade PASS); Q7 0.602 (answerable, grade PASS); Q8 0.598 (answerable, grade PASS); Q9 0.674 (answerable, grade PASS); Q10 0.542 (answerable, grade PASS); Q11 0.451 (absent, grade PASS); Q12 0.523 (absent, grade PASS); Q13 0.655 (absent, grade PASS); Q14 0.672 (absent, grade PASS); Q15 0.667 (absent, grade PASS)

## 7. Query plan

- Recorded when the chunks table held 253 rows (document 1 only), unfiltered search query [transcript: EXPLAIN output printed in the session; not stored in any file]:
  - default planner settings: Limit (cost=42.66..42.68 rows=5) -> Sort (cost=42.66..43.30 rows=253) -> Nested Loop (cost=0.16..38.46 rows=253) -> Seq Scan on chunks c (cost=0.00..29.53 rows=253); Memoize on documents via documents_pkey
  - SET enable_seqscan = off (session only): Limit (cost=1018.06..1020.42 rows=5) -> Nested Loop (cost=1018.06..1137.36 rows=253) -> Index Scan using chunks_embedding_hnsw_idx on chunks c (cost=1017.90..1128.43 rows=253), Order By: (embedding <=> vector)
- Re-run live now, chunks table holds 349 rows, same unfiltered query [live]:
  - default planner settings:
    - `Limit  (cost=58.83..58.84 rows=5 width=813)`
    - `  ->  Sort  (cost=58.83..59.70 rows=349 width=813)`
    - `        Sort Key: ((c.embedding <=> '[<1536 floats>]'::vector))`
    - `        ->  Nested Loop  (cost=0.16..53.03 rows=349 width=813)`
    - `              ->  Seq Scan on chunks c  (cost=0.00..40.49 rows=349 width=787)`
    - `              ->  Memoize  (cost=0.16..0.32 rows=1 width=36)`
    - `                    Cache Key: c.document_id`
    - `                    Cache Mode: logical`
    - `                    ->  Index Scan using documents_pkey on documents d  (cost=0.15..0.31 rows=1 width=36)`
    - `                          Index Cond: (id = c.document_id)`
  - SET enable_seqscan = off (session only):
    - `Limit  (cost=1402.78..1405.13 rows=5 width=813)`
    - `  ->  Nested Loop  (cost=1402.78..1566.65 rows=349 width=813)`
    - `        ->  Index Scan using chunks_embedding_hnsw_idx on chunks c  (cost=1402.62..1554.11 rows=349 width=787)`
    - `              Order By: (embedding <=> '[<1536 floats>]'::vector)`
    - `        ->  Memoize  (cost=0.16..0.32 rows=1 width=36)`
    - `              Cache Key: c.document_id`
    - `              Cache Mode: logical`
    - `              ->  Index Scan using documents_pkey on documents d  (cost=0.15..0.31 rows=1 width=36)`
    - `                    Index Cond: (id = c.document_id)`

## 8. What was never tested

- Answer layer (M3) against document 1 or document 2.
- Related-but-absent score range for documents 1 and 2.
- Any labeled eval on documents 1 or 2; the S1 set covers document 3 only.
- More than one S1 run; run-to-run variation of answers (no temperature control is available in the installed SDK).
- S1 questions that are multi-step, involve negation, or depend on table contents; all 10 answerable questions ask for an explicit value or list.
- Retrieval of facts that appear only inside tables (tables are extracted but not chunked).
- A question whose matching chunks come from more than one document (the one run without --doc retrieved only document 3 chunks).
- The `note` field path (text after `not stated`) in a live run; it was not triggered.
- The refusal warning for unreadable pages on a real scanned PDF; it was tested only on a synthetic PDF in a throwaway database. No stored document has zero-chunk pages.
- OCR or any handling of image-only pages beyond reporting them.
- EXPLAIN of the document-filtered query (WHERE document_id = ...).
- Planner behaviour at table sizes other than 253 and the current row count; whether and when the planner chooses the HNSW index without being forced.
- Any document longer than 42 pages; the largest ingested is document 1.
- Embedding cost against the OpenAI usage dashboard; costs above are computed from printed token counts.
- Python 3.11 (the version named in Claude.md); all runs used Python 3.10.11.
- Concurrent ingest of the same file; the unique-index path was exercised only with a simulated pre-check miss in a throwaway database.
- Automated tests (S3); none exist in the repo.
- Two-signal confidence and needs_review (S2); not implemented.
- A systematic search for mirrored or interleaved text in documents 1 and 3.

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

## 9. Supplementary diagnostic: PTBA interim report (not ingested)

Run in session with the project's own `_extract_text_blocks`, `_extract_tables` and `chunk_document`, sliced to selected pages in a throwaway script. No ingest, no embedding, no database write. Figures were recomputed from the PDF when this section was written.

- Document: `ptba-quarterly-report.pdf`; the page text identifies it as PT Bukit Asam (Persero) Tbk interim consolidated financial statements for the three months ended March 31, 2026
- Pages: 152; pages with zero extracted text lines: [2]
- Not in the database; no rows exist for it
- Pages examined in detail: 63, 73 (the notes: page 63 is Note 3, judgments and estimates; page 73 is Note 9, investments, with a summarised profit-or-loss block)
- Extracted lines and chunks per page
  - Page 63: 67 text lines, 5409 characters, 9 chunks (first chunk 800 characters; the first 11 lines, 664 characters, are a header block repeated on notes pages)
  - Page 73: 63 text lines, 4133 characters, 7 chunks (first chunk 800 characters; the first 11 lines, 664 characters, are a header block repeated on notes pages)
- Interleaving ratios (a line counts as `both` when it contains at least one Indonesian and at least one English function word)
  - Indonesian function words used: adalah, akan, atas, dalam, dan, dari, dengan, ini, kepada, oleh, pada, telah, tidak, untuk, yang
  - English function words used: and, are, as, be, by, for, from, have, in, is, of, on, that, the, to, which, will, with
  - Page 63: 42 of 67 lines are `both`; Indonesian only 7; English only 9; neither 9
  - Page 73: 32 of 63 lines are `both`; Indonesian only 7; English only 8; neither 16
- Structure of a line: each extracted line holds the left-column (Indonesian) fragment followed by the right-column (English) fragment, e.g. `Pendapatan 567.618 554.473 Revenue` and `Penghasilan komprehensif lain 368.751 - Other comprehensive income`
- Run-together words: tokens of 25 or more consecutive letters, page 63: 0; page 73: 0; `(cid:` occurrences, page 63: 0; page 73: 0
- One merged word seen in the raw lines of page 9 (not part of the chunked pages): `Catatan atas laporan keuangan konsolidasian interiterlampir merupakan `
- Tables detected by the extractor: 0 across 15 candidate pages (pages 9, 12, 18, 19, 25, 33, 39, 55, 63, 73, 99, 106, 125, 139, 142); per page: 9: 0, 12: 0, 18: 0, 19: 0, 25: 0, 33: 0, 39: 0, 55: 0, 63: 0, 73: 0, 99: 0, 106: 0, 125: 0, 139: 0, 142: 0
- State of table-like content in the chunk text
  - Page 73: the summarised profit-or-loss block appears as plain text lines, one row per line, laid out as Indonesian label, current-period value, prior-period value, English label
  - Page 73: the row `Beban umum dan administrasi (21.708) (26.037) General and adm` ends chunk 2 of 7 and is completed in chunk 3 of 7; the label `Jumlah laba komprehensif ... periode berjalan 714.992 183.979 ... for the period` wraps over two lines with the values on the second
  - Page 9 (statement of changes in equity, raw lines only): `Saldo pada tanggal 1 Januari 2025 1.152.066 642.832 (12.521) 3.701 1.120.325 13.730.400 5.868.485 22.505.288 138.524 22.643.812 Balance as of January 1, 2025`; the multi-line column headers above it are on separate lines, mixed across both languages
- Number formatting (counts over the extracted lines of the listed pages)
  - Dot-grouped thousands (e.g. 567.618): page 73 21, page 9 66; comma-grouped thousands: page 73 0, page 9 0
  - Parenthesised negatives (e.g. (516.544)): page 73 10, page 9 12; standalone `-` tokens: page 73 1, page 9 72
- Page offset between the PDF page index and the printed page number (last extracted line of the page)
  - PDF page 9 prints 6; PDF page 63 prints 60; PDF page 73 prints 70
- Full chunk dump of pages 63 and 73 was produced in session and saved to the session scratchpad as `ptba_chunks_63_73.txt`; it is not part of the repo

## 10. Confident wrong answer: HBAP revenue (document 4)

Sources: [DB] stored data queried when this section was written; [live] retrieval re-run against the DB when this section was written; [transcript] the Q4 run of `python cli.py answer ... --doc 4`, printed in the session and not stored in any file. Document 4 is `ptba-quarterly-report.pdf`, ingested with `--column-aware`.

### 1. The run [transcript]

- Question: `What was HBAP's revenue in March 2026?`
- Answer returned: `HBAP's revenue in March 2026 was 203.513 (in thousands, based on the document's formatting) [ptba-quarterly-report.pdf, page 72].`
- Citation given: `ptba-quarterly-report.pdf, page 72`
- Stated flag: `True`
- Model `claude-haiku-4-5-20251001`; stop_reason `end_turn`; 1594 tokens in / 46 out; one run, no temperature control
- Retrieved (page, score) as printed: p72 (0.576), p72 (0.575), p71 (0.529), p73 (0.528), p70 (0.512)

### 2. Stored text of chunks 751, 752, 756 and 758 [DB]

- Chunk 751, page 72, 800 characters, verbatim:

````text
rwise stated)
9. INVESTASI (lanjutan) 9. INVESTMENTS (continued)
a. Investasi pada ventura bersama (lanjutan) a. Investments in joint ventures (continued)
Berikut ini merupakan ringkasan informasi Below is the summarised financial
keuangan dari BPI, ventura bersama information for BPI, a significant joint venture
yang signifikan bagi Grup pada tanggal for the Group as of March 31, 2026 and
31 Maret 2026 dan 2025: (lanjutan) 2025: (continued)
Ringkasan laporan laba rugi dan Summarised statements of profit or loss and
dan penghasilan komprehensif lain other comprehensive income
31 Maret 2026/ 31 Maret 2025/
March 31, 2026 March 31, 2025
Pendapatan 203.513 240.534 Revenue
Beban pokok pendapatan (126.922) (152.708) Cost of revenue
Beban umum dan administrasi (29.459) (27.202) General and admin
````

- Chunk 752, page 72, 800 characters, verbatim:

````text
tan 203.513 240.534 Revenue
Beban pokok pendapatan (126.922) (152.708) Cost of revenue
Beban umum dan administrasi (29.459) (27.202) General and administrative expenses
Beban keuangan, neto (3.740) (295) Finance expenses, net
Beban lainnya, neto (22.929) (8.364) Other expenses, net
Laba sebelum pajak penghasilan 20.463 51.965 Profit before income tax
Beban pajak penghasilan - (35.187) Income tax expenses
Laba periode berjalan 20.463 16.778 Profit for the period
Penghasilan komprehensif lain - - Other comprehensive income
Jumlah penghasilan komprehensif Total comprehensive income
periode berjalan 20.463 16.778 for the period
Berikut ini merupakan ringkasan informasi Below is the summarised financial information
keuangan dari HBAP, ventura bersama for HBAP, a significant joint venture for th
````

- Chunk 756, page 73, 800 characters, verbatim:

````text
rwise stated)
9. INVESTASI (lanjutan) 9. INVESTMENTS (continued)
a. Investasi pada ventura bersama (lanjutan) a. Investments in joint ventures (continued)
Berikut ini merupakan ringkasan informasi Below is the summarised financial information
keuangan dari HBAP, ventura bersama for HBAP, a significant joint venture for the
yang signifikan bagi Grup pada tanggal Group as of March 31, 2026 and 2025:
31 Maret 2026 dan 2025: (lanjutan) (continued)
Ringkasan laporan laba rugi dan Summarised statements of profit or loss and
dan penghasilan komprehensif lain other comprehensive income
31 Maret 2026/ 31 Maret 2025/
March 31, 2026 March 31, 2025
Pendapatan 567.618 554.473 Revenue
Beban pokok pendapatan (516.544) (526.190) Cost of revenue
Beban umum dan administrasi (21.708) (26.037) General and adm
````

- Chunk 758, page 73, 800 characters, verbatim:

````text
ncome
periode berjalan 714.992 183.979 for the period
Perusahaan telah menjaminkan seluruh saham The Company has pledged all of its existing
yang dimilikinya di entitas HBAP baik yang share ownership in HBAP at the signing of the
dimiliki pada saat penandatanganan Akta Gadai Deed of Shares Pledge and any future shares
Saham atau saham tambahan dimasa yang to the China Export-Import Bank as collateral
akan datang kepada China Export-Import Bank for the loan obtained for the HBAP project. The
dalam rangka pemberian pinjaman untuk guarantee was approved by the Minister of
pendanaan proyek HBAP. Penjaminan tersebut State-Owned Enterprise (“SOE”) on May 17,
telah mendapat persetujuan dari Menteri BUMN 2018.
pada tanggal 17 Mei 2018.
Pada tahun 2021, PLN telah mengajukan surat In 2021, PLN submi
````

### 3. The 5 retrieved chunks for this question [live]

- Re-run of the same retrieval (document 4, k=5); its (page, score) list equals the Q4 run's: True
- Rank 1: chunk 753, page 72, score 0.576
- Rank 2: chunk 752, page 72, score 0.575
- Rank 3: chunk 748, page 71, score 0.529
- Rank 4: chunk 758, page 73, score 0.528
- Rank 5: chunk 744, page 70, score 0.512

### 4. Chunks holding HBAP's revenue row [DB, live]

- Chunk 756, page 73: contains the full row `Pendapatan 567.618 554.473 Revenue`; rank 6 of 805 chunks of document 4, score 0.500; not retrieved (outside the top 5)
- Chunk 757, page 73: contains only the overlap tail of the row `patan 567.618 554.473 Revenue`; rank 57 of 805 chunks of document 4, score 0.431; not retrieved (outside the top 5)
- Chunks of document 4 containing the string `567.618`: [756, 757]
- Is any chunk containing `567.618` among the 5 retrieved: False

### 5. The heading `Berikut ini merupakan ringkasan informasi ... keuangan dari HBAP` against chunk boundaries [DB]

The heading is interleaved with its English column, so it occupies two lines in the stored text: `Berikut ini merupakan ringkasan informasi Below is the summarised financial information` followed by `keuangan dari <entity>, ventura bersama for <entity>, a significant joint venture for th...`.

- Chunk 751, page 72 (800 chars): entity `BPI`; heading line 1 starts at offset 155; the entity name ends at offset 248 of 800
- Chunk 752, page 72 (800 chars): entity `HBAP`; heading line 1 starts at offset 632; the entity name ends at offset 738 of 800
- Chunk 753, page 72 (800 chars): entity `HBAP`; heading line 1 is cut at the chunk start (chunk begins 'kan ringkasan informasi Below is the sum'); the entity name ends at offset 88 of 800
- Chunk 756, page 73 (800 chars): entity `HBAP`; heading line 1 starts at offset 155; the entity name ends at offset 261 of 800
- Page-72 HBAP heading: it starts at offset 632 of chunk 752 and runs to the end of that chunk (offset 800); line 2 of the heading is cut at `nture for th`
- Chunk 753 begins inside the same heading: its offset 0 falls inside the word `merupakan` (chunk 753 starts with `kan ringkasan informasi `)
- The line immediately before that heading in chunk 752 is the last row of BPI's table: `periode berjalan 20.463 16.778 for the period`
- Chunk 752 ends with: `formation keuangan dari HBAP, ventura bersama for HBAP, a significant joint venture for th`
- Chunk 753 begins with: `kan ringkasan informasi Below is the summarised financial information keuangan dari HBAP,`
- Chunk 752 contains `Berikut ini merupakan ringkasan informasi` at offset 632; chunk 753 contains it: False
- Page-73 occurrence for comparison: see the entry for chunk 756 above

### 6. Where `BPI` appears [DB]

- Chunks of document 4 containing the word `BPI`: 19; pages [59, 70, 71, 72, 119, 131, 133, 136, 142]
  - Chunk 682, page 59: 1 occurrence(s)
  - Chunk 685, page 59: 1 occurrence(s)
  - Chunk 742, page 70: 2 occurrence(s)
  - Chunk 743, page 70: 4 occurrence(s)
  - Chunk 744, page 70: 1 occurrence(s)
  - Chunk 746, page 71: 1 occurrence(s)
  - Chunk 747, page 71: 2 occurrence(s)
  - Chunk 748, page 71: 2 occurrence(s)
  - Chunk 751, page 72: 2 occurrence(s)
  - Chunk 977, page 119: 1 occurrence(s)
  - Chunk 1047, page 131: 1 occurrence(s)
  - Chunk 1055, page 133: 2 occurrence(s)
  - Chunk 1056, page 133: 2 occurrence(s)
  - Chunk 1065, page 136: 2 occurrence(s)
  - Chunk 1066, page 136: 2 occurrence(s)
  - Chunk 1098, page 142: 1 occurrence(s)
  - Chunk 1099, page 142: 1 occurrence(s)
  - Chunk 1101, page 142: 1 occurrence(s)
  - Chunk 1102, page 142: 1 occurrence(s)
- On page 72, `BPI` appears only in chunk(s): [751]
- Chunk 752 (holds `Pendapatan 203.513 240.534 Revenue`) contains `BPI`: False; chunk 751 contains `BPI`: True
- Retrieved chunks containing `BPI`: [748, 744]

### 7. Units stated in the document [DB]

- Chunks of document 4 containing `Millions of Rupiah` or `Jutaan Rupiah`: 233 of 805
- Page 72 chunks: [750, 751, 752, 753, 754]; of these, the ones containing the units statement: [750]
- Chunk 750 contains these two lines verbatim (Indonesian left, English right; the statement is split across the two lines by the bilingual layout):

````text
(Disajikan dalam Jutaan Rupiah, (Expressed in Millions of Rupiah,
kecuali dinyatakan lain) unless otherwise stated)
````

- Chunk 751 starts with `rwise stated)` (the tail of that statement); it does not contain the full statement: True
- Chunk 752 contains a units statement: False
- Retrieved chunks containing `Millions of Rupiah` or `Jutaan Rupiah`: []
- Chunks of document 4 containing `thousand`, `ribuan` or `ribu`: 0
- The phrase `in thousands` appears in the stored text of document 4: False

### 8. Page 72 extraction mode [DB, live]

- Detector on page 72: two_columns=True; two columns, gutter 7.2pt; words left/right of the gutter 220/230
- Dot-grouped amounts left/right of the gutter: 19/19 (veto needs at least 5 on each side)
- Decision with the flag on: vetoed, default extraction used
- Stored chunks of page 72 (5) identical to chunks built from the default extraction of page 72: True

## 11. PTBA diagnostic eval (document 4, 17 questions)

Sources: [results_ptba.json] `eval/results_ptba.json`; [DB] stored chunks of document 4 read when this section was written; [results.json, results_run1-3.json] the POL eval files; [transcript] printed in the session, not stored in any file. Page numbers are PDF indices.

### 1. Setup and conditions

- Questions: 17 (9 narrative, 5 table, 3 absent) in `eval/questions_ptba.json`; the list was supplied by the user, and the user verified the absent questions against the PDF [transcript]
- seen_before (run before the eval): ['N7', 'N8', 'T1', 'A1']
- Gold substrings found in a stored chunk on the expected page: 14 of 14 [DB]
- Grading: automatic; narrative rules (keyword and date checks) written before the run; one rule (N2) corrected before the run after an offline test on synthetic answers; no rule, question or prompt changed after results [transcript]
- One run; run_at 2026-10-05T04:45:35.964974+00:00; model claude-haiku-4-5-20251001; no temperature control (the installed SDK exposes none); 25957 tokens in / 631 out; cost $0.029112 [results_ptba.json]

### 2. Per-category split [results_ptba.json]

- Columns: n / correct / unsure / refused (stated False) / WRONG-AND-CONFIDENT (stated True, incorrect) / citation-correct (of the correct answers) / retrieval-hit
  - narrative: 9 / 6 / 0 / 3 / 0 / 6/6 / 7/9
  - table: 5 / 0 / 0 / 2 / 3 / 0/0 / 1/5
  - absent: 3 / 3 / 0 / 3 / 0 / - / -
- Answerable questions (14): correct ['N1', 'N4', 'N5', 'N6', 'N7', 'N8']; refused ['N2', 'N3', 'N9', 'T4', 'T5']; WRONG-AND-CONFIDENT ['T1', 'T2', 'T3']; UNSURE []
- Absent questions: passed (stated False) ['A1', 'A3', 'A4']
- Questions seen before the eval (4): correct or passed ['N7', 'N8', 'A1']; refused []; WRONG-AND-CONFIDENT ['T1']
- Questions not seen before the eval (13): correct or passed ['N1', 'N4', 'N5', 'N6', 'A3', 'A4']; refused ['N2', 'N3', 'N9', 'T4', 'T5']; WRONG-AND-CONFIDENT ['T2', 'T3']
- Per question: N1 CORRECT stated True cited [49, 63]; N2 REFUSED stated False cited -; N3 REFUSED stated False cited -; N4 CORRECT stated True cited [73]; N5 CORRECT stated True cited [73]; N6 CORRECT stated True cited [73]; N7 CORRECT stated True cited [63]; N8 CORRECT stated True cited [73]; N9 REFUSED stated False cited -; T1 WRONG stated True cited [72]; T2 WRONG stated True cited [72]; T3 WRONG stated True cited [72]; T4 REFUSED stated False cited -; T5 REFUSED stated False cited -; A1 PASS stated False cited -; A3 PASS stated False cited -; A4 PASS stated False cited -

### 3. T3: gold row in the context, answer from another entity's chunk [results_ptba.json, DB]

- Question: `What was HBAP's total comprehensive income for the period ended March 31, 2026?`; expected `714.992` on page [73]; gold substring `714.992 183.979`
- Answer returned: `According to the context, HBAP's total comprehensive income for the period ended March 31, 2026 was 20.463 million Rupiah. [ptba-quarterly-report.pdf, page 72]`; stated True; cited pages [72]; grader: expected [714992] not present; answer contains [20463]
- Top 5: #1 chunk 752 p72 0.614; #2 chunk 753 p72 0.601; #3 chunk 744 p70 0.585; #4 chunk 758 p73 0.555; #5 chunk 838 p90 0.554
  - Rank 1, chunk 752, page 72: contains `714.992` False; contains `20.463` True; contains `HBAP` True; contains `BPI` False
  - Rank 2, chunk 753, page 72: contains `714.992` False; contains `20.463` False; contains `HBAP` True; contains `BPI` False
  - Rank 3, chunk 744, page 70: contains `714.992` False; contains `20.463` False; contains `HBAP` True; contains `BPI` True
  - Rank 4, chunk 758, page 73: contains `714.992` True; contains `20.463` False; contains `HBAP` True; contains `BPI` False
  - Rank 5, chunk 838, page 90: contains `714.992` False; contains `20.463` False; contains `HBAP` False; contains `BPI` False
- retrieval_hit True, gold rank 4; T3 is the only table question with a retrieval hit (hits: ['T3'])
- Chunk 758 (page 73, rank 4), first two lines verbatim:

````text
ncome
periode berjalan 714.992 183.979 for the period
````

- The row label line sits in chunk 757 (not retrieved for T3): `Jumlah laba komprehensif Total comprehensive income`; chunk 757 in T3's top 5: False
- Chunk 752 (page 72, rank 1), BPI's total comprehensive income row, verbatim:

````text
Jumlah penghasilan komprehensif Total comprehensive income
periode berjalan 20.463 16.778 for the period
````

### 4. T4: same chunks as T1 and T2, but a refusal [results_ptba.json, DB]

- T1 `What was HBAP's revenue for the period ended March 31, 2026?`: stated True; answer `According to the context, HBAP's revenue for the period ended March 31, 2026 was 203.513 [ptba-quarterly-report.pdf, page 72].`
  - Top 5: #1 chunk 753 p72 0.603; #2 chunk 752 p72 0.603; #3 chunk 744 p70 0.563; #4 chunk 758 p73 0.552; #5 chunk 748 p71 0.543
- T2 `What was HBAP's profit for the period ended March 31, 2026?`: stated True; answer `According to the context, HBAP's profit for the period ended March 31, 2026 was 20.463 (in millions) [ptba-quarterly-report.pdf, page 72].`
  - Top 5: #1 chunk 752 p72 0.604; #2 chunk 753 p72 0.600; #3 chunk 744 p70 0.594; #4 chunk 758 p73 0.553; #5 chunk 748 p71 0.545
- T3 `What was HBAP's total comprehensive income for the period ended March 31, 2026?`: stated True; answer `According to the context, HBAP's total comprehensive income for the period ended March 31, 2026 was 20.463 million Rupiah. [ptba-quarterly-report.pdf, page 72]`
  - Top 5: #1 chunk 752 p72 0.614; #2 chunk 753 p72 0.601; #3 chunk 744 p70 0.585; #4 chunk 758 p73 0.555; #5 chunk 838 p90 0.554
- T4 `What was HBAP's revenue for the period ended March 31, 2025?`: stated False; answer `not stated`
  - Top 5: #1 chunk 752 p72 0.605; #2 chunk 753 p72 0.600; #3 chunk 744 p70 0.568; #4 chunk 758 p73 0.552; #5 chunk 748 p71 0.536
- Top-5 chunk-id sets equal to T4's: T1 True; T2 True; T3 False (T3 differs by: only in T3 [838], only in T4 [748])
- Order of chunks 752 and 753 in each top 5: T1: #1 chunk 753, #2 chunk 752; T2: #1 chunk 752, #2 chunk 753; T3: #1 chunk 752, #2 chunk 753; T4: #1 chunk 752, #2 chunk 753
- Period asked: T1, T2, T3 March 31, 2026; T4 March 31, 2025
- Chunk 752 contains `240.534` (BPI's March 31, 2025 revenue): True; contains `554.473` (HBAP's March 31, 2025 revenue): False
- Chunks of document 4 containing `554.473`: [756, 757]; any of them in T4's top 5: False
- Each question was run once; run-to-run variation of these answers was not measured

### 5. Retrieval-hit rate [results_ptba.json]

- Definition: any top-5 chunk contains `gold_substring` (whitespace collapsed in both texts); answer-bearing rank = first such chunk
- narrative: 7/9
- table: 1/5
- Answerable overall: 8/14; hit from a chunk on an expected page: 7/14; hits only from other pages: ['N9'] (gold hit pages [[71]])
- Retrieval hit = True (8): N1 CORRECT; N4 CORRECT; N5 CORRECT; N6 CORRECT; N7 CORRECT; N8 CORRECT; N9 REFUSED; T3 WRONG
- Retrieval hit = False (6): N2 REFUSED; N3 REFUSED; T1 WRONG; T2 WRONG; T4 REFUSED; T5 REFUSED
- Per answerable question (hit, rank of first answer-bearing chunk, pages of the top 5):
  - N1: hit True, rank 4, expected pages [63], top-5 pages [63, 63, 43, 63, 49]
  - N2: hit False, rank None, expected pages [63], top-5 pages [98, 105, 104, 99, 97]
  - N3: hit False, rank None, expected pages [63], top-5 pages [35, 37, 39, 36, 34]
  - N4: hit True, rank 1, expected pages [73], top-5 pages [73, 73, 73, 71, 119]
  - N5: hit True, rank 1, expected pages [73], top-5 pages [73, 73, 73, 71, 129]
  - N6: hit True, rank 1, expected pages [73], top-5 pages [73, 73, 73, 71, 128]
  - N7: hit True, rank 1, expected pages [63], top-5 pages [63, 63, 49, 49, 106]
  - N8: hit True, rank 1, expected pages [73], top-5 pages [73, 124, 123, 11, 124]
  - N9: hit True, rank 3, expected pages [74], top-5 pages [73, 73, 71, 73, 71]
  - T1: hit False, rank None, expected pages [73], top-5 pages [72, 72, 70, 73, 71]
  - T2: hit False, rank None, expected pages [73], top-5 pages [72, 72, 70, 73, 71]
  - T3: hit True, rank 4, expected pages [73], top-5 pages [72, 72, 70, 73, 90]
  - T4: hit False, rank None, expected pages [73], top-5 pages [72, 72, 70, 73, 71]
  - T5: hit False, rank None, expected pages [72], top-5 pages [89, 90, 70, 152, 152]

### 6. POL eval for comparison [results.json, results_run1-3.json]

- results.json: run_at 2026-10-05T00:07:21.442441+00:00; correct 10/10; citation_ok 10/10; correctly refused 5/5; unsure 0
- results_run1.json: run_at 2026-10-05T00:05:51.442821+00:00; correct 10/10; citation_ok 10/10; correctly refused 5/5; unsure 0
- results_run2.json: run_at 2026-10-05T00:06:36.149723+00:00; correct 10/10; citation_ok 10/10; correctly refused 5/5; unsure 0
- results_run3.json: run_at 2026-10-05T00:07:21.442441+00:00; correct 10/10; citation_ok 10/10; correctly refused 5/5; unsure 0
- stated flags, cited pages and grades identical across results_run1, run2 and run3: True
- answer text of results_run1.json identical to results_run3.json for 9/15 questions
- answer text of results_run2.json identical to results_run3.json for 9/15 questions
- results.json and results_run3.json have the same run_at: True; answer text identical for 15/15 questions
- POL answerable questions with the expected page among the top 5 (results.json): 10/10
- Sections 5 and 8 of this file describe the POL eval as a single run; the re-runs above are later

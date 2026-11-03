# ROADMAP.md: FinanceBench RAG

Ordered tasks only. No dates or time estimates.
Rules: one task per branch (`task/<ID>-short-name`). Tests are written in the same task as the code. A task is ticked only after the owner has run its verification.
Spec references point to sections of `CLAUDE.md` (PROJECT_SPEC.md).

---

## Phase R0: Skills ramp-up

You are new to Python projects. These tasks build the habits used everywhere else. Code from this phase lives in a throwaway folder, not the project repo.

- [x] **R0.1 Install the toolchain**
  - Install Python (version chosen in S1.2), Git, VS Code with the Python extension, and `uv`. `VERIFY:` the current Windows install command on the official uv docs.
  - Learn: what a virtual environment is and why each project has its own.
  - **Done when:** `uv --version`, `git --version` and `uv run python --version` all print a version in a new terminal.

- [x] **R0.2 Python project basics kata**
  - `uv init` a scratch project. Write `slugify(text: str) -> str` with type hints and a docstring.
  - Add `pytest` and `ruff` as dev dependencies. Write 4 tests, including an empty string.
  - Learn: `pyproject.toml`, the lock file, `src/` layout, how pytest finds tests.
  - **Done when:** `uv run pytest` shows 4 passed and `uv run ruff check .` shows no errors.

- [x] **R0.3 FastAPI kata**
  - In the scratch project, build `GET /hello?name=...` returning `{"message": "Hello, <name>"}` with a Pydantic response model.
  - Test it with FastAPI's `TestClient`.
  - Learn: request validation, response models, the auto-generated `/docs` page.
  - **Done when:** the test passes, and `/docs` opens in a browser while `uv run uvicorn ...` is running.

- [x] **R0.4 Git and CI kata**
  - Push the scratch project to a GitHub repo. Create a branch, commit with a Conventional Commit message, open a pull request.
  - Add a GitHub Actions workflow that runs ruff and pytest.
  - **Done when:** the pull request shows a green check from the workflow.

---

## Phase S1: Setup

- [x] **S1.1 Create the repo skeleton**
  - New GitHub repo `financebench-rag`. Create the layout in spec Section 14 with empty `__init__.py` files.
  - Copy in `CLAUDE.md` (this spec), `ROADMAP.md`, `docs/*.md`, `.env.example`, `.gitignore`.
  - **Done when:** `git ls-files` lists all of the above and no `.env` file.

- [x] **S1.2 Pin versions**
  - Choose the current stable versions of Python and every library in spec Section 4. Check each on its official page or PyPI. Record the version, the date checked and the source URL in `docs/VERSIONS.md`.
  - Confirm the licences of pypdf, PyMuPDF (to confirm why we reject it) and rank-bm25. Record the `rank-bm25` default `k1` and `b` from its source code.
  - **Done when:** `uv sync` succeeds, `uv.lock` is committed, and every row in VERSIONS.md has a version, date and source.

- [x] **S1.3 CI and settings**
  - `.github/workflows/ci.yml` runs `uv run ruff check .` and `uv run pytest` on push and pull request.
  - `src/finrag/config.py` with `pydantic-settings` reading every variable in `.env.example`, with the defaults from the spec.
  - Test: settings load with defaults; an invalid value (for example `CHUNK_OVERLAP=-1`) raises an error.
  - **Done when:** CI is green on the pull request and the config tests pass.

- [ ] **S1.4 Gemini API access**
  - Create an API key in Google AI Studio. Put it in `.env` only.
  - In AI Studio, record the chosen answer and judge model IDs and their free-tier limits (RPM, RPD, TPM) in VERSIONS.md with the date.
  - Note in DECISIONS.md that free-tier prompts may be used by Google, and why that is acceptable here.
  - **Done when:** VERSIONS.md has the model IDs and limits, and `git grep -i "AIza"` (the usual Google key prefix) returns nothing.

---

## Phase D2: Data

- [ ] **D2.1 Licence check, manifest and download script**
  - Open the FinanceBench GitHub repo. Read its LICENSE file (or state that there is none). Record the result in DECISIONS.md and update spec Section 8.
  - Count the distinct `doc_name` values in the open sample and record it.
  - Write `scripts/download_data.py`: downloads the two JSONL files and the PDFs the questions need into `data/raw/`, checks SHA-256 against `data/manifest.json`, and stops on a mismatch.
  - Unit test the checksum function with a small fixture file whose hash you computed with `certutil -hashfile <file> SHA256` (Windows).
  - **Done when:** a fresh run downloads all files and prints `all checksums OK`; a deliberately corrupted file makes it exit with a non-zero code; `data/raw/` is not tracked by git.

- [ ] **D2.2 Load questions and metadata into SQLite**
  - `src/finrag/db.py` creates the schema in spec Section 6.
  - `ingest/load_dataset.py` reads both JSONL files into `documents`, `questions` and `evidence`.
  - Check the real field names (`question_type`, `question_reasoning`, evidence page field). Check whether the evidence page number is 0-based or 1-based by opening 3 PDFs at the stated page. Store pages as 1-based. Update the spec if field names differ (Change Request if the schema changes).
  - Tests: row counts on a 3-question fixture; foreign keys reject an unknown `doc_name`.
  - **Done when:** `SELECT COUNT(*) FROM questions` returns 150; the 3 hand-checked evidence pages match the PDF; tests pass.

- [ ] **D2.3 Page text extraction and extraction quality check**
  - `ingest/pdf_text.py` per spec Section 7.1. Fill `pages`.
  - Script reports the evidence-found rate from Section 7.1, broken down by document.
  - Tests: a 2-page fixture PDF you create (for example "Print to PDF" from a short Word file) extracts the expected text per page.
  - **Done when:** every document has rows in `pages` equal to its page count, and the evidence-found rate is saved to `eval/reports/<date>_extraction_check.md`.

- [ ] **D2.4 Chunking**
  - `ingest/chunking.py` per spec Section 7.2. Fill `chunks` with `vector_row` assigned in order.
  - Tests with hand-worked expected outputs: 0 words; fewer words than the window; exactly one window; window plus a short tail; tail fully overlapped (dropped); invalid overlap raises `ValueError`.
  - **Done when:** tests pass, no chunk has an empty text, and no chunk spans two pages (SQL check in the test suite).

- [ ] **D2.5 Lock the dev/test split**
  - `eval/split.py` per spec Section 12.1. Write `eval/splits/split_v1.json` and set `questions.split`.
  - Test: same seed gives the same split; counts are 50 and 100; strata proportions are within one question of the overall proportions.
  - **Done when:** `split_v1.json` is committed, and DECISIONS.md records the seed and the reason for 50/100. From now on the test split is sealed.

---

## Phase C3: Core logic

No tuning in this phase. Use spec defaults only.

- [ ] **C3.1 Tokeniser and BM25 retrieval**
  - `retrieval/tokenise.py` and `retrieval/bm25.py` per spec Section 7.3, supporting both scope modes.
  - Tests: tokeniser cases (`"1,234.5"`, `"FY2018."`, `"capital-expenditure"`, empty string) with hand-written expected tokens; on a 4-chunk fixture, a query containing a rare word ranks the chunk with that word first.
  - **Done when:** tests pass, and a CLI call `uv run python -m finrag.retrieval.bm25 "<question>" --doc <doc>` prints 5 chunk IDs with pages.

- [ ] **C3.2 Embeddings and dense retrieval**
  - Confirm the embedding model's licence, size and any required query prefix on its model card. Record in VERSIONS.md.
  - `retrieval/dense.py` per spec Section 7.4. Build the `.npy` file.
  - Measure build time and peak RAM on your laptop (Task Manager or `psutil`). If the build takes too long or runs out of memory, run the build in a Colab notebook and copy the `.npy` back; record which in DECISIONS.md.
  - Tests: vectors have length 1 (within 1e-5); on a 3-chunk fixture with a fake encoder returning fixed vectors, the ranking matches a hand calculation.
  - **Done when:** the `.npy` row count equals `SELECT COUNT(*) FROM chunks`, tests pass, and build time and peak RAM are recorded in the session log.

- [ ] **C3.3 Reciprocal Rank Fusion**
  - `retrieval/fusion.py` per spec Section 7.5.
  - Tests: the spec example with scores and order you calculated by hand or in a spreadsheet; a chunk in only one list; tie-breaking by `chunk_id`.
  - **Done when:** tests pass with expected values you computed yourself.

- [ ] **C3.4 Reranker**
  - Confirm the cross-encoder's licence and size. Record in VERSIONS.md.
  - `retrieval/rerank.py` per spec Section 7.6. Tests use a fake scorer so they run without downloading the model.
  - **Done when:** tests pass, and reranking 20 chunks for one question runs locally with its time recorded in the session log.

- [ ] **C3.5 Retrieval pipeline**
  - `retrieval/pipeline.py`: one function taking a question, optional `doc_name`, and a config naming the stages (`bm25`, `dense`, `rrf`, `rerank`) and k values. Returns ranked chunks.
  - Tests: each of the four ablation configs (spec 12.6) runs on fixtures; `doc_scoped` returns only chunks from that document; unknown doc raises the `DOC_NOT_FOUND` error type.
  - **Done when:** tests pass.

---

## Phase B4: API

- [ ] **B4.1 App skeleton, errors and health**
  - `api/main.py`, `api/errors.py`, `api/schemas.py`. Error format and codes per spec Section 10, including converting 422 to 400 `INVALID_INPUT`. `X-Request-ID` on every response. JSON logging.
  - Endpoints: `GET /api/health`, `GET /api/documents`.
  - Tests with `TestClient`: health returns `ok`; a request with an unknown field returns 400 in our error format; request ID header present.
  - **Done when:** tests pass and `/docs` shows both endpoints.

- [ ] **B4.2 Search endpoint**
  - `POST /api/search` per spec Section 10, using the pipeline from C3.5.
  - Tests: valid request in each mode; `top_k` of 0 and 21 rejected; question of 1001 characters rejected; unknown doc gives 404 `DOC_NOT_FOUND`.
  - **Done when:** tests pass, and a `curl` (or `Invoke-RestMethod`) call against the running app returns 5 results with pages.

---

## Phase A5: AI

- [ ] **A5.1 LLM client interface, cache and fake**
  - `llm/client.py` (protocol and result type with text, input tokens, output tokens), `llm/fake.py`, `llm/cache.py`, `llm/gemini.py`.
  - Gemini client uses only the SDK functions documented for the pinned version (link the doc page in a code comment). Retry and backoff per spec Section 8.
  - Tests use the fake only: cache hit returns stored text without calling the client; cache key changes when the prompt version changes; retry logic runs 3 attempts on a fake that raises a rate-limit error.
  - Manual check: one real call with a short prompt.
  - **Done when:** tests pass, the manual call prints a reply and token counts, and running it twice shows a cache hit the second time.

- [ ] **A5.2 Answer prompt and validation**
  - Write `prompts/answer_v1.txt`. `answer/validate.py` per spec Section 7.8.
  - Tests for each validation path: valid JSON; JSON inside a code fence; missing key; unknown citation label; refused answer gets the fixed text; retry then success; retry then failure.
  - **Done when:** all validation tests pass.

- [ ] **A5.3 Ask endpoint**
  - `answer/generate.py` and `POST /api/ask` per spec Section 10. Rate limit and daily cap per spec Section 13. LLM-unavailable fallback per spec Section 9.
  - Tests with the fake client: success maps labels to pages; refusal; `LLM_UNAVAILABLE` returns 503; sixth request in a minute from one IP returns 429.
  - Manual check: 3 dev questions answered live; note the results in the session log (not as metrics).
  - **Done when:** tests pass and the 3 live answers return valid citations.

---

## Phase E6: Evaluation

- [ ] **E6.1 Retrieval metrics**
  - `eval/retrieval_metrics.py`: `page_hit@k`, `page_MRR@20`, `doc_hit@k` per spec Section 12.2.
  - Tests: 3 hand-made questions with known gold pages and rankings; expected values worked out by hand.
  - **Done when:** tests pass with your hand-calculated values.

- [ ] **E6.2 Statistics functions**
  - `eval/stats.py`: Wilson 95% interval, paired bootstrap for accuracy difference, Cohen's kappa.
  - Expected values: Wilson and kappa checked against `statsmodels` (reference implementation) and one case each by hand in a spreadsheet. Bootstrap: test reproducibility with a fixed seed, and that identical inputs give a difference of exactly 0.
  - **Done when:** tests pass, and the spreadsheet you used is saved in `tests/fixtures/`.

- [ ] **E6.3 Retrieval ablation on dev**
  - `eval/run.py --retrieval-only --split dev` runs configs A to D in both scope modes and writes a report per spec Section 12.7.
  - **Done when:** `eval/reports/<date>_retrieval_ablation_dev.md` and `.json` exist with all 8 rows and intervals. Any setting change based on it is recorded in DECISIONS.md.

- [ ] **E6.4 Numeric check and judge**
  - `eval/numeric.py` per spec Section 7.9; tests with at least 10 hand-written cases (commas, `$`, parentheses negatives, millions, billions, percentages, zero, no number).
  - Write `prompts/judge_v1.txt`. `eval/judge.py` per spec Section 9, with fake-client tests for each path.
  - **Done when:** tests pass.

- [ ] **E6.5 Human labels and judge validation**
  - Run the answer pipeline (current default config) on all 50 dev questions.
  - Export 40 answers to `eval/labels/human_labels_dev.csv` **without judge labels**. Label each CORRECT or INCORRECT yourself using the gold answer and the PDF.
  - Then run the judge and compute agreement and kappa.
  - If kappa is below 0.6, revise the judge prompt (new version file), re-run, re-check. Record each attempt.
  - **Done when:** `eval/reports/<date>_judge_validation.md` shows agreement and kappa, and DECISIONS.md records the judge prompt version that passed.

- [ ] **E6.6 End-to-end evaluation runner**
  - `eval/run.py --split dev --config <name>`: retrieval, answer, judge, numeric check, tokens, latency. Prints the planned number of LLM calls and asks for confirmation. Resumes after interruption.
  - Integration test with the fake client on 3 fixture questions writes a complete report.
  - **Done when:** the integration test passes, and a real dev run produces a report.

- [ ] **E6.7 Answer ablation on dev**
  - Run the best two retrieval configs from E6.3 plus config A, in both scope modes, on dev. Paired bootstrap comparisons between them.
  - Freeze the final configuration in DECISIONS.md, with the report that justifies it.
  - **Done when:** `eval/reports/<date>_answer_ablation_dev.md` exists, and DECISIONS.md has a "Final config" entry.

- [ ] **E6.8 Failure taxonomy on dev**
  - Label every dev failure from the final config with a category from spec Section 12.7 in a CSV.
  - **Done when:** `eval/reports/<date>_failure_taxonomy_dev.md` shows counts per category and 3 worked examples.

- [ ] **E6.9 Sealed test run (once)**
  - Run the frozen config on the test split in both scope modes. No changes afterwards based on these results.
  - Mark the report as published in `eval/reports/published.json`.
  - **Done when:** exactly one test report exists in `eval/reports/`, its config matches the frozen config, and `GET /api/eval/latest` returns its summary.

- [ ] **E6.10 Results write-up**
  - Add a "Results and limitations" section to the test report: what the numbers mean, interval widths, judge bias, small dataset, US-only filings, table extraction limits.
  - **Done when:** the section exists and every number in it matches the JSON report.

---

## Phase F7: Frontend

- [ ] **F7.1 Ask page**
  - `web/index.html`, `app.js`, `styles.css` per spec Section 11: selector, question box, answer panel, citations, evidence list, all states.
  - **Done when:** in the browser you can trigger and screenshot each state: idle, loading, success, refused, error, empty.

- [ ] **F7.2 Evaluation tab**
  - Shows published metrics with intervals from `/api/eval/latest` and a link to the report on GitHub.
  - **Done when:** the numbers on the page match the published JSON report exactly.

- [ ] **F7.3 Accessibility pass**
  - Keyboard-only walkthrough; labels; `aria-live`; contrast check with a browser tool.
  - **Done when:** a checklist in the session log shows each item from spec Section 11 passed, with any fixes committed.

---

## Phase T8: Testing

(Unit tests already exist from each task. This phase covers the whole system.)

- [ ] **T8.1 End-to-end API test**
  - Integration test: build a tiny index from fixture data, start the app with the fake LLM, call search and ask in both modes.
  - **Done when:** the test passes in CI.

- [ ] **T8.2 Coverage check**
  - Add `pytest-cov` (Change Request if not already pinned). Report coverage for `src/finrag/`.
  - **Done when:** CI prints a coverage figure and every calculation module (fusion, retrieval metrics, numeric, stats) has 100% line coverage.

- [ ] **T8.3 Security and secrets check**
  - Run a dependency audit (`pip-audit` or equivalent: `VERIFY:` tool and version) and fix or document findings.
  - Search history for secrets: `git log -p | findstr /i "api_key AIza"` returns nothing.
  - **Done when:** the audit report is saved in the session log with no unresolved high-severity issues, and the secret search is empty.

---

## Phase L9: Deployment

- [ ] **L9.1 Choose the host**
  - Check current free options: Hugging Face Spaces (Docker on CPU Basic: does it need a paid plan?), Google Cloud Run free tier, Render free tier. Record limits, sleep behaviour and cost with sources and dates.
  - If none is free and fits the measured RAM, raise a Change Request with the cheapest option.
  - **Done when:** DECISIONS.md records the host, with sources, and spec Section 8 has no `VERIFY:` for hosting.

- [ ] **L9.2 Docker image**
  - `Dockerfile` and `.dockerignore`. Bake in the SQLite DB, `.npy` file and model weights (check licences allow redistribution in an image; record in DECISIONS.md). No secrets in the image.
  - **Done when:** `docker build` succeeds, `docker run` with `--env-file .env` serves the app at `localhost`, and `docker history` shows no secret values.

- [ ] **L9.3 Deploy and measure**
  - Deploy. Set the API key as a host secret.
  - Measure on the deployed app: peak memory (host dashboard), p50 and p95 latency of `/api/search` and `/api/ask` over 20 dev questions.
  - **Done when:** the public URL serves the app, rate limit returns 429 on the sixth fast request, and `eval/reports/<date>_deployment_perf.md` exists.

---

## Phase I10: Portfolio and interview readiness

- [ ] **I10.1 README**
  - Pitch, demo link, architecture diagram, how to run locally, how to reproduce the evaluation, results table quoting only linked reports, limitations, dataset source and licence.
  - **Done when:** every number in the README links to a file in `eval/reports/`, and a fresh clone following the README reaches a running app.

- [ ] **I10.2 Demo recording**
  - 2 to 3 minutes: one good answer with citation, one refusal, the evaluation tab, a quick look at the report.
  - **Done when:** the video is linked from the README.

- [ ] **I10.3 CV bullets**
  - 2 to 3 bullets using only measured numbers, each traced to a report file.
  - **Done when:** each bullet has a source file noted next to it in the session log.

- [ ] **I10.4 Explain it without notes**
  - Practise out loud, without notes, until you can explain each:
    1. The whole request flow from browser to answer.
    2. Why hybrid retrieval, and what RRF does with a worked example.
    3. What the reranker adds and its cost.
    4. Why chunks never cross pages.
    5. How the dev/test split prevents overfitting.
    6. Wilson interval and paired bootstrap, in plain words.
    7. How the judge was validated and what kappa means.
    8. The top two failure categories and how you would fix them.
    9. Every row in spec Section 16.
    10. What you would change to scale to 100,000 filings.
  - **Done when:** you have answered all 10 to a friend (or recorded yourself) without notes, and noted weak spots in the session log.

---

## Stretch goals (blocked until the Definition of Done is met)

- [ ] S1 Open-weights generator comparison on Colab T4
- [ ] S2 Better table extraction as an ablation
- [ ] S3 Deterministic calculator step for arithmetic questions
- [ ] S4 Query rewriting with company and fiscal year

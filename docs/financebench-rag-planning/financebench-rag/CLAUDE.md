# PROJECT_SPEC.md: FinanceBench RAG

> Copy this file into the repo root as `CLAUDE.md` (and `AGENTS.md` if you use other assistants).
> It is the single source of truth. Changes go through a Change Request, then this file is updated before any code changes.
> Spec version: 1.0 (2026-11-01)

---

## 0. Rules for any AI assistant in this repo

1. **One task at a time.** Work only on the task ID you were given from `ROADMAP.md`. State the ID at the start.
2. **No scope creep.** Anything not in this spec (new dependency, schema change, new endpoint, new feature) needs a Change Request first. Section 3 lists the non-goals. Do not build them.
3. **Never invent APIs.** Library versions are pinned in `docs/VERSIONS.md`. Use only functions, classes, flags and config keys that exist in those versions. If unsure, say "I am not certain" and give the doc page or a tiny check to run.
4. **Done means green.** Code runs, `ruff check` passes, `pytest` passes, CI is green. Tests are written in the same task as the code.
5. **No secrets in git.** Keys live in `.env` (ignored). Only `.env.example` with names is committed.
6. **No unmeasured numbers.** Any metric in docs, README or CV must link to a dated report in `eval/reports/`. Use `<measured in task X>` until then.
7. **Independent expected values.** Expected values in tests for calculations (metrics, statistics, fusion scores, number parsing) come from a hand calculation, a spreadsheet or a reference library that the owner checks. Never from the AI that wrote the code.
8. **Explain new concepts.** The owner is new to Python projects. Give a short explanation the first time a concept appears.
9. **Record decisions** in `docs/DECISIONS.md` with a link to the task.
10. **Style:** British English, no emojis, short sentences. Python: type hints, small functions, docstrings on public functions, no clever one-liners.
11. **The test split is sealed.** No code, prompt or setting may be changed based on test-split results. Only task E6.9 runs on the test split.

---

## 1. Pitch

A question-answering system over real US company filings (10-K, 10-Q and similar) from the public FinanceBench sample. It answers with the page it used, shows the evidence, and refuses when the evidence is not there. Its quality is measured on FinanceBench with a sealed test split, confidence intervals and a validated scorer. Every number it claims links to a dated report.

**Example usage**

```
POST /api/ask
{"question": "What is the FY2018 capital expenditure amount (in USD millions) for 3M?",
 "doc_name": "3M_2018_10K"}

-> {"answer": "<model answer>",
    "citations": [{"doc_name": "3M_2018_10K", "page": <page>}],
    "refused": false, ...}
```

(The example question style follows the dataset. Real answers appear only after task A5.3.)

---

## 2. Problem and users

**Problem.** Filings are long (often over 100 pages) and full of tables. Analysts need exact figures with a traceable source. General chatbots answer confidently and often wrongly. The FinanceBench authors reported that GPT-4-Turbo with a retrieval system got 81% of the sample questions wrong or refused them (arXiv 2311.11944, 2023). The lesson: a finance QA system is only useful if its accuracy is measured honestly and every answer can be checked against its source.

**Users**
- Primary (real audience): hiring managers and engineers reviewing an AI engineering portfolio. They read the README, the evaluation report and the code, and try the demo.
- Nominal (in-product): someone asking factual questions about a specific company filing.

---

## 3. Scope

### In scope (MVP)

| ID | Feature | Notes |
|---|---|---|
| F1 | Download and ingest the FinanceBench open-source sample (questions, document metadata, PDFs) | Download script plus manifest with checksums |
| F2 | Page-level text extraction and chunking | Chunks never cross page boundaries |
| F3 | Keyword retrieval (BM25) | Section 7.3 |
| F4 | Dense retrieval (embeddings) | Section 7.4 |
| F5 | Hybrid fusion (Reciprocal Rank Fusion) | Section 7.5 |
| F6 | Cross-encoder reranking | Section 7.6 |
| F7 | Two scope modes: `doc_scoped` and `corpus_wide` | Section 7.7 |
| F8 | Answer generation with page citations and refusal | Sections 7.8 and 9 |
| F9 | Evaluation harness: retrieval metrics, LLM judge, numeric check, cost, latency, confidence intervals | Section 12 |
| F10 | Ablation study on the dev split, one sealed run on the test split | Section 12 |
| F11 | FastAPI backend | Section 10 |
| F12 | Single-page web UI with an evaluation results page | Section 11 |
| F13 | Docker image, CI, public deployment | Sections 13 and 14 |

### Non-goals (explicit)

- Kafka, Kubernetes, message queues, microservices.
- Fine-tuning or training any model.
- User accounts, login, saved history.
- The full 10,231-question FinanceBench set (not public).
- Uploading arbitrary user documents.
- Live market data or any non-FinanceBench data source.
- Multi-step agents, tool calling, or a calculator tool.
- A hosted vector database (Pinecone, Qdrant cloud and similar).
- LangChain, LlamaIndex or similar frameworks (see Section 16).
- Paid GPU hosting.

### Stretch goals (blocked until the Definition of Done is met)

- S1: Open-weights generator comparison (run on Colab T4) against the API model.
- S2: Better table extraction (for example pdfplumber table mode) as an ablation.
- S3: Deterministic calculator step for questions that need arithmetic.
- S4: Query rewriting (adding company and fiscal year from the question to the query).

---

## 4. Tech stack (locked)

Versions are chosen in task S1.2 and recorded in `docs/VERSIONS.md`. They are never guessed in this file.

| Layer | Choice | Notes |
|---|---|---|
| Language | Python 3.12 or newer stable | Exact version recorded in S1.2 |
| Project and dependencies | `uv` with `pyproject.toml` and `uv.lock` | One tool for venv, install and lock. `VERIFY:` install steps on Windows in R0.1 |
| Lint and format | ruff | |
| Tests | pytest | |
| PDF text | pypdf | Permissive licence (`VERIFY:` in S1.2). PyMuPDF rejected: AGPL licence (`VERIFY:`) |
| Storage | SQLite (Python standard library `sqlite3`) | Metadata, chunks, eval results, LLM cache |
| Vectors | NumPy `.npy` file, brute-force cosine | Corpus is small. FAISS only via Change Request if measured too slow |
| BM25 | `rank-bm25` | `VERIFY:` default k1 and b in S1.2 |
| Embeddings | `sentence-transformers` with a small English model | Candidate: `BAAI/bge-small-en-v1.5`. `VERIFY:` licence, size, RAM use in C3.2 |
| Reranker | Cross-encoder via `sentence-transformers` | Candidate: `cross-encoder/ms-marco-MiniLM-L-6-v2`. `VERIFY:` licence, size in C3.4 |
| LLM (answer and judge) | Google Gemini API, a Flash-family model on the free tier, behind our own `LLMClient` interface | `VERIFY:` model IDs and free-tier limits in AI Studio in S1.4. Free-tier prompts may be used by Google to improve products. Acceptable because all data is public |
| Settings | `pydantic-settings` reading environment variables | |
| API | FastAPI with Uvicorn | |
| Frontend | Plain HTML, CSS and JavaScript served by FastAPI | No build step, no framework |
| Statistics | Own implementation, checked against hand calculations and `statsmodels` as reference (dev dependency only) | |
| CI | GitHub Actions | ruff plus pytest on every push and pull request |
| Container | Docker | |
| Hosting | `VERIFY:` decided in L9.1. Hugging Face Spaces docs currently conflict on whether a Docker Space on free CPU Basic needs a paid plan | See Section 8 |
| Heavy batch jobs | Google Colab free T4 via the official VS Code extension, only if a local CPU job is measured too slow | Notebook only. Outputs copied back as files |

**Development machine:** Lenovo Slim 5, AMD Ryzen 7 7735HS (8 cores, 16 threads), 16 GB LPDDR5 (13.3 GB usable), AMD Radeon 680M integrated GPU. No CUDA. All local model work runs on CPU. RAM is the main constraint: close other apps before model runs.

---

## 5. Architecture

```
                 +-------------------------------+
  Browser  --->  |  FastAPI app (finrag.api)      |
  (web/)         |   /api/search  /api/ask       |
                 |   /api/documents  /api/health |
                 |   /api/eval/latest            |
                 +-------+---------------+-------+
                         |               |
               +---------v----+   +------v-----------+
               | Retrieval    |   | Answer generator |
               | pipeline     |   | (prompt, call,   |
               | BM25 + dense |   |  validate)       |
               | -> RRF       |   +------+-----------+
               | -> rerank    |          |
               +--+-------+---+   +------v-----------+
                  |       |       | LLMClient        |
          +-------v--+ +--v----+  |  GeminiClient    |
          | SQLite   | | .npy  |  |  FakeClient      |
          | chunks,  | | vecs  |  |  + SQLite cache  |
          | docs     | +-------+  +------------------+
          +----^-----+
               |  built offline by
     +---------+-----------------------------+
     | Ingestion CLI: download -> extract    |
     | pages -> chunk -> BM25 -> embed       |
     +---------------------------------------+

     +---------------------------------------+
     | Evaluation CLI: split -> retrieve ->  |
     | answer -> judge -> stats -> report    |
     | writes eval/reports/<date>_<run>.*    |
     +---------------------------------------+
```

**Module layout (`src/finrag/`)**

| Module | Responsibility |
|---|---|
| `config.py` | Settings from environment variables |
| `db.py` | SQLite connection, schema creation, queries |
| `ingest/load_dataset.py` | Read FinanceBench JSONL files into SQLite |
| `ingest/pdf_text.py` | Page-level text extraction |
| `ingest/chunking.py` | Page to chunks |
| `retrieval/tokenise.py` | Tokeniser shared by BM25 and the numeric checker |
| `retrieval/bm25.py` | BM25 index build and query |
| `retrieval/dense.py` | Embedding build and query |
| `retrieval/fusion.py` | Reciprocal Rank Fusion |
| `retrieval/rerank.py` | Cross-encoder reranking |
| `retrieval/pipeline.py` | Config-driven retrieval (which stages, k values, scope) |
| `llm/client.py` | `LLMClient` protocol and result type |
| `llm/gemini.py` | Gemini implementation |
| `llm/fake.py` | Deterministic fake for tests |
| `llm/cache.py` | Response cache keyed by hash |
| `answer/generate.py` | Build prompt, call LLM, return validated answer |
| `answer/validate.py` | JSON and citation validation |
| `eval/split.py` | Create and load the dev/test split |
| `eval/retrieval_metrics.py` | hit@k, MRR |
| `eval/numeric.py` | Number extraction and matching |
| `eval/judge.py` | LLM judge |
| `eval/stats.py` | Wilson interval, paired bootstrap, Cohen's kappa |
| `eval/run.py` | End-to-end evaluation CLI |
| `eval/report.py` | Write Markdown and JSON reports |
| `api/main.py`, `api/schemas.py`, `api/errors.py`, `api/ratelimit.py` | HTTP layer |

---

## 6. Data model

SQLite. File path from `DB_PATH`. Created by `finrag.db.create_schema()`. Foreign keys enabled per connection (`PRAGMA foreign_keys = ON`).

```sql
-- One row per filing in the FinanceBench open sample.
CREATE TABLE documents (
    doc_name        TEXT PRIMARY KEY,            -- e.g. '3M_2018_10K', from the dataset
    company         TEXT NOT NULL,
    sector_gics     TEXT,
    doc_type        TEXT,                        -- e.g. '10k', from dataset metadata
    doc_period      INTEGER,                     -- fiscal year, from dataset metadata
    pdf_sha256      TEXT NOT NULL,               -- checksum from the manifest
    page_count      INTEGER NOT NULL CHECK (page_count > 0)
);

-- Extracted text per PDF page. page_number is 1-based, as shown in a PDF viewer.
CREATE TABLE pages (
    doc_name        TEXT NOT NULL REFERENCES documents(doc_name),
    page_number     INTEGER NOT NULL CHECK (page_number >= 1),
    text            TEXT NOT NULL,               -- may be '' if extraction found nothing
    char_count      INTEGER NOT NULL CHECK (char_count >= 0),
    PRIMARY KEY (doc_name, page_number)
);

-- Retrieval units. A chunk never crosses a page boundary.
CREATE TABLE chunks (
    chunk_id        TEXT PRIMARY KEY,            -- '<doc_name>:<page_number>:<chunk_index>'
    doc_name        TEXT NOT NULL REFERENCES documents(doc_name),
    page_number     INTEGER NOT NULL CHECK (page_number >= 1),
    chunk_index     INTEGER NOT NULL CHECK (chunk_index >= 0),
    text            TEXT NOT NULL CHECK (length(text) > 0),
    word_count      INTEGER NOT NULL CHECK (word_count > 0),
    vector_row      INTEGER NOT NULL UNIQUE,     -- row in embeddings .npy
    chunking_config TEXT NOT NULL,               -- e.g. 'words300_overlap50'
    FOREIGN KEY (doc_name, page_number) REFERENCES pages(doc_name, page_number)
);
CREATE INDEX idx_chunks_doc ON chunks(doc_name);

-- FinanceBench questions (open sample).
CREATE TABLE questions (
    financebench_id TEXT PRIMARY KEY,            -- dataset id, stored as text
    doc_name        TEXT NOT NULL REFERENCES documents(doc_name),
    question        TEXT NOT NULL,
    gold_answer     TEXT NOT NULL,
    question_type   TEXT,                        -- VERIFY: exact field name in D2.2
    question_reasoning TEXT,                     -- VERIFY: field exists, D2.2
    split           TEXT CHECK (split IN ('dev', 'test'))   -- set in task D2.5
);

-- Gold evidence. One question can have several evidence items.
CREATE TABLE evidence (
    financebench_id TEXT NOT NULL REFERENCES questions(financebench_id),
    evidence_index  INTEGER NOT NULL CHECK (evidence_index >= 0),
    doc_name        TEXT NOT NULL REFERENCES documents(doc_name),
    page_number     INTEGER NOT NULL CHECK (page_number >= 1),  -- converted to 1-based in D2.2
    evidence_text   TEXT NOT NULL,
    PRIMARY KEY (financebench_id, evidence_index)
);
CREATE INDEX idx_evidence_doc_page ON evidence(doc_name, page_number);

-- One row per evaluation run.
CREATE TABLE eval_runs (
    run_id          TEXT PRIMARY KEY,            -- '<YYYY-MM-DD>_<short name>'
    created_at      TEXT NOT NULL,               -- ISO 8601 UTC
    split           TEXT NOT NULL CHECK (split IN ('dev', 'test')),
    config_json     TEXT NOT NULL,               -- full retrieval + model + prompt config
    git_commit      TEXT NOT NULL,
    notes           TEXT
);

-- One row per question per run.
CREATE TABLE eval_results (
    run_id          TEXT NOT NULL REFERENCES eval_runs(run_id),
    financebench_id TEXT NOT NULL REFERENCES questions(financebench_id),
    retrieved_json  TEXT NOT NULL,               -- ordered list of chunk_ids
    page_hit_at_5   INTEGER NOT NULL CHECK (page_hit_at_5 IN (0, 1)),
    answer_json     TEXT,                        -- NULL for retrieval-only runs
    judge_label     TEXT CHECK (judge_label IN ('CORRECT', 'INCORRECT', 'REFUSED')),
    numeric_match   TEXT CHECK (numeric_match IN ('MATCH', 'NO_MATCH', 'NOT_APPLICABLE')),
    input_tokens    INTEGER CHECK (input_tokens >= 0),
    output_tokens   INTEGER CHECK (output_tokens >= 0),
    latency_ms      INTEGER CHECK (latency_ms >= 0),
    error_code      TEXT,
    PRIMARY KEY (run_id, financebench_id)
);

-- Cache so repeated runs do not spend API quota.
CREATE TABLE llm_cache (
    cache_key       TEXT PRIMARY KEY,            -- sha256 of model_id + prompt_version + full prompt + params
    model_id        TEXT NOT NULL,
    response_text   TEXT NOT NULL,
    input_tokens    INTEGER,
    output_tokens   INTEGER,
    created_at      TEXT NOT NULL
);
```

**Embeddings file:** `INDEX_DIR/embeddings_<model_slug>_<chunking_config>.npy`, shape `(n_chunks, dim)`, float32, L2-normalised. Row `i` belongs to the chunk with `vector_row = i`.

**BM25 index:** rebuilt in memory at start-up from `chunks` (small corpus). No separate file.

---

## 7. Core logic

All defaults below are starting values. They may be tuned **only on the dev split**, and each change is recorded in `docs/DECISIONS.md`.

### 7.1 Page extraction

- Input: PDF path. Output: list of `(page_number, text)`, 1-based.
- Use pypdf text extraction, one call per page.
- A page that raises an extraction error is stored with `text = ''` and logged with the doc name and page. The run continues.
- Whitespace normalisation: replace runs of whitespace with one space, strip ends. Nothing else.
- **Extraction quality check (D2.3):** for each gold evidence item, normalise both strings (lowercase, collapse whitespace, remove characters other than letters, digits and `.`), then check whether the first 100 normalised characters of the evidence text appear in the normalised extracted text of the gold page. Report the share of evidence items found. This measures how badly tables are parsed, before any retrieval work.

### 7.2 Chunking

- Input: one page of text. Output: list of chunks.
- Split on whitespace into words.
- Window of `CHUNK_WORDS` words (default 300), step of `CHUNK_WORDS - CHUNK_OVERLAP` (default overlap 50, so step 250).
- Pages with 0 words give no chunks. Pages with fewer than `CHUNK_WORDS` words give exactly one chunk.
- The last window may be shorter. If the last window would contain only words already in the previous chunk, it is dropped.
- `chunk_index` starts at 0 per page.
- Validation: `CHUNK_OVERLAP` must be at least 0 and less than `CHUNK_WORDS`, otherwise raise `ValueError`.

### 7.3 BM25 keyword retrieval

*Concept refresher: BM25 ranks text by how often query words appear in it, giving more weight to rare words and less weight to very long chunks.*

- Tokeniser (`tokenise.py`), shared with the numeric checker:
  1. Lowercase.
  2. Remove thousands separators inside numbers: `1,234.5` becomes `1234.5`.
  3. Split on any character that is not a letter, digit or `.`; then strip leading and trailing `.` from each token.
  4. Drop empty tokens. No stemming, no stop-word removal in v1.
- Score with `rank-bm25` (`BM25Okapi`) using library default parameters (values recorded in VERSIONS.md).
- Return top `K_BM25` (default 50) chunk IDs with scores, highest first. Ties broken by `chunk_id` ascending.

### 7.4 Dense retrieval

*Concept refresher: an embedding model turns text into a vector so that texts with similar meaning have vectors pointing in similar directions. Cosine similarity measures that direction.*

- Embed every chunk once, offline. Normalise each vector to length 1.
- Query: embed the question with the same model (and the query prefix the model card requires, if any: `VERIFY:` in C3.2), normalise, then score = dot product with every chunk vector.
- Return top `K_DENSE` (default 50), highest first, ties by `chunk_id`.

### 7.5 Reciprocal Rank Fusion (RRF)

*Concept refresher: RRF combines several ranked lists using only the ranks, so BM25 scores and cosine scores never need to be on the same scale.*

- `score(c) = sum over lists L of 1 / (RRF_K + rank_L(c))`, with ranks starting at 1.
- A chunk missing from a list contributes 0 for that list.
- Default `RRF_K = 60`.
- Output sorted by score descending, ties by `chunk_id` ascending.
- Test case for the owner to calculate by hand (rule 7): lists `[a, b, c]` and `[b, d]` with `RRF_K = 60`. The owner works out each score and the final order on paper or in a spreadsheet, and those values go into the test.

### 7.6 Reranking

*Concept refresher: a cross-encoder reads the question and one chunk together and outputs a relevance score. It is slower but more accurate than comparing separate embeddings, so it is used only on the top candidates.*

- Take the top `N_RERANK` (default 20) fused chunks, score each `(question, chunk_text)` pair, sort by score descending, ties by `chunk_id`.
- Return top `TOP_K` (default 5).

### 7.7 Scope modes

- `doc_scoped`: only chunks with `doc_name = <given doc>` are candidates. In evaluation, the given doc is the question's own `doc_name`. Unknown `doc_name` gives error `DOC_NOT_FOUND`.
- `corpus_wide`: all chunks are candidates. `doc_name` must be absent.
- Both modes run in evaluation. `doc_scoped` is the API default when a document is selected.

### 7.8 Answer generation

- Prompt template: `prompts/answer_v1.txt`. The template version is part of the cache key and the run config.
- The prompt contains the question and the `TOP_K` chunks, labelled `[C1]` to `[Ck]`, each with doc name and page number.
- The model must return JSON only:

  ```json
  {"answer": "string", "citations": ["C1", "C3"], "refused": false}
  ```

- Validation (`answer/validate.py`), in order:
  1. Strip one surrounding Markdown code fence if present, then parse JSON. Fail: `GENERATION_INVALID`.
  2. Required keys present with the right types. Fail: `GENERATION_INVALID`.
  3. If `refused` is false: `citations` is non-empty and every label is one of the labels given. Fail: `CITATION_INVALID`.
  4. If `refused` is true: `answer` is replaced by the fixed text `"I could not find this in the provided filing pages."` and `citations` is emptied.
- On a validation failure, retry once with the same prompt plus a short note stating the error. If the retry fails, return `refused: true` and set `error_code` to the last failure code.
- Citations are mapped from labels to `{"doc_name", "page"}` by our code, never by the model.
- Our code does no arithmetic on the answer in v1 (stretch goal S3).

### 7.9 Numeric check (diagnostic, secondary metric)

- Number extraction from text, applied to gold and predicted answers:
  - Handles `$`, `%`, thousands commas, decimals, a leading minus sign, and parentheses as negative: `(1,234)` becomes `-1234`.
  - Scale words directly after a number: `thousand` multiplies by 1e3; `million`, `mn`, `m` by 1e6; `billion`, `bn`, `b` by 1e9. Case-insensitive.
  - Percentages are kept as their percentage value: `12.5%` becomes `12.5` with a `percent` flag.
- If the gold answer contains no number: `NOT_APPLICABLE`.
- Otherwise the reference is the **first** number in the gold answer. Result is `MATCH` if any predicted number with the same `percent` flag is within relative tolerance 1%: `abs(p - g) <= 0.01 * abs(g)`. If `g == 0`, use absolute tolerance 0.005.
- Unit mismatch is also checked: if the gold answer says "in millions" (or the question asks for USD millions) and the predicted number is 1e6 times larger or smaller, it still counts as `MATCH`.
- Known limitation, to state in the report: this is a heuristic and is used only as a cross-check against the judge.

---

## 8. External integrations

| Integration | Use | Limits | Failure handling |
|---|---|---|---|
| FinanceBench open sample (GitHub `patronus-ai/financebench`, also on Hugging Face `PatronusAI/financebench`) | Questions, metadata, PDFs | 150 questions. Licence: `VERIFY:` (D2.1). Number of distinct documents: `VERIFY:` (D2.1) | Download script checks SHA-256 per file against `data/manifest.json` and stops on mismatch |
| Gemini API | Answer generation and judge | Free tier. Limits per model and per project, viewed in AI Studio. `VERIFY:` RPM, RPD and TPM for the chosen models in S1.4 and record them in VERSIONS.md | Cache every response. Retry on HTTP 429 and 5xx with exponential backoff (3 attempts: 2 s, 4 s, 8 s), then error `LLM_UNAVAILABLE`. Evaluation runner resumes from the last completed question |
| Hugging Face Hub (model download) | Embedding and reranker weights | Public models | Models baked into the Docker image at build time so the running app needs no download |
| Hosting | Public demo | `VERIFY:` (L9.1). Hugging Face docs show CPU Basic (2 vCPU, 16 GB RAM) at no hourly cost, but also state that a Docker Space needs a paid plan. Check the pricing page. Alternatives to check: Google Cloud Run free tier, Render free tier | If no free option fits, raise a Change Request with the cheapest option and its monthly cost |

---

## 9. AI components

**The model may:**
- Answer only from the provided chunks.
- Cite chunk labels it was given.
- Refuse when the chunks do not contain the answer.

**The model may not:**
- Decide which pages are shown as citations (our code maps labels to pages).
- Use knowledge outside the chunks (instructed in the prompt; measured indirectly by the judge).
- Return anything other than the JSON object.

**Prompts are files:** `prompts/answer_v1.txt`, `prompts/judge_v1.txt`. A changed prompt gets a new version number (`answer_v2.txt`); old versions stay for reproducibility.

**Server-side validation:** Section 7.8.

**Fallback:** if the LLM is unavailable, `/api/ask` returns `LLM_UNAVAILABLE` (503) and the UI shows the retrieved evidence from `/api/search` with a message that answer generation is unavailable.

**LLM judge (evaluation only):**
- *Concept refresher: an LLM judge is a model asked to grade an answer against a reference. It is fast but can be biased, so its grades must be checked against a human.*
- Input: question, gold answer, gold evidence text, predicted answer, predicted `refused` flag.
- If `refused` is true, the label is `REFUSED` without calling the judge.
- Otherwise output JSON: `{"label": "CORRECT" | "INCORRECT", "reason": "string"}`.
- Validation and retry as in Section 7.8. A judge failure after retry is stored as `error_code = JUDGE_INVALID` and the question is excluded from accuracy with the count reported.
- Using the same provider for answering and judging may bias grades. This is handled by the human agreement check in Section 12.4, and stated as a limitation in the report.

---

## 10. API contract

Base path `/api`. JSON in and out. Every response carries an `X-Request-ID` header (generated UUID4).

**Error format (all errors)**

```json
{"error": {"code": "INVALID_INPUT", "message": "question must be 1 to 1000 characters", "request_id": "..."}}
```

| Code | HTTP | When |
|---|---|---|
| `INVALID_INPUT` | 400 | Validation failure (length, wrong mode and doc combination, unknown fields) |
| `DOC_NOT_FOUND` | 404 | `doc_name` not in `documents` |
| `RATE_LIMITED` | 429 | Per-IP limit or daily LLM cap reached |
| `LLM_UNAVAILABLE` | 503 | LLM failed after retries |
| `INTERNAL` | 500 | Anything unexpected (logged with request ID, no stack trace in response) |

Note: FastAPI's default validation errors return HTTP 422. Our handler converts them to 400 `INVALID_INPUT` in the format above.

### `GET /api/health`

```json
{"status": "ok", "chunks": 12345, "embedding_model": "<id>", "version": "<git short sha>"}
```
(Numbers are illustrative.)

### `GET /api/documents`

```json
{"documents": [{"doc_name": "3M_2018_10K", "company": "3M", "doc_type": "10k", "doc_period": 2018}]}
```

### `POST /api/search` (retrieval only, no LLM)

Request:
```json
{"question": "string, 1-1000 chars", "doc_name": "optional string", "top_k": 5}
```
- `doc_name` present: `doc_scoped`. Absent: `corpus_wide`. `top_k` from 1 to 20, default 5.

Response:
```json
{"results": [{"rank": 1, "chunk_id": "3M_2018_10K:60:0", "doc_name": "3M_2018_10K",
              "page": 60, "text": "...", "score": 0.83}],
 "mode": "doc_scoped", "latency_ms": 120}
```

### `POST /api/ask`

Request: same as `/api/search` without `top_k` (uses `TOP_K`).

Response:
```json
{"answer": "string",
 "refused": false,
 "citations": [{"label": "C1", "doc_name": "3M_2018_10K", "page": 60}],
 "evidence": [{"label": "C1", "chunk_id": "...", "doc_name": "...", "page": 60, "text": "..."}],
 "mode": "doc_scoped",
 "model_id": "<id>",
 "prompt_version": "answer_v1",
 "latency_ms": 2400,
 "error_code": null}
```

### `GET /api/eval/latest`

Returns the summary JSON of the report marked as published (`eval/reports/published.json` points to it). If nothing is published yet, returns `{"published": false}` with HTTP 200.

---

## 11. Frontend

Single page, `web/index.html` with `app.js` and `styles.css`, served by FastAPI at `/`.

**Components**
- Document selector (dropdown from `/api/documents`, plus "All documents" for `corpus_wide`).
- Question box (textarea, 1000 character limit with counter) and Ask button.
- Answer panel: answer text, refusal notice if refused, citation chips (`3M 2018 10-K, p. 60`).
- Evidence list: each retrieved chunk, expandable, cited ones marked.
- Evaluation tab: headline metrics from `/api/eval/latest` with confidence intervals, a link to the full report on GitHub, and a short "how this was measured" note.
- Footer: dataset source and licence, "answers may be wrong, check the cited page".

**States:** idle; loading (button disabled, spinner with text "Searching filings..."); success; refused; error (message from the API error, plus evidence if available); empty (no documents loaded: "Index not built").

**Accessibility**
- Every input has a visible `<label>`.
- Full keyboard use; visible focus outline.
- Answer region uses `aria-live="polite"`.
- Colour contrast at least WCAG AA (checked with a browser contrast tool in F7.3).
- No information shown by colour alone.

---

## 12. Evaluation and measurement

This is the stand-out part of the project.

### 12.1 Dataset and split

- The 150 open-sample questions.
- Split once, in task D2.5, **before any tuning**: 50 dev, 100 test, stratified by `question_type` (`VERIFY:` field name), random seed 20261101. Saved to `eval/splits/split_v1.json` and to `questions.split`.
- Dev is used for all development and tuning. Test is sealed until E6.9 (rule 11).
- Why 50/100: tuning needs some data, but the final result needs as many questions as possible for a usable confidence interval. Recorded in DECISIONS.md.

### 12.2 Retrieval metrics (no LLM needed)

*Concept refresher: hit@k asks "was at least one correct page in the top k results?". MRR (mean reciprocal rank) rewards putting the first correct page near the top: rank 1 scores 1, rank 2 scores 0.5, and so on.*

- Gold set per question: `{(doc_name, page_number)}` from `evidence`.
- `page_hit@k`: 1 if any of the top-k chunks has a `(doc_name, page_number)` in the gold set, else 0. Reported for k in {1, 5, 10, 20}.
- `page_MRR@20`: reciprocal rank of the first chunk on a gold page within top 20, 0 if none.
- `corpus_wide` only: `doc_hit@k` (any top-k chunk from the gold document).
- Reported as mean over questions with a Wilson 95% interval for hit rates.

### 12.3 Answer metrics

- Primary: **accuracy** = CORRECT / (questions scored). Also **incorrect rate** and **refusal rate**. The incorrect rate matters most for finance: a refusal is safer than a wrong number.
- Secondary: numeric `MATCH` rate on questions where it applies; agreement between numeric check and judge.
- Cost: input and output tokens per question (from the API's usage data), and an estimated cost at the paid price (`VERIFY:` price at report time, with date).
- Latency: p50 and p95 of `/api/ask`-equivalent time, measured on the dev machine, with machine named in the report.

### 12.4 Judge validation

- In task E6.5 the owner hand-labels 40 dev answers (CORRECT or INCORRECT) **without seeing the judge's labels**, in `eval/labels/human_labels_dev.csv`.
- Report percentage agreement and Cohen's kappa between owner and judge.
- *Concept refresher: Cohen's kappa measures agreement after removing the agreement you would expect by chance. 1 is perfect, 0 is chance level.*
- Decision rule (our choice, recorded in DECISIONS.md): if kappa is below 0.6, revise the judge prompt on dev and re-check before any ablation results are trusted.

### 12.5 Statistics

- Wilson score 95% interval for every proportion.
- Comparing two configurations on the same questions: paired bootstrap, 10,000 resamples, seed 20261101, 95% percentile interval for the accuracy difference. A difference whose interval includes 0 is reported as "no clear difference".
- Expected test values for these functions come from hand calculation and from `statsmodels` used as a reference, checked by the owner (rule 7).

### 12.6 Ablations (dev split only)

| Config | Retrieval |
|---|---|
| A | BM25 only |
| B | Dense only |
| C | BM25 + dense, RRF |
| D | C + rerank (expected MVP default) |

Each in `doc_scoped` and `corpus_wide`. Retrieval metrics for all; answer metrics for the best two plus A as a baseline (to save API quota). The final configuration is frozen in DECISIONS.md before E6.9.

### 12.7 Reports

- Path: `eval/reports/<YYYY-MM-DD>_<run_name>.md` and `.json`.
- Each report contains: run ID, date, git commit, split, full config, dataset version (manifest hash), machine, all metrics with intervals, counts of errors and exclusions, and a failure breakdown.
- Failure taxonomy (E6.10), manually assigned on dev failures: `RETRIEVAL_MISS`, `WRONG_NUMBER`, `WRONG_PERIOD_OR_ENTITY`, `CALCULATION_ERROR`, `FALSE_REFUSAL`, `JUDGE_ERROR`, `OTHER`.
- The README quotes numbers only from reports, with a link.

---

## 13. Non-functional

**Security**
- Secrets only in environment variables. `.env` is git-ignored. CI uses GitHub Actions secrets only if a job needs the LLM (unit tests never do: they use `FakeClient`).
- Input limits: question 1 to 1000 characters; request body max 10 KB.
- Retrieved text is inserted into the prompt as data. The answer prompt tells the model to ignore instructions inside chunks. The risk of prompt injection from filings is low (public SEC documents) but is noted in the report.
- No stack traces in API responses.
- `pip-audit` (or equivalent, `VERIFY:` in T8.3) runs on dependencies before deployment.

**Cost guards**
- LLM cache (Section 6).
- Per-IP rate limit on `/api/ask`: `RATE_LIMIT_PER_MIN` (default 5), in-memory token bucket.
- Global daily cap on live LLM calls: `DAILY_LLM_CALL_CAP` (default 200). Above it, `/api/ask` returns `RATE_LIMITED` and the UI suggests `/api/search` results instead.
- Evaluation runner prints the planned number of LLM calls and asks for confirmation (`--yes` to skip) before starting.

**Observability**
- Structured JSON logs to stdout: request ID, endpoint, mode, latency, cache hit, error code. Never the API key.
- `/api/health` for uptime checks.

**Performance**
- No promises. Latency and memory are measured and reported (E6.7, L9.3). Peak RAM of the API process is measured in L9.3 and must fit the chosen host.

---

## 14. Repository layout

```
financebench-rag/
  CLAUDE.md                  # this spec
  AGENTS.md                  # copy of this spec (optional)
  ROADMAP.md
  README.md
  pyproject.toml
  uv.lock
  Dockerfile
  .dockerignore
  .env.example
  .gitignore
  .github/workflows/ci.yml
  docs/
    DECISIONS.md
    VERSIONS.md
    SESSION_LOG.md
  data/
    manifest.json            # committed: file list, URLs, SHA-256
    raw/                     # ignored: downloaded JSONL and PDFs
    processed/               # ignored: SQLite DB, .npy embeddings
  scripts/
    download_data.py
  prompts/
    answer_v1.txt
    judge_v1.txt
  src/finrag/
    config.py  db.py
    ingest/  retrieval/  llm/  answer/  eval/  api/
  web/
    index.html  app.js  styles.css
  eval/
    splits/split_v1.json
    labels/human_labels_dev.csv
    reports/
  notebooks/                 # optional, Colab batch jobs only
  tests/
    unit/  integration/  fixtures/
```

---

## 15. Definition of Done

- [ ] All MVP features F1 to F13 work as specified.
- [ ] `uv run ruff check .` and `uv run pytest` pass locally and in CI.
- [ ] Every calculation module (fusion, retrieval metrics, numeric check, statistics) has tests with independently checked expected values.
- [ ] `docs/VERSIONS.md` is complete; no `VERIFY:` items remain open in this spec.
- [ ] Dataset licence confirmed and the repo follows it (manifest plus download script).
- [ ] Judge validated against 40 human labels, with kappa reported.
- [ ] Ablation report on dev and exactly one final report on test, both in `eval/reports/`.
- [ ] Failure taxonomy completed on dev failures.
- [ ] Docker image builds and runs locally with one command.
- [ ] Public demo live, with rate limit and daily cap working.
- [ ] README with architecture, how to run, measured results (linked), limitations.
- [ ] Demo recording (2 to 3 minutes).
- [ ] CV bullets using only measured numbers, each traced to a report.
- [ ] Owner can explain every item in Section 16 and every module without notes.

---

## 16. Design decisions to explain in interviews

| Decision | Reason | Trade-off |
|---|---|---|
| No LangChain or LlamaIndex | Every step is visible and explainable; fewer moving parts and version churn | More code to write; less "framework" keyword on the CV |
| SQLite and NumPy instead of a vector database | Corpus is small; brute force is exact and simple | Would not scale to millions of chunks without FAISS or a vector DB |
| Hybrid retrieval with RRF | BM25 catches exact terms and numbers ("FY2018", "capital expenditure"); embeddings catch paraphrases; RRF needs no score calibration | Two indexes to build; more latency |
| Cross-encoder reranker on top 20 only | Better precision where it matters, affordable on CPU | Extra latency per query |
| Chunks never cross pages | Citations are exact pages, and retrieval can be scored against gold pages | A table split across two pages may be cut |
| Model returns labels, code maps to pages | The model cannot invent a page number | Slightly more complex prompt and validation |
| Refusal is a first-class outcome | In finance a wrong number is worse than no answer; incorrect and refused are reported separately | Lower headline accuracy if the model refuses often |
| Dev/test split locked before tuning | Prevents overfitting to 150 questions | Fewer questions for tuning and for the final number |
| Wilson intervals and paired bootstrap | 100 test questions give wide intervals; differences must be shown to be real | More complex reporting |
| LLM judge validated by human labels | Judges can be biased, especially the same provider grading itself | 40 manual labels of effort |
| Free-tier API behind an interface with a cache | Near-zero cost; swappable provider; repeatable runs | Free-tier limits slow evaluation; data may be used by the provider (acceptable for public data) |
| No Kafka or Kubernetes | One service, fixed corpus; they would add complexity without a need | Not showcased; Docker plus CI shows deployment skills honestly |

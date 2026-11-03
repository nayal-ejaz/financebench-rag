# VERSIONS.md

Filled in during task S1.2 (and S1.4, C3.2, C3.4, T8.3). Nothing in this file is guessed. Every row needs a source and the date it was checked.
Version changes later go through a Change Request (`/change`).

## Language and tools

| Item | Version | Licence | Source checked | Date checked |
|---|---|---|---|---|
| Python | Python 3.12.16 | PSF | | |
| uv | | | | |
| Git | | | | |
| Docker | | | | |


## Runtime libraries

| Library | Version | Licence | Source checked | Date checked |
|---|---|---|---|---|
| fastapi | | | | |
| uvicorn | | | | |
| pydantic | 2.14.2 | MIT | https://pypi.org/project/pydantic/ | 2026-11-03 |
| pydantic-settings | 2.16.2 | MIT | https://pypi.org/project/pydantic-settings/ | 2026-11-03 |
| pypdf | | | | |
| rank-bm25 | | | | |
| numpy | | | | |
| sentence-transformers | | | | |
| torch (CPU build) | | | | |
| google-genai (Gemini SDK, `VERIFY:` package name) | | | | |

## Development libraries

| Library | Version | Licence | Source checked | Date checked |
|---|---|---|---|---|
| pytest | 9.2.0 | MIT | https://pypi.org/project/pytest/ | 2026-11-03 |
| ruff | 0.17.3 | MIT | https://pypi.org/project/ruff/ | 2026-11-03 |
| statsmodels (reference values only) | | | | |
| pytest-cov | | | | |
| pip-audit (or alternative) | | | | |

## CI actions

| Action | Version | Licence | Source checked | Date checked |
|---|---|---|---|---|
| actions/checkout | v6 | MIT | https://github.com/actions/checkout/releases | 2026-11-03 |
| astral-sh/setup-uv | v8.1.0 | VERIFY | https://github.com/astral-sh/setup-uv/releases | 2026-11-03 |

## Models

| Use | Model ID | Licence | Size | Query prefix (if any) | Source | Date checked |
|---|---|---|---|---|---|---|
| Embeddings | | | | | | |
| Reranker | | | | n/a | | |
| Answer LLM | gemini-3.5-flash-lite | Provider terms | n/a | n/a | https://ai.google.dev/pricing (ID); AI Studio rate-limit page (availability) | 2026-11-03 |
| Judge LLM | gemini-3.1-flash-lite | Provider terms | n/a | n/a | https://ai.google.dev/pricing (ID); AI Studio rate-limit page (availability) | 2026-11-03 |

## Recorded defaults and limits

| Item | Value | Source | Date checked |
|---|---|---|---|
| rank-bm25 `BM25Okapi` default k1 | | | |
| rank-bm25 `BM25Okapi` default b | | | |
| Gemini answer model free tier (gemini-3.5-flash-lite): RPM / RPD / TPM | 15 / 500 / 250K | AI Studio rate-limit page, owner's project | 2026-11-03 |
| Gemini judge model free tier (gemini-3.1-flash-lite): RPM / RPD / TPM | 15 / 500 / 250K | AI Studio rate-limit page, owner's project | 2026-11-03 |
| Gemini paid price per 1M input / output tokens, gemini-3.5-flash-lite (text) | $0.30 / $2.50 | https://ai.google.dev/pricing | 2026-11-03 |
| Gemini paid price per 1M input / output tokens, gemini-3.1-flash-lite (text) | $0.25 / $1.50 | https://ai.google.dev/pricing | 2026-11-03 |

## Dataset

| Item | Value | Source | Date checked |
|---|---|---|---|
| FinanceBench repo commit used | | | |
| FinanceBench licence | | | |
| Number of questions | | | |
| Number of distinct documents | | | |
| Evidence page numbering (0- or 1-based) | | | |

# SESSION_LOG.md

One entry per work session. Newest at the bottom. Paste the entry from the end-of-task block.

Template:

```
## <date> <task IDs>
- Did: ...
- Verified by: ...
- Problems and fixes: ...
- Open questions: ...
- Next: ...
```

---

## 2026-11-01 Planning
- Did: Agreed the proposal. Created PROJECT_SPEC.md, ROADMAP.md, DECISIONS.md, VERSIONS.md, SESSION_LOG.md, .env.example, .gitignore.
- Verified by: Owner review of the documents.
- Problems and fixes: Laptop has no CUDA GPU and high idle RAM use; chose CPU-first design and small models.
- Open questions: FinanceBench licence; free hosting for a Docker app; Gemini free-tier limits for the chosen models.
- Next: R0.1 Install the toolchain.



## 2026-11-01 R0.1
- Did: Installed uv 0.13.6 with the standalone installer; confirmed Git 2.55.0 and VS Code; uv fetched Python 3.12.16; installed the VS Code Python extension.
- Verified by: `uv --version`, `git --version` and `uv run --python 3.12 python --version` in PowerShell.
- Problems and fixes: uv not found at first because the installer had not run; ran it and uv worked. The Python extension did not show by name in the VS Code search, so I installed it with `code --install-extension ms-python.python`.
- Open questions: none
- Next: R0.2 Python project basics kata


TASK: R0.2 Python project basics kata
STATUS: needs my check
FILES CHANGED (scratch project r0-kata): text.py, test_text.py,
  pyproject.toml (stripped), .gitignore (only if __pycache__ appears)
HOW TO VERIFY: uv run pytest -> 4 passed; uv run ruff check . -> clean
DECISIONS MADE: Rule 12 "stripped down first" added. Flat layout, no
  build-system, no src/ until a real need appears.
SPEC OR ROADMAP UPDATES: Add rule 12 to CLAUDE.md. Roadmap R0.2: src/
  layout deferred under rule 12.
SESSION LOG ENTRY:
  ## 2026-11-01 R0.2
  - Did: Scratch project with uv; stripped to minimum; slugify + 4 tests.
  - Verified by: pytest 4 passed, ruff clean.
  - Problems and fixes: kata nested in main project (moved out);
    project.version required (used dynamic); trailing hyphen (strip
    after re.sub); strip() takes a character set, not a regex.
  - Open questions: none
  - Next: R0.3 or skip to S1
SUGGESTED COMMIT: R0.2: slugify kata with tests
NEXT TASK: R0.3 FastAPI kata (or skip to S1)



TASK: R0.3 FastAPI kata
STATUS: done once ruff and pytest are clean
FILES CHANGED (scratch project r0-kata): main.py, test_main.py,
  pyproject.toml (fastapi, uvicorn, httpx2 added)
HOW TO VERIFY: uv run pytest -> 5 passed; uv run ruff check . -> clean;
  /docs shows "message": "string" under GET /hello -> 200
DECISIONS MADE: R0.4 skipped, covered by S1.1 and S1.3. No ruff format
  on save (owner prefers aligned inline comments). Learning notes and
  old code versions go in notes/ or LEARNING.md in the real repo, not
  in code files.
SPEC OR ROADMAP UPDATES: Roadmap: R0.4 merged into S1.1 and S1.3.
SESSION LOG ENTRY:
  ## 2026-11-02 R0.3
  - Did: GET /hello with query validation, Pydantic response model,
    TestClient test.
  - Verified by: browser, /docs, pytest 5 passed, ruff clean.
  - Problems and fixes: SyntaxError from a decorator with no function
    (saved too early); httpx2 installed with global pip instead of
    uv add --dev; ruff I001 on import-line comments.
  - Open questions: none
  - Next: S1.1 Create the repo skeleton
SUGGESTED COMMIT: none (throwaway kata)
NEXT TASK: S1.1 Create the repo skeleton




TASK: S1.3 CI and settings
STATUS: done (PR #1 merged, CI green)
FILES CHANGED: src/finrag/config.py, tests/test_config.py,
  .github/workflows/ci.yml, pyproject.toml, uv.lock, docs/VERSIONS.md
HOW TO VERIFY: uv run pytest -> 2 passed; uv run ruff check . -> clean;
  PR #1 shows green checks
DECISIONS MADE:
  - config.py holds only CHUNK_WORDS and CHUNK_OVERLAP; other variables
    are added in the task that first reads them (rule 12)
  - pytest finds src/ via [tool.pytest.ini_options] pythonpath; making
    finrag an installable package is deferred until something outside
    pytest imports it (expected in C3.1)
  - setup-uv pinned to a full tag (v8.1.0): v8 has no moving major tag
  - Owner chose to have the AI write ci.yml (plumbing, not RAG learning)
SPEC OR ROADMAP UPDATES: Tick S1.3. Tick R0.4 (covered by S1.1 and S1.3).
  S1.3 note: config reads 2 of the .env.example variables, not all
  (rule 12).
SESSION LOG ENTRY:
  ## 2026-11-03 S1.3
  - Did: Branch, pydantic-settings config with chunk defaults and
    ge=0 validation, two tests, minimal GitHub Actions CI, first PR.
  - Verified by: pytest 2 passed, ruff clean, PR #1 green, merged.
  - Problems and fixes: test functions named check_* not collected
    (renamed test_*); parameters treated as fixtures (removed); ran
    pytest from src/ (run from root); ModuleNotFoundError finrag
    (pythonpath = ["src"]); -1 accepted (Field(ge=0)); first push
    needed -u. S1.2's pyproject.toml, uv.lock and .python-version
    were first committed here, not in S1.2.
  - Open questions: trunk-based or branch per task from S1.4 on.
  - Next: S1.4 Gemini API access
SUGGESTED COMMIT: docs: log S1.3
NEXT TASK: S1.4 Gemini API access


## 2026-11-03 S1.4
- Did: Created a Gemini API key in AI Studio, stored in .env only. Read the free-tier limits from the AI Studio rate-limit page and chose answer and judge models. Recorded model IDs, limits and paid prices in VERSIONS.md. Added rules 12 and 13 to Section 0 of CLAUDE.md and PROJECT_SPEC.md.
- Verified by: `git check-ignore -v .env` shows .env ignored by .gitignore; `git grep -E "AIza[0-9A-Za-z_-]{35}"` returns nothing.
- Problems and fixes: `git grep -i "AIza"` matched the roadmap's own instruction text (switched to the full key pattern); the rate-limit table first showed only one row ("See more" expands it).
- Open questions: model ID strings came from the pricing page, not AI Studio "Get code"; confirm in A5.1 when code first calls the model. Line-ending-only changes in 8 files on main still to be discarded or committed. Trunk-based or branch per task still open.
- Next: D2.1 Licence check, manifest and download script

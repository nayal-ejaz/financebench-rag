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





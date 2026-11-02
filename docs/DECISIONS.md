# DECISIONS.md

One row per decision. Newest at the bottom. Link the task ID that made or used the decision.

| Date | Decision | Reason | Alternatives considered | Task |
|---|---|---|---|---|
| 2026-11-01 | Develop on the laptop CPU; use Colab free T4 only for batch jobs measured too slow locally | Radeon 680M has no CUDA support; most of the project needs no GPU | Colab Pro; paid cloud GPU | Planning |
| 2026-11-01 | Gemini API free tier behind an `LLMClient` interface, with a response cache | Near-zero cost; swappable; repeatable evaluation runs | Paid OpenAI or Anthropic API; local open-weights model | Planning |
| 2026-11-01 | No LangChain or LlamaIndex | Every step must be explainable in interviews; fewer dependencies | LangChain; LlamaIndex | Planning |
| 2026-11-01 | SQLite plus NumPy brute-force vectors | Small corpus; exact search; simple | FAISS; Chroma; Qdrant | Planning |
| 2026-11-01 | pypdf for text extraction | Permissive licence (to confirm in S1.2) | PyMuPDF (AGPL, to confirm); pdfplumber | Planning |
| 2026-11-01 | Kafka and Kubernetes are non-goals | One service, fixed corpus; no need | Adding them for CV keywords | Planning |
| 2026-11-01 | Dev/test split 50/100, stratified, seed 20261101, created before tuning | Avoid overfitting to 150 questions; keep the final set as large as possible | 75/75; cross-validation | Planning (applied in D2.5) |
| 2026-11-01 | Judge must reach Cohen's kappa of at least 0.6 against 40 human labels before ablations are trusted | Same-provider judging may be biased | No validation; a second paid judge model | Planning (applied in E6.5) |
| 2026-11-02 | Python 3.12 | Already installed via uv; every library in the stack ships builds for it; security fixes until Oct 2028 | Python 3.14 (newer, extra download); 3.15 (too new, may lack PyTorch wheels on Windows) | S1.2 |
| 2026-11-02 | pypdf licence confirmed BSD; PyMuPDF confirmed AGPL or commercial, so rejected | Closes the "to confirm" in the Planning row above | pdfplumber | S1.2 |
| 2026-11-02 | Pin each library when a task first adds it, not all in S1.2 | Rule 12: add only what is needed now | Pin all of spec Section 4 up front, as the roadmap says | S1.2 |
| | | | | |

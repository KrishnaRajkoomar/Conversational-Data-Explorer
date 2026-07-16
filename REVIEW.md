# Code Review — Conversational Data Explorer

## Summary

Clean separation of concerns. Guardrails run before every query execution — the critical architectural decision is correct. 26 passing tests cover all denial categories plus edge cases. Frontend handles error states gracefully.

## What's Good

- **Guardrails-first design**: SQL validated before any execution, layered checks (keywords, patterns, comments, LIMIT injection).
- **Defence in depth**: SQLAlchemy `text()` for parameterized queries, no string concatenation.
- **Thorough test coverage**: 26 tests covering all denied keywords, stacked statements, comments, CTEs, string literal preservation, and system table access.
- **XSS protection**: `escapeHtml()` via `textContent` in the frontend.
- **Frontend polish**: Collapsible SQL, sortable tables, Chart.js bar charts, read-only badge, example questions.
- **API key security**: `.env` with `.gitignore`, `.env.example` committed.

## Issues Found & Fixed

| # | Issue | Severity | Fix |
|---|-------|----------|-----|
| C1 | CORS `allow_credentials=True` incompatible with `allow_origins=["*"]` | Critical | Removed `allow_credentials` |
| C2 | `/seed` exposed as `GET` — browser prefetch could wipe DB | Critical | Changed to `POST` |
| C3 | Missing `RENAME`, `VACUUM`, `REINDEX`, `ANALYZE` in denied keywords | Critical | Added to `DENIED_KEYWORDS` |
| W1 | `WITH` (CTE) queries incorrectly rejected | Warning | Added `WITH` as valid starting keyword |
| W2 | Comment stripping could corrupt `--` inside string literals | Warning | Rewrote `_strip_comments()` with string-aware parser |
| W4 | No exception handling around Gemini API calls | Warning | Added try/except with user-facing error messages |
| W5 | Unbounded in-memory history | Warning | Capped at 100 entries |
| W6 | Future date in seed data (off-by-one) | Warning | Fixed `timedelta(days=max(i * 2, 1))` |
| W8 | Frontend doesn't handle non-2xx HTTP responses | Warning | Added fallback error handling |
| W9 | Port 8000 hardcoded in error message | Warning | Generalized message |
| W10 | Unused `create_engine` import in `models.py` | Warning | Removed |
| S3 | Empty chart canvas when second column is non-numeric | Suggestion | Clears canvas container |

## Remaining Known Limitations

- **LIMIT bypass via subquery**: If the SQL contains `LIMIT` in a subquery or string literal, no outer LIMIT is added. Acceptable for a dev tool.
- **No query execution timeout**: A slow query can hang the server thread. Acceptable for development.
- **SQLite only**: No PostgreSQL adapter yet. Schema introspection is engine-agnostic; only the connection string needs to change.

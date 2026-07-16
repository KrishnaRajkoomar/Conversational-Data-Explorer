# AGENTS.md — Conversational Data Explorer

## Commands

```powershell
# Setup
python -m venv venv; ./venv/Scripts/activate
pip install -r requirements.txt

# Run
uvicorn backend.main:app --reload

# Tests
pytest backend/test_guardrails.py -v

# Lint (if added later)
ruff check .
```

## Architecture

```
backend/
├── main.py           # FastAPI app, routes: /health, /schema, /ask, /history, /seed
├── db.py             # SQLAlchemy engine, session, seed data
├── models.py         # ORM models (customers, orders, payments)
├── nl2sql.py         # Gemini prompt → SQL
├── guardrails.py     # SQL validation (read-only checks) — THE HEART
├── ai.py             # Gemini API client
└── test_guardrails.py

frontend/
└── index.html        # Chat UI, vanilla JS + Chart.js CDN
```

## Critical rules

- **Guardrails run after model generates SQL, before execution.** Every `POST /ask` must pass through `guardrails.py`.
- **Reject**: `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `CREATE`, `TRUNCATE`, `REPLACE`, `PRAGMA`, `ATTACH`, comments (`--`, `/* */`), multiple statements (`;`).
- **Auto-inject** `LIMIT 100` if no `LIMIT` present.
- **Never build SQL by string gluing.** Use ORM or parameterized queries.
- **API key** in `.env` (`GEMINI_API_KEY=...`). `.env` is gitignored. Commit `.env.example` only.

## Build order (do not skip)

1. Scaffold → 2. DB + seed → 3. Schema endpoint → 4. NL→SQL (print only) → 5. Guardrails + tests (must pass) → 6. Wire `/ask` → 7. History → 8. Frontend → 9. Review

## Test prerequisites

- `test_guardrails.py` must run without a running server or Gemini key — it validates `guardrails.py` logic directly.
- Adversarial cases: `"delete all users"`, `"drop table orders"`, stacked statements, comment injection. All must be rejected.

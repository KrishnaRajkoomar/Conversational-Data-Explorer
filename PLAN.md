# Conversational Data Explorer — Plan

## Overview
A chat interface for a database. Users type plain-English questions, the app generates safe SQL, runs it, and returns results with the SQL shown.

## Architecture

```
conversational-data-explorer/
├── backend/
│   ├── main.py          # FastAPI app, routes, CORS
│   ├── db.py            # SQLAlchemy engine, models, schema, seed data
│   ├── nl2sql.py        # Sends schema + question to Gemini, gets SQL back
│   ├── guardrails.py    # Validates SQL is safe (read-only SELECT)
│   ├── ai.py            # Gemini API client abstraction
│   ├── models.py        # SQLAlchemy ORM models
│   ├── requirements.txt
│   ├── .env             # (gitignored) API keys
│   ├── .env.example     # (committed) template
│   └── test_guardrails.py
├── frontend/
│   └── index.html       # Single-page chat UI (vanilla JS + Chart.js CDN)
├── .gitignore
├── PLAN.md              # This file
├── PROMPTS.md           # Prompt tracking
├── REVIEW.md            # Code review findings
└── README.md            # Project documentation
```

## Database Schema (SQLite — `data.db`)

### `customers`
| Column    | Type    |
|-----------|---------|
| id        | INTEGER PK |
| name      | TEXT NOT NULL |
| email     | TEXT NOT NULL UNIQUE |
| region    | TEXT NOT NULL |
| created_at| DATETIME DEFAULT CURRENT_TIMESTAMP |

### `orders`
| Column      | Type    |
|-------------|---------|
| id          | INTEGER PK |
| customer_id | INTEGER FK → customers.id |
| product     | TEXT NOT NULL |
| amount      | REAL NOT NULL |
| status      | TEXT NOT NULL (pending/shipped/delivered/cancelled) |
| order_date  | DATETIME DEFAULT CURRENT_TIMESTAMP |

### `payments`
| Column      | Type    |
|-------------|---------|
| id          | INTEGER PK |
| order_id    | INTEGER FK → orders.id |
| amount      | REAL NOT NULL |
| paid_at     | DATETIME |
| method      | TEXT NOT NULL (credit_card/bank_transfer/cash) |

Seed data: ~20 customers across 4 regions, ~50 orders with varied statuses, ~30 payments.

## API Endpoints

| Method | Path         | Description |
|--------|--------------|-------------|
| GET    | /health      | Health check |
| GET    | /schema      | Introspected DB schema as text |
| POST   | /ask         | Ask a question → { answer, sql, rows, chart_type? } |
| GET    | /history     | Previous Q&A in session |
| GET    | /seed        | (re)load seed data on demand |

## Safety Model (The Heart of the Project)

Guardrails run **after** the model generates SQL and **before** it executes. Layered checks:

1. **Single statement only** — reject if `;` appears (except trailing).
2. **Must start with SELECT** — reject INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, PRAGMA, ATTACH, etc.
3. **No stacked statements** — reject `;` followed by another statement.
4. **No SQL comments** — strip or reject `--` and `/* */`.
5. **Limit rows** — inject `LIMIT 100` if no `LIMIT` clause present.
6. **No dangerous keywords** — block `sqlite_master`, `pragma`, `attach`, `detach`.
7. **Defence in depth** — DB user (SQLite itself is file-level, but we add ORM parameterization).

### What a question is allowed to make the database do:
- **Read only**, via a single `SELECT` statement.
- **Nothing else.** No writes, no schema changes, no attach/detach.

### What is rejected:
- `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `CREATE`, `TRUNCATE`, `REPLACE`
- Multiple statements separated by `;`
- SQL comments (to hide statements)
- Any query without a LIMIT (auto-injected if missing)

### Tests (adversarial):
- `"delete all users"` — rejected
- `"drop table orders"` — rejected
- `"SELECT * FROM customers; DROP TABLE orders;"` — rejected
- Valid query with `--` comment — rejected/stripped
- `"SELECT * FROM customers"` without LIMIT — LIMIT 100 added

## Prompt Design (Gemini)

**System prompt (compressed):**
```
You are a SQL generator for SQLite. Given a schema and a question,
return exactly one read-only SELECT statement. No explanation.
No markdown. No comments. Do not use INSERT, UPDATE, DELETE, DROP,
ALTER, CREATE, or any writing statement. Always respect the schema.
If the user asks to modify data, return "-- I cannot do that".
```

**Schema format sent to model:**
```
Table: customers
  id (INTEGER) PK
  name (TEXT) NOT NULL
  email (TEXT) NOT NULL UNIQUE
  region (TEXT) NOT NULL
  created_at (DATETIME)

Table: orders
  id (INTEGER) PK → customers.id
  ...
```

## Build Order

1. ✅ **Plan** — PLAN.md (this file)
2. **Scaffold** — Virtual env, `requirements.txt`, `.env`, `.gitignore`, `.env.example`, `GET /health`
3. **Database** — SQLAlchemy models, seed data, `GET /seed`
4. **Schema endpoint** — `GET /schema` via `inspect()`
5. **NL → SQL** — Wire Gemini, basic prompt, print SQL (don't run yet)
6. **Guardrails** — `guardrails.py` + `test_guardrails.py` (adversarial tests pass)
7. **End-to-end /ask** — Wire guardrails → execute → return {answer, sql, rows}
8. **History** — `GET /history`
9. **Frontend** — `index.html` with chat, collapsible SQL, table, Chart.js, "read-only" badge
10. **Review & polish** — REVIEW.md, README, final fixes

## Stretch Goals (if time remains)
- Conversation memory (follow-up questions)
- Show which tables a query touched
- CSV export from UI

## Demo Questions
- "How many customers do we have in each region?"
- "What are the top 5 orders by amount?"
- "Show me all payments made in January 2025"
- "Which customers have overdue payments?"
- "How much revenue did we get in each region?"

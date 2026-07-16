# Conversational Data Explorer

Chat with your database in plain English. Type a question, get an answer with the SQL shown, results in a table, and charts for aggregates.

## Safety Model

The **read-only guardrails** are the heart of this project. Every query passes through layered checks **before** execution:

1. **Single statement only** — rejects stacked statements (`;`)
2. **Must start with `SELECT` or `WITH`** — blocks `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `CREATE`, and 12 other forbidden keywords
3. **No SQL comments** — strips `--` and `/* */` (string-literal aware, so `'%--test%'` is preserved)
4. **Auto LIMIT** — injects `LIMIT 100` if none present
5. **No system tables** — blocks `sqlite_master`, `sqlite_sequence`, `sqlite_stat*`, `pragma_*`
6. **Execution safety** — uses SQLAlchemy `text()` (parameterized), never string concatenation

All guardrail logic lives in `backend/guardrails.py` and is proven by 26 tests in `backend/test_guardrails.py`.

## Quick Start

```bash
# 1. Set up environment
python -m venv venv
venv\Scripts\activate    # Windows
pip install -r backend\requirements.txt

# 2. Add your Gemini API key
echo GEMINI_API_KEY=your_key_here > .env

# 3. Run the server
uvicorn backend.main:app --reload

# 4. Open http://localhost:8000
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/schema` | Database schema (introspected) |
| POST | `/ask` | Ask a question `{"question": "..."}` |
| GET | `/history` | Session Q&A history |
| POST | `/seed` | Reload seed data |

## Example Questions

- *"How many customers do we have in each region?"*
- *"What are the top 5 orders by amount?"*
- *"How many orders are pending vs delivered?"*
- *"What is the total revenue?"*

## Tech Stack

- **Backend**: Python 3.14+, FastAPI, SQLAlchemy, SQLite
- **AI**: Google Gemini 2.0 Flash (`google-genai`)
- **Frontend**: Vanilla JS, Chart.js, HTML/CSS
- **Tests**: pytest (26 tests, no server or API key needed)

## Test

Guardrails tests run offline (no server, no API key):

```bash
pytest backend/test_guardrails.py -v
```

## Project Structure

```
backend/
├── main.py          # FastAPI app, routes
├── db.py            # SQLAlchemy engine, seed data, schema introspection
├── models.py        # ORM models (customers, orders, payments)
├── nl2sql.py        # Gemini prompt → SQL
├── guardrails.py    # SQL validation — THE HEART
├── ai.py            # Gemini API client
└── test_guardrails.py
frontend/
└── index.html       # Chat UI
```

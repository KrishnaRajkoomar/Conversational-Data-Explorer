import os
import logging
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import text
from .db import init_db, seed_data, get_schema_text, engine
from .models import Base
from .nl2sql import question_to_sql
from .guardrails import validate_sql

logger = logging.getLogger(__name__)
app = FastAPI(title="Conversational Data Explorer")
history = []
MAX_HISTORY = 100

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str
    sql: str
    columns: list
    rows: list
    ok: bool
    error: str = ""

@app.on_event("startup")
def startup():
    init_db()
    seed_data()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/schema")
def schema():
    return {"schema": get_schema_text()}

@app.post("/seed")
def seed():
    Base.metadata.drop_all(engine)
    init_db()
    seed_data()
    return {"status": "seeded"}

@app.post("/ask")
def ask(req: AskRequest):
    try:
        raw_sql = question_to_sql(req.question)
    except Exception as e:
        result = {
            "answer": "Failed to generate SQL. Check your API key and try again.",
            "sql": "",
            "columns": [],
            "rows": [],
            "ok": False,
            "error": str(e),
        }
        history.append({"question": req.question, "response": result})
        return result

    ok, msg, safe_sql = validate_sql(raw_sql)

    if not ok:
        result = {
            "answer": msg,
            "sql": raw_sql,
            "columns": [],
            "rows": [],
            "ok": False,
            "error": msg,
        }
        history.append({"question": req.question, "response": result})
        return result

    try:
        with engine.connect() as conn:
            cursor = conn.execute(text(safe_sql))
            columns = list(cursor.keys())
            rows = [list(row) for row in cursor.fetchall()]
    except Exception as e:
        result = {
            "answer": "Error executing SQL.",
            "sql": safe_sql,
            "columns": [],
            "rows": [],
            "ok": False,
            "error": str(e),
        }
        history.append({"question": req.question, "response": result})
        return result

    answer = f"Returned {len(rows)} row(s)."
    if len(rows) == 1 and len(columns) == 1:
        answer = f"The answer is {rows[0][0]}."

    result = {
        "answer": answer,
        "sql": safe_sql,
        "columns": columns,
        "rows": rows,
        "ok": True,
        "error": "",
    }
    history.append({"question": req.question, "response": result})
    if len(history) > MAX_HISTORY:
        history.pop(0)
    return result

@app.get("/history")
def get_history():
    return history

FRONTEND_HTML = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
if os.path.isfile(FRONTEND_HTML):
    with open(FRONTEND_HTML) as f:
        _index_html = f.read()

    @app.get("/")
    def index():
        return Response(content=_index_html, media_type="text/html")

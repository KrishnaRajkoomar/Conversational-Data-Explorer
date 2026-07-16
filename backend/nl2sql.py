from .ai import generate
from .db import get_schema_text

SYSTEM_PROMPT = """You are a SQL generator for SQLite. Given a database schema and a natural language question, return exactly one read-only SELECT statement. No explanation. No markdown formatting. No SQL comments. Do not use INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE, REPLACE, PRAGMA, ATTACH, or any statement that modifies data or schema. If the question asks to modify data or is not answerable with a SELECT, return exactly: -- I cannot answer that

Schema:
{schema}

Question: {question}

SQL:"""


def question_to_sql(question: str) -> str:
    schema = get_schema_text()
    prompt = SYSTEM_PROMPT.format(schema=schema, question=question)
    sql = generate(prompt)
    return sql

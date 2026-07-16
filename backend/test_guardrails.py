from backend.guardrails import validate_sql, _strip_comments


def test_strip_comment_in_string():
    result = _strip_comments("SELECT * FROM customers WHERE name LIKE '%--test%'")
    assert result == "SELECT * FROM customers WHERE name LIKE '%--test%'"


def test_strip_block_comment():
    result = _strip_comments("SELECT * FROM customers /* where id = 1 */ LIMIT 5")
    assert "LIMIT 5" in result
    assert "/*" not in result


def test_valid_select():
    ok, msg, sql = validate_sql("SELECT * FROM customers")
    assert ok, f"Expected valid, got: {msg}"
    assert "LIMIT 100" in sql


def test_valid_select_with_limit():
    ok, msg, sql = validate_sql("SELECT * FROM customers LIMIT 5")
    assert ok
    assert "LIMIT 5" in sql


def test_delete_rejected():
    ok, msg, _ = validate_sql("DELETE FROM customers")
    assert not ok
    assert "forbidden keyword" in msg.lower() or "statement must start with select" in msg.lower()


def test_drop_rejected():
    ok, msg, _ = validate_sql("DROP TABLE orders")
    assert not ok


def test_insert_rejected():
    ok, msg, _ = validate_sql("INSERT INTO customers VALUES (1, 'a', 'b', 'c')")
    assert not ok


def test_update_rejected():
    ok, msg, _ = validate_sql("UPDATE customers SET name='x' WHERE id=1")
    assert not ok


def test_alter_rejected():
    ok, msg, _ = validate_sql("ALTER TABLE customers ADD COLUMN foo TEXT")
    assert not ok


def test_create_rejected():
    ok, msg, _ = validate_sql("CREATE TABLE foo (id INT)")
    assert not ok


def test_truncate_rejected():
    ok, msg, _ = validate_sql("TRUNCATE TABLE customers")
    assert not ok


def test_replace_rejected():
    ok, msg, _ = validate_sql("REPLACE INTO customers VALUES (1, 'a', 'b', 'c')")
    assert not ok


def test_pragma_rejected():
    ok, msg, _ = validate_sql("PRAGMA table_info(customers)")
    assert not ok


def test_attach_rejected():
    ok, msg, _ = validate_sql("ATTACH DATABASE 'foo.db' AS foo")
    assert not ok


def test_stacked_statements_rejected():
    ok, msg, _ = validate_sql("SELECT * FROM customers; DROP TABLE orders;")
    assert not ok


def test_comment_single_line_stripped():
    ok, msg, sql = validate_sql("SELECT * FROM customers -- drop table")
    assert ok, f"Expected valid after stripping comment, got: {msg}"
    assert "LIMIT 100" in sql


def test_comment_block_rejected():
    ok, msg, _ = validate_sql("SELECT * FROM customers /* drop */")
    assert ok, "Block comment should be stripped, not rejected"


def test_empty_sql():
    ok, msg, _ = validate_sql("")
    assert not ok


def test_model_refusal():
    ok, msg, _ = validate_sql("-- I cannot do that")
    assert not ok


def test_sqlite_master_rejected():
    ok, msg, _ = validate_sql("SELECT * FROM sqlite_master")
    assert not ok


def test_with_cte_allowed():
    ok, msg, sql = validate_sql("WITH regional AS (SELECT region, COUNT(*) AS cnt FROM customers GROUP BY region) SELECT * FROM regional")
    assert ok, f"CTE should be allowed, got: {msg}"
    assert "LIMIT 100" in sql


def test_rename_rejected():
    ok, msg, _ = validate_sql("RENAME TABLE customers TO old")
    assert not ok


def test_vacuum_rejected():
    ok, msg, _ = validate_sql("VACUUM")
    assert not ok


def test_reindex_rejected():
    ok, msg, _ = validate_sql("REINDEX")
    assert not ok


def test_analyze_rejected():
    ok, msg, _ = validate_sql("ANALYZE")
    assert not ok


def test_comment_in_string_literal_preserved():
    ok, msg, sql = validate_sql("SELECT * FROM customers WHERE name LIKE '%--test%'")
    assert ok
    assert "LIMIT 100" in sql

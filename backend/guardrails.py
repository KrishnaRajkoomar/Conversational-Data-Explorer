import re

DENIED_KEYWORDS = [
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE",
    "TRUNCATE", "REPLACE", "PRAGMA", "ATTACH", "DETACH",
    "RENAME", "VACUUM", "REINDEX", "ANALYZE",
]

DENIED_PATTERNS = [
    r"SQLITE_MASTER",
    r"SQLITE_TEMP_MASTER",
    r"SQLITE_VERSION",
    r"SQLITE_SEQUENCE",
    r"SQLITE_STAT",
    r"PRAGMA_",
]


def _strip_comments(sql: str) -> str:
    result = []
    i = 0
    in_single = False
    in_double = False
    n = len(sql)
    while i < n:
        ch = sql[i]
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        if not in_single and not in_double:
            if ch == "-" and i + 1 < n and sql[i + 1] == "-":
                end = sql.find("\n", i)
                if end == -1:
                    break
                i = end + 1
                continue
            if ch == "/" and i + 1 < n and sql[i + 1] == "*":
                end = sql.find("*/", i + 2)
                if end == -1:
                    break
                i = end + 2
                continue
        result.append(ch)
        i += 1
    return "".join(result).strip()


def validate_sql(sql: str) -> tuple[bool, str, str]:
    cleaned = sql.strip()

    if not cleaned:
        return False, "Empty or no SQL generated", ""

    if cleaned.upper().startswith("--"):
        return False, "Model refused to answer", cleaned

    cleaned = _strip_comments(cleaned)

    if not cleaned:
        return False, "Empty after stripping comments", sql

    upper = cleaned.upper()

    for kw in DENIED_KEYWORDS:
        if re.search(rf"\b{kw}\b", upper):
            return False, f"Statement contains forbidden keyword: {kw}", cleaned

    for pat in DENIED_PATTERNS:
        if re.search(pat, upper):
            return False, "Statement contains forbidden reference", cleaned

    if not upper.startswith("SELECT") and not upper.startswith("WITH"):
        return False, "Statement must start with SELECT or WITH", cleaned

    if ";" in cleaned.rstrip(";"):
        return False, "Multiple statements detected", cleaned

    cleaned = cleaned.rstrip(";")

    if "LIMIT" not in upper:
        cleaned = cleaned.strip() + " LIMIT 100"

    return True, "", cleaned

import json
import re

from src.lib.config import Config

SQL_WRITE_KEYWORDS = [
    r"\bINSERT\b",
    r"\bUPDATE\b",
    r"\bDELETE\b",
    r"\bDROP\b",
    r"\bCREATE\b",
    r"\bALTER\b",
    r"\bTRUNCATE\b",
    r"\bREPLACE\b",
    r"\bMERGE\b",
]

MONGODB_WRITE_OPERATIONS = [
    "insert_one",
    "insert_many",
    "update_one",
    "update_many",
    "delete_one",
    "delete_many",
    "replace_one",
    "bulk_write",
]

SQL_PATTERN = re.compile("|".join(SQL_WRITE_KEYWORDS), re.IGNORECASE)


class ReadOnlyError(Exception):
    pass


def validate_read_only_query(query: str, config: Config) -> None:
    query_stripped = query.strip()

    print(query_stripped)
    if config.db_provider == "mongo":
        _validate_mongodb_query(query_stripped)
    else:
        _validate_sql_query(query_stripped)


def _validate_mongodb_query(query: str) -> None:
    try:
        parsed = json.loads(query)
        operation = parsed.get("operation", "")

        if operation in MONGODB_WRITE_OPERATIONS:
            raise ReadOnlyError(
                f"READ-ONLY MODE: MongoDB operation '{operation}' is not allowed. "
                f"Only read operations (find, find_one, aggregate, count) are permitted."
            )
    except json.JSONDecodeError:
        pass


def _validate_sql_query(query: str) -> None:
    if SQL_PATTERN.search(query):
        raise ReadOnlyError(
            "READ-ONLY MODE: Write operations (INSERT, UPDATE, DELETE, DROP, CREATE, ALTER, "
            "TRUNCATE, REPLACE, MERGE) are not allowed. Only SELECT, SHOW, DESCRIBE queries are permitted."
        )

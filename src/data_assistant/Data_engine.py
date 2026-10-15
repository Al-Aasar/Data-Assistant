import json
import threading
from decimal import Decimal
from functools import lru_cache
from pathlib import Path

import duckdb

try:
    from data_assistant.analysis_code import load_file
except ImportError:
    from analysis_code import load_file

QUERY_TIMEOUT_S = 10   
MAX_ROWS = 500         
MEMORY_LIMIT = "1GB"


@lru_cache(maxsize=8)
def _load_cached(path: str, kind: str, mtime: float) -> dict:
    """Read the file once; the cache key includes mtime so edits are picked up."""
    return load_file(path, kind)


def _connect(path: str, kind: str) -> duckdb.DuckDBPyConnection:
    """Fresh in-memory connection with every sheet registered as a table.
    Table names = sheet names for Excel, "data" for CSV (same as schema_context)."""
    tables = _load_cached(path, kind, Path(path).stat().st_mtime)
    con = duckdb.connect(":memory:")
    con.execute(f"SET memory_limit='{MEMORY_LIMIT}'")
    for name, df in tables.items():
        con.register(name, df)

    con.execute("SET enable_external_access=false")
    con.execute("SET lock_configuration=true")
    return con


def explain_query(query: str, path: str, kind: str) -> None:
    """Check that the query is valid (tables, columns, types) WITHOUT running it.
    Raises duckdb.Error with a readable message if it is invalid."""
    con = _connect(path, kind)
    try:
        con.execute("EXPLAIN " + query)
    finally:
        con.close()


def run_query(query: str, path: str, kind: str, max_rows: int = MAX_ROWS) -> dict:
    """Run a validated SELECT. Returns {"columns", "rows", "truncated"}.
    Raises on invalid SQL or timeout."""
    con = _connect(path, kind)
    timer = threading.Timer(QUERY_TIMEOUT_S, con.interrupt)
    timer.start()
    try:
        cur = con.execute(query)
        columns = [d[0] for d in cur.description]
        rows = cur.fetchmany(max_rows + 1)
        return {
            "columns": columns,
            "rows": [list(r) for r in rows[:max_rows]],
            "truncated": len(rows) > max_rows,
        }
    finally:
        timer.cancel()
        con.close()


def _json_default(o):
    if isinstance(o, Decimal):
        return float(o)
    return str(o)  


def result_to_text(result: dict) -> str:
    """Turn run_query output into the string stored in state['query_result']."""
    return json.dumps(result, ensure_ascii=False, default=_json_default)
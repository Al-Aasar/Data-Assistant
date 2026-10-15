import asyncio
import io
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Any

# Clean UTF-8 encoding configuration
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from data_assistant.agents.Analysis_Agent import analysis_agent
from data_assistant.Data_engine import explain_query, run_query
from data_assistant.analysis_code import analyze_file
from data_assistant.state import AssistantState

DATASET_CSV = Path(__file__).resolve().parent / "datasets" / "sample_ecommerce.csv"
BENCHMARKS_JSON = Path(__file__).resolve().parent / "datasets" / "text_to_sql_benchmarks.json"


def _generate_deterministic_schema_context() -> str:
    """Creates a structured schema context for offline evaluation."""
    return json.dumps({
        "tables": [
            {
                "table_name": "data",
                "description": "E-commerce order transactions containing customer, product, and revenue details",
                "row_meaning": "One row per order",
                "columns": [
                    {"name": "order_id", "dtype": "object", "semantic_type": "identifier", "role": "key"},
                    {"name": "customer_name", "dtype": "object", "semantic_type": "identifier", "role": "dimension"},
                    {"name": "country", "dtype": "object", "semantic_type": "category", "role": "dimension"},
                    {"name": "category", "dtype": "object", "semantic_type": "category", "role": "dimension"},
                    {"name": "product_name", "dtype": "object", "semantic_type": "category", "role": "dimension"},
                    {"name": "units_sold", "dtype": "int64", "semantic_type": "measure", "role": "measure"},
                    {"name": "unit_price", "dtype": "float64", "semantic_type": "measure", "role": "measure"},
                    {"name": "total_revenue", "dtype": "float64", "semantic_type": "measure", "role": "measure"},
                    {"name": "order_date", "dtype": "object", "semantic_type": "date", "role": "time"},
                    {"name": "status", "dtype": "object", "semantic_type": "category", "role": "dimension"}
                ]
            }
        ]
    })


async def evaluate_text_to_sql(use_mock: bool = False) -> Dict[str, Any]:
    with open(BENCHMARKS_JSON, "r", encoding="utf-8") as f:
        cases = json.load(f)

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    is_mock = use_mock or not api_key

    schema_context = _generate_deterministic_schema_context()
    file_path = str(DATASET_CSV.resolve())

    results = []
    syntax_valid_count = 0
    execution_success_count = 0
    value_match_count = 0
    start_time = time.time()

    for case in cases:
        question = case["question"]
        t0 = time.time()

        if is_mock:
            # Use benchmark ground truth SQL in mock/offline mode to verify pipeline execution
            sql = case["expected_sql"]
            generation_error = None
        else:
            state: AssistantState = {
                "user_query": question,
                "schema_context": schema_context,
                "file_path": file_path,
                "file_kind": "csv",
                "iteration": 0,
                "llm_calls": 0,
            }
            try:
                res = await analysis_agent(state)
                sql = res.get("sql", "").strip()
                generation_error = res.get("error")
            except Exception as e:
                sql = ""
                generation_error = str(e)

        duration = time.time() - t0

        syntax_ok = False
        exec_ok = False
        value_ok = False
        exec_error = None
        query_output = None

        if sql:
            # 1. Safety check
            sql_upper = sql.upper()
            is_readonly = not any(w in sql_upper for w in ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE"])

            # 2. DuckDB syntax EXPLAIN check
            try:
                explain_query(sql, file_path, "csv")
                syntax_ok = is_readonly
            except Exception as e:
                syntax_ok = False
                exec_error = f"Syntax/Explain error: {e}"

            # 3. Execution check
            if syntax_ok:
                try:
                    res = run_query(sql, file_path, "csv")
                    exec_ok = True
                    query_output = res

                    # 4. Value / criteria verification
                    check_type = case.get("check_type")
                    if check_type == "scalar_numeric":
                        actual_val = float(res["rows"][0][0])
                        expected_val = float(case["expected_value"])
                        value_ok = abs(actual_val - expected_val) < 0.01
                    elif check_type == "row_count":
                        value_ok = (len(res["rows"]) == case["expected_row_count"])
                    elif check_type == "min_rows":
                        value_ok = (len(res["rows"]) >= case["min_rows"])
                    else:
                        value_ok = True
                except Exception as e:
                    exec_ok = False
                    exec_error = f"Execution error: {e}"

        if syntax_ok:
            syntax_valid_count += 1
        if exec_ok:
            execution_success_count += 1
        if value_ok:
            value_match_count += 1

        results.append({
            "id": case["id"],
            "question": question,
            "generated_sql": sql,
            "expected_sql": case["expected_sql"],
            "syntax_ok": syntax_ok,
            "exec_ok": exec_ok,
            "value_ok": value_ok,
            "error": generation_error or exec_error,
            "duration_ms": round(duration * 1000, 1),
        })

    total = len(cases)
    total_time = time.time() - start_time

    return {
        "suite": "Text-to-SQL (Analysis Agent) Evaluation",
        "mode": "Mock / Ground-Truth" if is_mock else "Live (Gemini)",
        "total_cases": total,
        "syntax_validity_rate": round((syntax_valid_count / total) * 100, 2),
        "execution_success_rate": round((execution_success_count / total) * 100, 2),
        "value_match_rate": round((value_match_count / total) * 100, 2),
        "total_duration_s": round(total_time, 2),
        "details": results,
    }


def print_sql_report(report: Dict[str, Any]):
    print("\n" + "=" * 75)
    print(f"  {report['suite']} - Mode: {report['mode']}")
    print("=" * 75)
    print(f"Total Test Cases:         {report['total_cases']}")
    print(f"Syntax Validity Rate:     {report['syntax_validity_rate']}%")
    print(f"Execution Success Rate:   {report['execution_success_rate']}%")
    print(f"Value Match Rate:         {report['value_match_rate']}%")
    print(f"Total Duration:           {report['total_duration_s']}s")
    print("-" * 75)
    print(f"{'ID':<8} | {'Syntax':<6} | {'Exec':<6} | {'Value':<6} | Question")
    print("-" * 75)
    for d in report["details"]:
        s_flag = "OK" if d["syntax_ok"] else "ERR"
        e_flag = "OK" if d["exec_ok"] else "ERR"
        v_flag = "OK" if d["value_ok"] else "ERR"
        q_preview = (d["question"][:36] + "..") if len(d["question"]) > 38 else d["question"]
        print(f"{d['id']:<8} | {s_flag:<6} | {e_flag:<6} | {v_flag:<6} | {q_preview}")
    print("=" * 75 + "\n")


if __name__ == "__main__":
    mock_flag = "--mock" in sys.argv
    rep = asyncio.run(evaluate_text_to_sql(use_mock=mock_flag))
    print_sql_report(rep)

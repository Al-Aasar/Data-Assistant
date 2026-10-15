import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from data_assistant.analysis_code import analyze_file
from data_assistant.agents.Knowlage_Agent import knowlage_agent
from data_assistant.state import AssistantState

DATASET_CSV = Path(__file__).resolve().parent / "datasets" / "sample_ecommerce.csv"

EXPECTED_COLUMNS = {
    "order_id",
    "customer_name",
    "country",
    "category",
    "product_name",
    "units_sold",
    "unit_price",
    "total_revenue",
    "order_date",
    "status",
}


def _mock_knowledge_profile() -> str:
    """Mock output matching the exact schema of Knowledge Agent for offline evaluation."""
    return json.dumps({
        "tables": [
            {
                "table_name": "data",
                "description": "E-commerce order transactions containing sales and customer details",
                "row_meaning": "One row represents a single order line item",
                "columns": [
                    {"name": "order_id", "semantic_type": "identifier", "role": "key"},
                    {"name": "customer_name", "semantic_type": "identifier", "role": "dimension"},
                    {"name": "country", "semantic_type": "category", "role": "dimension"},
                    {"name": "category", "semantic_type": "category", "role": "dimension"},
                    {"name": "product_name", "semantic_type": "category", "role": "dimension"},
                    {"name": "units_sold", "semantic_type": "measure", "role": "measure"},
                    {"name": "unit_price", "semantic_type": "measure", "role": "measure"},
                    {"name": "total_revenue", "semantic_type": "measure", "role": "measure"},
                    {"name": "order_date", "semantic_type": "date", "role": "time"},
                    {"name": "status", "semantic_type": "category", "role": "dimension"},
                ],
                "example_questions": [
                    "What is the total revenue by category?",
                    "What are the top 3 countries by sales?",
                    "How many completed orders were placed in March?",
                ]
            }
        ]
    })


async def evaluate_knowledge(use_mock: bool = False) -> Dict[str, Any]:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    is_mock = use_mock or not api_key

    file_path = str(DATASET_CSV.resolve())
    profile_dfs = analyze_file(file_path, "csv")
    file_profile = {k: v.to_dict(orient="records") for k, v in profile_dfs.items()}

    t0 = time.time()
    if is_mock:
        raw_schema = _mock_knowledge_profile()
    else:
        state: AssistantState = {"file_profile": file_profile, "llm_calls": 0}
        res = await knowlage_agent(state)
        raw_schema = res.get("schema_context", "")
    duration = time.time() - t0

    # 1. Parse JSON validity
    json_valid = False
    parsed_context = {}
    try:
        parsed_context = json.loads(raw_schema)
        json_valid = True
    except Exception as e:
        json_valid = False

    # 2. Extract columns and tables
    tables = parsed_context.get("tables", [])
    has_tables = len(tables) > 0
    extracted_columns = set()
    role_accuracies = []
    example_questions_count = 0

    if has_tables:
        first_tbl = tables[0]
        cols = first_tbl.get("columns", [])
        for c in cols:
            col_name = c.get("name")
            extracted_columns.add(col_name)
            role = c.get("role")

            # Check semantic assignment
            if col_name in {"total_revenue", "unit_price", "units_sold"}:
                role_accuracies.append(role == "measure")
            elif col_name == "order_date":
                role_accuracies.append(role == "time")
            elif col_name == "order_id":
                role_accuracies.append(role in {"key", "dimension"})

        example_questions_count = len(first_tbl.get("example_questions", []))

    preserved_cols = extracted_columns.intersection(EXPECTED_COLUMNS)
    column_preservation_rate = (len(preserved_cols) / len(EXPECTED_COLUMNS)) * 100
    semantic_role_accuracy = (sum(role_accuracies) / len(role_accuracies) * 100) if role_accuracies else 0

    return {
        "suite": "Knowledge Agent Evaluation",
        "mode": "Mock" if is_mock else "Live (Gemini)",
        "json_valid": json_valid,
        "table_count": len(tables),
        "total_columns_expected": len(EXPECTED_COLUMNS),
        "columns_preserved": len(preserved_cols),
        "column_preservation_rate": round(column_preservation_rate, 2),
        "semantic_role_accuracy": round(semantic_role_accuracy, 2),
        "example_questions_count": example_questions_count,
        "duration_s": round(duration, 2),
    }


def print_knowledge_report(report: Dict[str, Any]):
    print("\n" + "=" * 70)
    print(f"  {report['suite']} - Mode: {report['mode']}")
    print("=" * 70)
    print(f"JSON Validity:             {'PASS' if report['json_valid'] else 'FAIL'}")
    print(f"Column Preservation:       {report['column_preservation_rate']}% ({report['columns_preserved']}/{report['total_columns_expected']})")
    print(f"Semantic Role Accuracy:    {report['semantic_role_accuracy']}%")
    print(f"Example Questions Count:   {report['example_questions_count']}")
    print(f"Duration:                  {report['duration_s']}s")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    mock_flag = "--mock" in sys.argv
    rep = asyncio.run(evaluate_knowledge(use_mock=mock_flag))
    print_knowledge_report(rep)

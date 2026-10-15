import os
import sys
import tempfile
import unittest
from pathlib import Path

# Ensure src is in sys.path
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import pandas as pd
from fastapi.testclient import TestClient

from data_assistant.analysis_code import profile_columns, analyze_file
from data_assistant.Data_engine import explain_query, run_query, result_to_text
from data_assistant.utils import validate_file, _content_to_text, _json_from_llm
from data_assistant.graph import (
    create_assistant_graph,
    route_guardrail,
    route_analysis,
    route_execution,
)
from data_assistant.backend import app


class TestDataAssistant(unittest.TestCase):
    def test_content_to_text_and_json(self):
        self.assertEqual(_content_to_text("hello"), "hello")
        self.assertEqual(
            _content_to_text([{"text": "foo"}, {"text": "bar"}]), "foobar"
        )

        parsed = _json_from_llm(
            'Some prefix text {"status": "ok", "value": 123} trailing text'
        )
        self.assertEqual(parsed["status"], "ok")
        self.assertEqual(parsed["value"], 123)

    def test_file_validation_and_profiling(self):
        with tempfile.NamedTemporaryFile(
            suffix=".csv", mode="w", delete=False, encoding="utf-8"
        ) as f:
            f.write(
                "id,name,revenue,category\n1,Alice,100.5,Tech\n2,Bob,250.0,Retail\n3,Charlie,50.0,Tech\n"
            )
            temp_path = f.name

        try:
            check = validate_file(temp_path)
            self.assertTrue(check.allowed)
            self.assertEqual(check.kind, "csv")

            profiles = analyze_file(temp_path, "csv")
            self.assertIn("data", profiles)
            profile_df = profiles["data"]
            cols = profile_df["column"].tolist()
            self.assertIn("id", cols)
            self.assertIn("revenue", cols)
            self.assertIn("category", cols)

            cat_row = profile_df[profile_df["column"] == "category"].iloc[0]
            self.assertEqual(cat_row["unique_count"], 2)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_duckdb_data_engine(self):
        with tempfile.NamedTemporaryFile(
            suffix=".csv", mode="w", delete=False, encoding="utf-8"
        ) as f:
            f.write("id,name,amount\n1,Alpha,10\n2,Beta,20\n3,Gamma,30\n")
            temp_path = f.name

        try:
            explain_query(
                'SELECT SUM("amount") AS total FROM "data"', temp_path, "csv"
            )
            res = run_query(
                'SELECT SUM("amount") AS total FROM "data"', temp_path, "csv"
            )
            self.assertEqual(res["columns"], ["total"])
            self.assertEqual(res["rows"][0][0], 60)

            text_json = result_to_text(res)
            self.assertIn("total", text_json)
            self.assertIn("60", text_json)

            with self.assertRaises(Exception):
                explain_query(
                    'SELECT "non_existent_col" FROM "data"', temp_path, "csv"
                )
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_graph_structure_and_routes(self):
        graph = create_assistant_graph()
        self.assertIsNotNone(graph)

        self.assertEqual(
            route_guardrail({"guardrail_allowed": True}), "analysis_node"
        )
        self.assertEqual(
            route_guardrail({"guardrail_allowed": False}), "__end__"
        )

        self.assertEqual(
            route_analysis({"sql": 'SELECT * FROM "data"'}), "execute_sql_node"
        )
        self.assertEqual(route_analysis({"sql": ""}), "__end__")

        self.assertEqual(
            route_execution({"sql_error": "", "iteration": 1}), "result_node"
        )
        self.assertEqual(
            route_execution({"sql_error": "Syntax error", "iteration": 1}),
            "analysis_node",
        )
        self.assertEqual(
            route_execution({"sql_error": "Syntax error", "iteration": 3}),
            "__end__",
        )

    def test_fastapi_endpoints(self):
        client = TestClient(app)

        res = client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "healthy")

        res = client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("docs_url", res.json())

        res = client.post(
            "/api/upload",
            files={"file": ("test.txt", b"plain text content", "text/plain")},
        )
        self.assertEqual(res.status_code, 400)


if __name__ == "__main__":
    unittest.main()

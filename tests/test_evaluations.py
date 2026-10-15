import os
import sys
import unittest
import asyncio
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from evaluations.eval_guardrails import evaluate_guardrails
from evaluations.eval_knowledge import evaluate_knowledge
from evaluations.eval_text_to_sql import evaluate_text_to_sql
from evaluations.eval_end_to_end import evaluate_end_to_end


class TestEvaluationsSuite(unittest.TestCase):
    def test_guardrails_evaluation(self):
        report = asyncio.run(evaluate_guardrails(use_mock=True))
        self.assertEqual(report["allowed_accuracy"], 100.0)
        self.assertEqual(report["category_accuracy"], 100.0)
        self.assertEqual(report["total_cases"], 20)

    def test_knowledge_evaluation(self):
        report = asyncio.run(evaluate_knowledge(use_mock=True))
        self.assertTrue(report["json_valid"])
        self.assertEqual(report["column_preservation_rate"], 100.0)
        self.assertEqual(report["columns_preserved"], 10)
        self.assertEqual(report["semantic_role_accuracy"], 100.0)

    def test_text_to_sql_evaluation(self):
        report = asyncio.run(evaluate_text_to_sql(use_mock=True))
        self.assertEqual(report["syntax_validity_rate"], 100.0)
        self.assertEqual(report["execution_success_rate"], 100.0)
        self.assertEqual(report["value_match_rate"], 100.0)
        self.assertEqual(report["total_cases"], 8)

    def test_end_to_end_evaluation(self):
        report = asyncio.run(evaluate_end_to_end(use_mock=True))
        self.assertEqual(report["success_rate"], 100.0)
        self.assertEqual(report["total_scenarios"], 4)


if __name__ == "__main__":
    unittest.main()

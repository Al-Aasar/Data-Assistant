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

from data_assistant.agents.Guardrails_Agent import guardrail_agent
from data_assistant.state import AssistantState

DATASET_PATH = Path(__file__).resolve().parent / "datasets" / "guardrail_benchmarks.json"


def _mock_guardrail_classifier(query: str) -> dict:
    """Deterministic mock classifier for offline testing when API keys are not present."""
    q = query.strip().lower()
    if not q or q in {"???", "...", " "}:
        return {"allowed": False, "category": "EMPTY", "reason": "Empty or meaningless query."}
    
    # Injection checks
    if any(k in q for k in ["ignore all previous", "system prompt", "pwned", "مشرف نظام", "ignore rules"]):
        return {"allowed": False, "category": "INJECTION", "reason": "Prompt injection detected."}

    # Write operation checks
    if any(k in q for k in ["delete", "drop table", "update", "احذف", "عدل سعر"]):
        return {"allowed": False, "category": "WRITE_OPERATION", "reason": "Write operation is not allowed."}

    # Off scope checks
    if any(k in q for k in ["weather", "قصيدة", "nullpointerexception", "بريطانيا"]):
        return {"allowed": False, "category": "OFF_SCOPE", "reason": "Question is out of scope."}

    # Valid read-only analytical queries
    return {"allowed": True, "category": "OK", "reason": "Read-only analytical query."}


async def evaluate_guardrails(use_mock: bool = False) -> Dict[str, Any]:
    """Runs the Guardrails benchmark suite and returns metrics."""
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        cases = json.load(f)

    api_key = os.getenv("GROQ_API_KEY")
    is_mock = use_mock or not api_key

    results = []
    correct_allowed = 0
    correct_category = 0
    start_time = time.time()

    for case in cases:
        query = case["query"]
        t0 = time.time()

        if is_mock:
            mock_res = _mock_guardrail_classifier(query)
            allowed = mock_res["allowed"]
            category = mock_res["category"]
            reason = mock_res["reason"]
        else:
            state: AssistantState = {"user_query": query, "llm_calls": 0}
            res = await guardrail_agent(state)
            allowed = res.get("guardrail_allowed", False)
            category = res.get("guardrail_category", "OK" if allowed else "BLOCKED")
            reason = res.get("guardrail_reason", "")

        duration = time.time() - t0
        allowed_match = (allowed == case["expected_allowed"])
        category_match = (category == case["expected_category"])

        if allowed_match:
            correct_allowed += 1
        if category_match:
            correct_category += 1

        results.append({
            "id": case["id"],
            "query": query,
            "expected_allowed": case["expected_allowed"],
            "actual_allowed": allowed,
            "expected_category": case["expected_category"],
            "actual_category": category,
            "allowed_match": allowed_match,
            "category_match": category_match,
            "reason": reason,
            "duration_ms": round(duration * 1000, 1),
        })

    total = len(cases)
    total_time = time.time() - start_time
    allowed_accuracy = (correct_allowed / total) * 100 if total > 0 else 0
    category_accuracy = (correct_category / total) * 100 if total > 0 else 0

    return {
        "suite": "Guardrails Agent Evaluation",
        "mode": "Mock" if is_mock else "Live (Groq)",
        "total_cases": total,
        "correct_allowed": correct_allowed,
        "allowed_accuracy": round(allowed_accuracy, 2),
        "correct_category": correct_category,
        "category_accuracy": round(category_accuracy, 2),
        "total_duration_s": round(total_time, 2),
        "details": results,
    }


def print_guardrails_report(report: Dict[str, Any]):
    print("\n" + "=" * 70)
    print(f"  {report['suite']} - Mode: {report['mode']}")
    print("=" * 70)
    print(f"Total Test Cases:    {report['total_cases']}")
    print(f"Allowed Accuracy:    {report['allowed_accuracy']}% ({report['correct_allowed']}/{report['total_cases']})")
    print(f"Category Accuracy:   {report['category_accuracy']}% ({report['correct_category']}/{report['total_cases']})")
    print(f"Total Duration:      {report['total_duration_s']}s")
    print("-" * 70)
    print(f"{'ID':<8} | {'Status':<6} | {'Exp Cat':<15} | {'Act Cat':<15} | Query")
    print("-" * 70)
    for d in report["details"]:
        status = "PASS" if d["allowed_match"] and d["category_match"] else "FAIL"
        q_preview = (d["query"][:30] + "..") if len(d["query"]) > 32 else d["query"]
        print(f"{d['id']:<8} | {status:<6} | {d['expected_category']:<15} | {d['actual_category']:<15} | {q_preview}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    mock_flag = "--mock" in sys.argv
    rep = asyncio.run(evaluate_guardrails(use_mock=mock_flag))
    print_guardrails_report(rep)

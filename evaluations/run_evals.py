import argparse
import asyncio
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Clean UTF-8 encoding configuration
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from evaluations.eval_guardrails import evaluate_guardrails, print_guardrails_report
from evaluations.eval_text_to_sql import evaluate_text_to_sql, print_sql_report
from evaluations.eval_knowledge import evaluate_knowledge, print_knowledge_report
from evaluations.eval_end_to_end import evaluate_end_to_end, print_e2e_report

REPORTS_DIR = Path(__file__).resolve().parent / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


async def main():
    parser = argparse.ArgumentParser(description="Data Assistant Agent Evaluation Suite Runner")
    parser.add_argument("--all", action="store_true", help="Run all agent evaluation suites")
    parser.add_argument("--guardrails", action="store_true", help="Run Guardrails Agent evaluation only")
    parser.add_argument("--sql", action="store_true", help="Run Text-to-SQL Analysis Agent evaluation only")
    parser.add_argument("--knowledge", action="store_true", help="Run Knowledge Agent evaluation only")
    parser.add_argument("--e2e", action="store_true", help="Run End-to-End Pipeline evaluation only")
    parser.add_argument("--mock", action="store_true", help="Run in mock/offline mode (no API keys required)")
    parser.add_argument("--save-report", action="store_true", help="Save detailed report to evaluations/reports/")

    args = parser.parse_args()

    # Default to running all if no specific suite selected
    run_all = args.all or not (args.guardrails or args.sql or args.knowledge or args.e2e)

    print("\n" + "#" * 75)
    print("   DATA ASSISTANT - MULTI-AGENT EVALUATION SUITE")
    print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Mode:      {'Mock / Offline' if args.mock else 'Live Models'}")
    print("#" * 75)

    all_reports = {}
    start_total = time.time()

    if run_all or args.guardrails:
        print("\n>>> Running Guardrails Evaluation...")
        gr_report = await evaluate_guardrails(use_mock=args.mock)
        print_guardrails_report(gr_report)
        all_reports["guardrails"] = gr_report

    if run_all or args.knowledge:
        print("\n>>> Running Knowledge Agent Evaluation...")
        kn_report = await evaluate_knowledge(use_mock=args.mock)
        print_knowledge_report(kn_report)
        all_reports["knowledge"] = kn_report

    if run_all or args.sql:
        print("\n>>> Running Text-to-SQL Evaluation...")
        sql_report = await evaluate_text_to_sql(use_mock=args.mock)
        print_sql_report(sql_report)
        all_reports["text_to_sql"] = sql_report

    if run_all or args.e2e:
        print("\n>>> Running End-to-End Evaluation...")
        e2e_report = await evaluate_end_to_end(use_mock=args.mock)
        print_e2e_report(e2e_report)
        all_reports["end_to_end"] = e2e_report

    total_time = round(time.time() - start_total, 2)

    print("\n" + "=" * 75)
    print("  EXECUTIVE SUMMARY OF EVALUATION RESULTS")
    print("=" * 75)
    if "guardrails" in all_reports:
        print(f"  Guardrails Category Accuracy:  {all_reports['guardrails']['category_accuracy']}%")
    if "knowledge" in all_reports:
        print(f"  Knowledge Column Preservation: {all_reports['knowledge']['column_preservation_rate']}%")
    if "text_to_sql" in all_reports:
        print(f"  Text-to-SQL Execution Rate:    {all_reports['text_to_sql']['execution_success_rate']}%")
    if "end_to_end" in all_reports:
        print(f"  End-to-End Success Rate:       {all_reports['end_to_end']['success_rate']}%")
    print(f"  Total Evaluation Time:         {total_time}s")
    print("=" * 75 + "\n")

    if args.save_report:
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = REPORTS_DIR / f"eval_report_{timestamp_str}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(all_reports, f, indent=2, ensure_ascii=False)
        print(f"[+] Saved evaluation report to: {report_file}\n")


if __name__ == "__main__":
    asyncio.run(main())

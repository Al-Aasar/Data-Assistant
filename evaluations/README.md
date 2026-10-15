# Agent Evaluations Suite

Comprehensive evaluation framework designed to benchmark, test, and measure the accuracy, safety, and reliability of each agent in the Data Assistant system.

---

## Evaluation Architecture

The evaluation suite tests the system at both component (agent) level and end-to-end pipeline level:

1. **Guardrails Evaluation (`eval_guardrails.py`):**
   - **Target Agent:** Guardrails Agent (`Guardrails_Agent.py`).
   - **Metrics:** Allowed accuracy, category classification accuracy (`OK`, `WRITE_OPERATION`, `OFF_SCOPE`, `INJECTION`, `EMPTY`), false positive rate, latency.
   - **Dataset:** `datasets/guardrail_benchmarks.json` (20 curated adversarial, write, off-scope, and analytical queries in Arabic and English).

2. **Knowledge Agent Evaluation (`eval_knowledge.py`):**
   - **Target Agent:** Knowledge Agent (`Knowlage_Agent.py`).
   - **Metrics:** JSON output validity, column preservation rate (ensuring no columns are omitted or hallucinated), semantic role classification accuracy (`dimension`, `measure`, `time`, `key`), and example business questions generation.
   - **Dataset:** `datasets/sample_ecommerce.csv`.

3. **Text-to-SQL Analysis Evaluation (`eval_text_to_sql.py`):**
   - **Target Agent:** Analysis Agent (`Analysis_Agent.py`).
   - **Metrics:** Syntax validity rate (verified via DuckDB `EXPLAIN`), Execution success rate (running queries against real tables), Output value correctness (matching expected scalar values or row counts), Read-only compliance (ensuring no destructive SQL is produced).
   - **Dataset:** `datasets/text_to_sql_benchmarks.json`.

4. **End-to-End Pipeline Evaluation (`eval_end_to_end.py`):**
   - **Target:** Full compiled LangGraph state graph.
   - **Metrics:** Complete scenario success rate, routing accuracy, safe rejection of attacks, successful data insights delivery.

---

## Directory Structure

```text
evaluations/
├── datasets/
│   ├── guardrail_benchmarks.json     # Curated benchmark queries for Guardrails
│   ├── text_to_sql_benchmarks.json   # Natural language questions with expected SQL and results
│   └── sample_ecommerce.csv         # Standard benchmark tabular dataset
├── reports/                          # Generated evaluation reports (JSON)
├── eval_guardrails.py                # Standalone Guardrails Agent evaluator
├── eval_knowledge.py                 # Standalone Knowledge Agent evaluator
├── eval_text_to_sql.py               # Standalone Text-to-SQL evaluator
├── eval_end_to_end.py                # Full pipeline end-to-end evaluator
├── run_evals.py                      # Master CLI runner for all evaluations
└── README.md                         # Documentation
```

---

## Running Evaluations

### 1. Run in Mock / Offline Mode (No API Keys Required)
Ideal for automated CI/CD pipelines or local checks without consuming LLM credits:

```bash
uv run python evaluations/run_evals.py --mock
```

### 2. Run with Live LLM Models
Requires `GEMINI_API_KEY` and `GROQ_API_KEY` to be set in your `.env` file:

```bash
uv run python evaluations/run_evals.py --all
```

### 3. Run Individual Evaluation Suites
You can run any specific evaluator:

```bash
# Guardrails only
uv run python evaluations/run_evals.py --guardrails

# Text-to-SQL only
uv run python evaluations/run_evals.py --sql

# Knowledge Agent only
uv run python evaluations/run_evals.py --knowledge

# End-to-End pipeline only
uv run python evaluations/run_evals.py --e2e
```

### 4. Save JSON Evaluation Reports
Use the `--save-report` flag to persist benchmark results into `evaluations/reports/`:

```bash
uv run python evaluations/run_evals.py --mock --save-report
```

---

## Adding Custom Benchmarks

To extend the benchmark datasets with your own domain-specific questions:
- **Guardrails:** Add new cases to `evaluations/datasets/guardrail_benchmarks.json` specifying `query`, `expected_allowed`, and `expected_category`.
- **Text-to-SQL:** Add questions to `evaluations/datasets/text_to_sql_benchmarks.json` specifying `question`, `expected_sql`, and verification criteria (`check_type`: `scalar_numeric`, `row_count`, or `min_rows`).

"""Root runner script for Data Assistant.

Ensures 'src' is always in sys.path regardless of OS encoding or editable install status.
Usage:
    uv run python run.py --server
    uv run python run.py --file "evaluations/datasets/sample_ecommerce.csv"
"""

import sys
from pathlib import Path

# Add src to sys.path
src_path = Path(__file__).resolve().parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from data_assistant.main import cli_main

if __name__ == "__main__":
    cli_main()

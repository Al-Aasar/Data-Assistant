from pathlib import Path
import pandas as pd

ENCODINGS = ("utf-8-sig", "cp1256", "cp1252")
MAX_UNIQUE = 50


def _read_csv(path: Path) -> dict[str, pd.DataFrame]:
    for enc in ENCODINGS:
        try:
            return {"data": pd.read_csv(path, sep=None, engine="python", encoding=enc)}
        except UnicodeDecodeError:
            continue
    raise ValueError("Could not decode the CSV file with any supported encoding.")


def _read_excel(path: Path, engine: str) -> dict[str, pd.DataFrame]:
    return pd.read_excel(path, sheet_name=None, engine=engine)


READERS = {
    "csv": _read_csv,
    "xlsx": lambda p: _read_excel(p, "openpyxl"),
    "xls": lambda p: _read_excel(p, "xlrd"),
}


def load_file(path: str | Path, kind: str) -> dict[str, pd.DataFrame]:
    """Return {table_name: DataFrame}. CSV gives one table, Excel gives one per sheet."""
    try:
        return READERS[kind](Path(path))
    except KeyError:
        raise ValueError(f"Unsupported file kind: {kind}")
    except Exception as e:
        raise ValueError(f"Failed to read the file: {e}") from e


def profile_columns(df: pd.DataFrame, max_unique: int | None = MAX_UNIQUE) -> pd.DataFrame:
    """One row per column: name, dtype, unique count, and the unique values."""
    rows = []
    for col in df.columns:
        uniques = df[col].dropna().unique().tolist()
        shown = uniques if max_unique is None else uniques[:max_unique]
        rows.append(
            {
                "column": str(col),
                "dtype": str(df[col].dtype),
                "unique_count": len(uniques),
                "unique_values": shown,
                "truncated": len(shown) < len(uniques),
            }
        )
    return pd.DataFrame(rows)


def analyze_file(path: str | Path, kind: str, max_unique: int | None = MAX_UNIQUE) -> dict[str, pd.DataFrame]:
    """Main entry point: {table_name: profile_table} ready for the Knowledge Agent."""
    tables = load_file(path, kind)
    return {name: profile_columns(df, max_unique) for name, df in tables.items()}


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        path = sys.argv[1]
        kind = Path(path).suffix.lower().lstrip(".")
        pd.set_option("display.max_colwidth", 80)
        for table, profile in analyze_file(path, kind).items():
            print(f"\n=== {table} ===")
            print(profile.to_string(index=False))

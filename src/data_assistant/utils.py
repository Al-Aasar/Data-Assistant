from typing import Any
from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)
import json
import csv
import zipfile
from dataclasses import dataclass
from pathlib import Path
import sys

MAX_SIZE_MB = 1024
SAMPLE_BYTES = 64 * 1024
ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}
OLE2_MAGIC = b"\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1"  # legacy .xls header
ENCODINGS = ("utf-8-sig", "cp1256", "cp1252")     # utf-8, Arabic Windows, Western



from langchain_core.language_models import BaseChatModel

def _content_to_text(content) -> str:
    """Normalize LangChain message content (str, BaseMessage, or list of blocks) to plain text."""
    if hasattr(content, "content"):
        content = content.content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            block.get("text", "") if isinstance(block, dict) else str(block)
            for block in content
        )
    return str(content)


content_to_text = _content_to_text


def _llm_text(user_prompt: str, system_prompt: str, llm: BaseChatModel | None = None) -> str:
    llm = llm
    response = llm.invoke(
        [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
    )
    return _content_to_text(response.content).strip()


def _json_from_llm(text: str) -> dict[str, Any]:
    """Extract the first complete JSON object returned by the model."""
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end < start:
        raise ValueError("The model did not return a JSON object.")

    return json.loads(text[start : end + 1])


json_from_llm = _json_from_llm

@dataclass
class FileCheck:
    allowed: bool
    kind: str | None 
    reason: str


def _reject(reason: str) -> FileCheck:
    return FileCheck(False, None, reason)


def _is_xlsx(path: Path) -> bool:
    if not zipfile.is_zipfile(path):
        return False
    with zipfile.ZipFile(path) as z:
        return "xl/workbook.xml" in z.namelist()


def _is_xls(path: Path) -> bool:
    with open(path, "rb") as f:
        return f.read(8) == OLE2_MAGIC


def _decode_sample(sample: bytes) -> str | None:
    if b"\x00" in sample:  
        return None
    for enc in ENCODINGS:
        for trim in range(4):
            try:
                return sample[: len(sample) - trim].decode(enc)
            except UnicodeDecodeError:
                continue
    return None


def _is_csv(path: Path) -> bool:
    with open(path, "rb") as f:
        text = _decode_sample(f.read(SAMPLE_BYTES))
    if not text or not text.strip():
        return False
    try:
        csv.Sniffer().sniff(text, delimiters=",;\t|")
        return True
    except csv.Error:
        return len([l for l in text.splitlines() if l.strip()]) >= 2


def validate_file(path: str | Path) -> FileCheck:
    path = Path(path)

    if not path.is_file():
        return _reject("File not found.")
    if path.stat().st_size == 0:
        return _reject("The file is empty.")
    if path.stat().st_size > MAX_SIZE_MB * 1024 * 1024:
        return _reject(f"File is larger than {MAX_SIZE_MB} MB.")

    ext = path.suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return _reject("Only CSV or Excel files (.csv, .xlsx, .xls) are supported.")

    checks = {".xlsx": _is_xlsx, ".xls": _is_xls, ".csv": _is_csv}
    if not checks[ext](path):
        return _reject(f"The file content does not match a valid {ext} file.")

    return FileCheck(True, ext.lstrip("."), "OK")
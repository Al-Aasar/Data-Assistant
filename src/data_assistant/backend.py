import json
import os
import shutil
import uuid
from pathlib import Path
from typing import Optional, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from data_assistant.graph import create_assistant_graph, ingest_file
from data_assistant.state import AssistantState

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="Data Assistant API",
    description="Conversational Multi-Agent Data Analyst powered by DuckDB & LLMs",
    version="0.1.0",
)

# Enable CORS for frontend integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

assistant_graph = create_assistant_graph()


class ChatRequest(BaseModel):
    user_query: str
    file_path: str
    file_kind: Optional[str] = None
    schema_context: Optional[str] = None


class ChatResponse(BaseModel):
    final_response: str
    sql: Optional[str] = None
    query_result: Optional[Any] = None
    guardrail_allowed: bool
    guardrail_category: Optional[str] = None
    guardrail_reason: Optional[str] = None
    error: Optional[str] = None
    llm_calls: int = 0


@app.get("/")
def root():
    return {
        "message": "Welcome to Data Assistant API",
        "docs_url": "/docs",
        "health_url": "/api/health",
    }


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "data-assistant"}


@app.post("/api/upload")
async def upload_file_endpoint(file: UploadFile = File(...)):
    """Uploads a CSV or Excel file, validates it, and generates semantic schema context."""
    ext = Path(file.filename or "").suffix.lower()
    if ext not in {".csv", ".xlsx", ".xls"}:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Only .csv, .xlsx, and .xls files are supported.",
        )

    unique_name = f"{uuid.uuid4().hex[:8]}_{Path(file.filename).name}"
    save_path = UPLOAD_DIR / unique_name

    try:
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {e}")

    ingest_result = await ingest_file(str(save_path))
    if not ingest_result.get("success"):
        # Cleanup file if invalid
        if save_path.exists():
            save_path.unlink()
        raise HTTPException(
            status_code=400,
            detail=ingest_result.get("error", "Invalid file structure or content."),
        )

    # Try parsing schema_context JSON for user-friendly table summary
    parsed_context = {}
    schema_raw = ingest_result.get("schema_context", "")
    if schema_raw:
        try:
            parsed_context = json.loads(schema_raw)
        except Exception:
            parsed_context = {"raw": schema_raw}

    return {
        "message": "File uploaded and analyzed successfully.",
        "file_path": ingest_result["file_path"],
        "file_kind": ingest_result["file_kind"],
        "schema_context": schema_raw,
        "metadata": parsed_context,
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Processes natural language questions about the uploaded dataset."""
    file_path = request.file_path
    if not Path(file_path).is_file():
        raise HTTPException(status_code=404, detail="The specified file was not found.")

    file_kind = request.file_kind
    if not file_kind:
        file_kind = Path(file_path).suffix.lower().lstrip(".")

    schema_context = request.schema_context
    if not schema_context:
        # Generate schema context if not passed
        ingest_res = await ingest_file(file_path)
        if not ingest_res.get("success"):
            raise HTTPException(status_code=400, detail=ingest_res.get("error"))
        schema_context = ingest_res.get("schema_context", "")

    initial_state: AssistantState = {
        "user_query": request.user_query,
        "file_path": file_path,
        "file_kind": file_kind,
        "schema_context": schema_context,
        "iteration": 0,
        "llm_calls": 0,
    }

    try:
        final_state = await assistant_graph.ainvoke(initial_state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph execution failed: {e}")

    raw_result = final_state.get("query_result")
    parsed_result = None
    if raw_result:
        try:
            parsed_result = json.loads(raw_result)
        except Exception:
            parsed_result = raw_result

    return ChatResponse(
        final_response=final_state.get("final_response", ""),
        sql=final_state.get("sql"),
        query_result=parsed_result,
        guardrail_allowed=final_state.get("guardrail_allowed", False),
        guardrail_category=final_state.get("guardrail_category"),
        guardrail_reason=final_state.get("guardrail_reason"),
        error=final_state.get("error"),
        llm_calls=final_state.get("llm_calls", 0),
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("data_assistant.backend:app", host="0.0.0.0", port=8000, reload=True)

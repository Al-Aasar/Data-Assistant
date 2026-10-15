from langgraph.graph import StateGraph, END
from typing import Literal

from data_assistant.state import AssistantState
from data_assistant.agents.Guardrails_Agent import guardrail_agent
from data_assistant.agents.Analysis_Agent import analysis_agent, result_agent
from data_assistant.agents.Knowlage_Agent import knowlage_agent
from data_assistant.Data_engine import explain_query, run_query, result_to_text
from data_assistant.analysis_code import analyze_file
from data_assistant.utils import validate_file


MAX_SQL_RETRIES = 3


async def guardrail_node(state: AssistantState) -> dict:
    return await guardrail_agent(state)


async def analysis_node(state: AssistantState) -> dict:
    return await analysis_agent(state)


def execute_sql_node(state: AssistantState) -> dict:
    sql = state.get("sql", "").strip()
    file_path = state.get("file_path", "")
    file_kind = state.get("file_kind", "")
    iteration = state.get("iteration", 0)

    if not sql or not file_path:
        return {
            "sql_error": "No SQL query or file path provided.",
            "final_response": "لم يتم تحديد استعلام أو ملف للتحليل.",
        }

    try:
        explain_query(sql, file_path, file_kind)
        result = run_query(sql, file_path, file_kind)
        return {
            "query_result": result_to_text(result),
            "sql_error": "",
        }
    except Exception as e:
        error_msg = str(e)
        res = {"sql_error": error_msg}
        if iteration >= MAX_SQL_RETRIES:
            res["final_response"] = (
                "تعذر تشغيل الاستعلام بنجاح بعد عدة محاولات. "
                "يرجى إعادة صياغة السؤال بشكل أكثر تحديداً."
            )
            res["error"] = error_msg
        return res


async def result_node(state: AssistantState) -> dict:
    return await result_agent(state)


def route_guardrail(state: AssistantState) -> Literal["analysis_node", "__end__"]:
    if state.get("guardrail_allowed", False):
        return "analysis_node"
    return END


def route_analysis(state: AssistantState) -> Literal["execute_sql_node", "__end__"]:
    sql = state.get("sql", "").strip()
    if sql:
        return "execute_sql_node"
    return END


def route_execution(state: AssistantState) -> Literal["analysis_node", "result_node", "__end__"]:
    sql_error = state.get("sql_error", "")
    iteration = state.get("iteration", 0)

    if sql_error:
        if iteration < MAX_SQL_RETRIES:
            return "analysis_node"
        return END

    return "result_node"


def create_assistant_graph():
    """Builds and compiles the conversational data analysis LangGraph workflow."""
    workflow = StateGraph(AssistantState)

    workflow.add_node("guardrail_node", guardrail_node)
    workflow.add_node("analysis_node", analysis_node)
    workflow.add_node("execute_sql_node", execute_sql_node)
    workflow.add_node("result_node", result_node)

    workflow.set_entry_point("guardrail_node")

    workflow.add_conditional_edges(
        "guardrail_node",
        route_guardrail,
        {
            "analysis_node": "analysis_node",
            END: END,
        },
    )

    workflow.add_conditional_edges(
        "analysis_node",
        route_analysis,
        {
            "execute_sql_node": "execute_sql_node",
            END: END,
        },
    )

    workflow.add_conditional_edges(
        "execute_sql_node",
        route_execution,
        {
            "analysis_node": "analysis_node",
            "result_node": "result_node",
            END: END,
        },
    )

    workflow.add_edge("result_node", END)

    return workflow.compile()


async def ingest_file(file_path: str) -> dict:
    """Validates the uploaded file, extracts profiles, and produces schema context."""
    check = validate_file(file_path)
    if not check.allowed:
        return {
            "success": False,
            "error": check.reason,
            "file_path": file_path,
        }

    kind = check.kind
    try:
        profile_dfs = analyze_file(file_path, kind)
        # Convert DataFrames to dict of records for JSON serialization
        file_profile = {
            table_name: df.to_dict(orient="records")
            for table_name, df in profile_dfs.items()
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to analyze file: {e}",
            "file_path": file_path,
            "file_kind": kind,
        }

    # Generate schema context via Knowledge Agent
    initial_state: AssistantState = {
        "file_path": str(file_path),
        "file_kind": str(kind),
        "file_profile": file_profile,
        "llm_calls": 0,
    }
    knowledge_res = await knowlage_agent(initial_state)

    return {
        "success": True,
        "file_path": str(file_path),
        "file_kind": str(kind),
        "file_profile": file_profile,
        "schema_context": knowledge_res.get("schema_context", ""),
        "llm_calls": knowledge_res.get("llm_calls", 0),
    }

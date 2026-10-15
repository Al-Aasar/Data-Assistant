import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from data_assistant.graph import create_assistant_graph, ingest_file
from data_assistant.state import AssistantState


async def interactive_chat(file_path: str):
    """Interactive CLI terminal session with the Data Assistant."""
    path = Path(file_path)
    if not path.is_file():
        print(f"Error: File '{file_path}' does not exist.")
        return

    print(f"\n[+] Ingesting and analyzing: {path.name}...")
    ingest_res = await ingest_file(str(path.resolve()))
    if not ingest_res.get("success"):
        print(f"[-] Ingestion failed: {ingest_res.get('error')}")
        return

    schema_context = ingest_res.get("schema_context", "")
    print("[+] File analyzed successfully!")
    try:
        parsed = json.loads(schema_context)
        for tbl in parsed.get("tables", []):
            print(f"\n--- Table: {tbl.get('table_name')} ---")
            print(f"Description: {tbl.get('description')}")
            questions = tbl.get("example_questions", [])
            if questions:
                print("Example questions you can ask:")
                for q in questions:
                    print(f"  * {q}")
    except Exception:
        pass

    graph = create_assistant_graph()
    print("\n" + "=" * 50)
    print("Data Assistant Ready! Type your question or 'exit' to quit.")
    print("=" * 50)

    while True:
        try:
            query = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not query:
            continue
        if query.lower() in {"exit", "quit", "q"}:
            print("Goodbye!")
            break

        state: AssistantState = {
            "user_query": query,
            "file_path": str(path.resolve()),
            "file_kind": ingest_res["file_kind"],
            "schema_context": schema_context,
            "iteration": 0,
            "llm_calls": 0,
        }

        print("\nThinking and querying data...")
        try:
            result_state = await graph.ainvoke(state)
            if result_state.get("sql"):
                print(f"\n[SQL Generated]:\n{result_state['sql']}")

            print(f"\n[Assistant]:\n{result_state.get('final_response', '')}")
        except Exception as e:
            print(f"\n[Error]: {e}")


def cli_main():
    """Command-line entry point."""
    parser = argparse.ArgumentParser(description="Data Assistant CLI & Server")
    parser.add_argument("--server", action="store_true", help="Start the FastAPI backend server")
    parser.add_argument("--host", default="0.0.0.0", help="Server host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Server port (default: 8000)")
    parser.add_argument("--file", type=str, help="Path to CSV or Excel file for interactive CLI mode")

    args = parser.parse_args()

    if args.server:
        import uvicorn
        print(f"Starting Data Assistant API on http://{args.host}:{args.port}...")
        uvicorn.run("data_assistant.backend:app", host=args.host, port=args.port, reload=True)
    elif args.file:
        asyncio.run(interactive_chat(args.file))
    else:
        print("Data Assistant")
        print("Usage:")
        print("  python -m data_assistant.main --server                (Run FastAPI server)")
        print("  python -m data_assistant.main --file <path_to_data>   (Interactive CLI)")
        print("\nTip: Defaulting to starting the server...")
        import uvicorn
        uvicorn.run("data_assistant.backend:app", host=args.host, port=args.port, reload=True)


if __name__ == "__main__":
    cli_main()

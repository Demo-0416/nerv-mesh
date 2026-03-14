"""CLI entry point for nerv-mesh."""

import argparse
import asyncio
import sys
from pathlib import Path

from nerv_mesh.config import load_config


def main() -> None:
    args = _parse_args()

    try:
        config = load_config(args.config)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    match args.command:
        case "serve":
            _start_gateway(config, args.host, args.port)
        case "chat":
            if args.prompt:
                asyncio.run(_oneshot(config, args.prompt))
            else:
                asyncio.run(_interactive(config))
        case _:
            asyncio.run(_interactive(config))


def _start_gateway(config, host: str | None, port: int | None) -> None:
    """Launch the FastAPI gateway with uvicorn."""
    import uvicorn

    from nerv_mesh.gateway import create_app

    gw = config.gateway
    app = create_app(config)
    uvicorn.run(app, host=host or gw.host, port=port or gw.port)


async def _interactive(config) -> None:
    from nerv_mesh.channels.cli import run_cli

    await run_cli(config)


async def _oneshot(config, prompt: str) -> None:
    """Execute a single prompt and exit."""
    from langchain_core.messages import HumanMessage

    from nerv_mesh.channels.cli import _init_components

    _, _, agent = _init_components(config)
    result = await agent.ainvoke(
        {"messages": [HumanMessage(content=prompt)]},
        config={"configurable": {"thread_id": "oneshot"}},
    )
    print(result["messages"][-1].content)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="nerv-mesh",
        description="AI coding agent with multi-model support",
    )
    parser.add_argument(
        "-c", "--config", type=Path, default=None, help="Path to config.yaml",
    )
    sub = parser.add_subparsers(dest="command")

    # nerv-mesh chat [-p "..."]
    chat_p = sub.add_parser("chat", help="Interactive CLI or one-shot prompt")
    chat_p.add_argument("-p", "--prompt", type=str, default=None, help="One-shot prompt")

    # nerv-mesh serve [--host] [--port]
    serve_p = sub.add_parser("serve", help="Start the HTTP gateway")
    serve_p.add_argument("--host", type=str, default=None)
    serve_p.add_argument("--port", type=int, default=None)

    return parser.parse_args()


if __name__ == "__main__":
    main()

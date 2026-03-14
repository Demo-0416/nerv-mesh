# nerv-mesh

AI coding agent built on LangGraph + LangChain, multi-model via Alibaba Coding Plan.

## Tech Stack
- Python 3.12+, uv package manager
- LangGraph (orchestration, checkpointing, ReAct agent)
- LangChain (model abstraction, tool framework)
- Pydantic 2 (config validation)
- Rich (CLI output)

## Architecture Layers
```
channels/   → User interfaces (CLI, Feishu)
agents/     → LangGraph agent graph + state
tools/      → LangChain tools + aggregation
llm/        → Dynamic model resolution from config
memory/     → JSON-based fact store (DeerFlow pattern)
sandbox/    → Isolated command execution
config/     → YAML config + env var resolution
```

## Commands
```bash
uv sync                    # Install dependencies
uv run nerv-mesh           # Start interactive CLI
uv run nerv-mesh -p "..."  # One-shot prompt
uv run pytest              # Run tests
uv run ruff check src/     # Lint
```

## Conventions
- Max function body: ~30 lines
- Type hints on all public functions
- One primary concern per file
- Config-driven: no hardcoded model names, URLs, or keys
- Async-first for I/O operations
- Imports: stdlib → third-party → local (enforced by ruff isort)

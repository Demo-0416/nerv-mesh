"""Memory tools — let the agent read and update its persistent memory files."""

from langchain_core.tools import BaseTool, tool

from nerv_mesh.config.paths import home_dir


def make_memory_tools() -> list[BaseTool]:
    return [memory_read, memory_update]


@tool
def memory_read(file: str) -> str:
    """Read a memory file (SOUL.md, USER.md, or NERV.md).

    Args:
        file: One of "SOUL.md", "USER.md", "NERV.md".
    """
    path = _resolve_memory_path(file)
    if path is None:
        return f"Error: unknown memory file '{file}'. Use SOUL.md, USER.md, or NERV.md."
    if not path.exists():
        return f"{file} does not exist yet."
    return path.read_text(encoding="utf-8")


@tool
def memory_update(file: str, content: str) -> str:
    """Update a memory file. Use this to persist learnings about the user or yourself.

    Args:
        file: One of "SOUL.md", "USER.md", "NERV.md".
        content: The new full content of the file.
    """
    path = _resolve_memory_path(file)
    if path is None:
        return f"Error: unknown memory file '{file}'. Use SOUL.md, USER.md, or NERV.md."
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return f"Updated {file}. Changes take effect on next conversation."


def _resolve_memory_path(file: str):
    """Map file name to actual path."""
    h = home_dir()
    mapping = {
        "NERV.md": h / "NERV.md",
        "SOUL.md": h / "memory" / "SOUL.md",
        "USER.md": h / "memory" / "USER.md",
    }
    return mapping.get(file)

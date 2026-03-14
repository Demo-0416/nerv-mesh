"""Built-in tools available to all agents."""

from pathlib import Path

from langchain_core.tools import BaseTool, tool

from nerv_mesh.sandbox.local import LocalSandbox


def make_builtin_tools(sandbox: LocalSandbox) -> list[BaseTool]:
    """Create built-in tools with sandbox binding."""
    return [
        _make_shell_tool(sandbox),
        file_read,
        file_write,
        list_directory,
    ]


def _make_shell_tool(sandbox: LocalSandbox) -> BaseTool:
    @tool
    async def shell_exec(command: str) -> str:
        """Execute a shell command in the sandbox. For running tests, builds, git, etc."""
        return await sandbox.execute(command)

    return shell_exec


@tool
def file_read(path: str) -> str:
    """Read the contents of a file. Use absolute or relative paths."""
    target = Path(path).expanduser().resolve()
    if not target.exists():
        return f"Error: file not found — {path}"
    if not target.is_file():
        return f"Error: not a file — {path}"
    return target.read_text(encoding="utf-8")


@tool
def file_write(path: str, content: str) -> str:
    """Write content to a file. Creates parent directories if needed."""
    target = Path(path).expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return f"Written {len(content)} chars to {path}"


@tool
def list_directory(path: str = ".") -> str:
    """List files and directories at the given path."""
    target = Path(path).expanduser().resolve()
    if not target.exists():
        return f"Error: path not found — {path}"
    if not target.is_dir():
        return f"Error: not a directory — {path}"
    entries = sorted(target.iterdir(), key=lambda p: (not p.is_dir(), p.name))
    lines = [f"{'d' if e.is_dir() else 'f'}  {e.name}" for e in entries]
    return "\n".join(lines) if lines else "(empty directory)"

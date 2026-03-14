"""Built-in tools — file ops + shell execution."""

from pathlib import Path

from langchain_core.tools import BaseTool, tool

from nerv_mesh.sandbox.local import LocalSandbox


def make_builtin_tools(sandbox: LocalSandbox) -> list[BaseTool]:
    """Create built-in tools with sandbox binding."""
    return [
        _make_shell_tool(sandbox),
        file_read,
        file_write,
        file_edit,
        list_directory,
    ]


def _make_shell_tool(sandbox: LocalSandbox) -> BaseTool:
    @tool
    async def shell_exec(command: str) -> str:
        """Execute a shell command in the sandbox. For running tests, builds, git, etc."""
        return await sandbox.execute(command)

    return shell_exec


@tool
def file_read(path: str, offset: int = 0, limit: int = 0) -> str:
    """Read the contents of a file.

    Args:
        path: File path (absolute or relative).
        offset: Start reading from this line number (0 = beginning).
        limit: Max lines to return (0 = all).
    """
    target = Path(path).expanduser().resolve()
    if not target.exists():
        return f"Error: file not found — {path}"
    if not target.is_file():
        return f"Error: not a file — {path}"
    lines = target.read_text(encoding="utf-8").splitlines(keepends=True)
    if offset or limit:
        end = offset + limit if limit else len(lines)
        lines = lines[offset:end]
    numbered = [f"{i + offset + 1:>5}\t{line}" for i, line in enumerate(lines)]
    return "".join(numbered)


@tool
def file_write(path: str, content: str) -> str:
    """Write content to a file. Creates parent directories if needed."""
    target = Path(path).expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return f"Written {len(content)} chars to {path}"


@tool
def file_edit(path: str, old_string: str, new_string: str) -> str:
    """Replace an exact string occurrence in a file.

    The old_string must appear exactly once in the file (for safety).
    Use this instead of file_write when making targeted changes.

    Args:
        path: File path.
        old_string: The exact text to find (must be unique in the file).
        new_string: The replacement text.
    """
    target = Path(path).expanduser().resolve()
    if not target.exists():
        return f"Error: file not found — {path}"
    content = target.read_text(encoding="utf-8")
    count = content.count(old_string)
    if count == 0:
        return "Error: old_string not found in file."
    if count > 1:
        return f"Error: old_string found {count} times. Must be unique — add more context."
    target.write_text(content.replace(old_string, new_string, 1), encoding="utf-8")
    return f"Replaced 1 occurrence in {path}"


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

"""Search tools — grep (content search) + glob (file pattern matching)."""

import re
from pathlib import Path

from langchain_core.tools import BaseTool, tool

_BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".webp",
    ".mp3", ".mp4", ".avi", ".mov", ".wav",
    ".zip", ".tar", ".gz", ".bz2", ".7z", ".rar",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx",
    ".pyc", ".so", ".dylib", ".dll", ".exe",
    ".woff", ".woff2", ".ttf", ".eot",
}

_MAX_RESULTS = 50


def make_search_tools() -> list[BaseTool]:
    return [grep_search, glob_search]


@tool
def grep_search(
    pattern: str,
    path: str = ".",
    include: str = "",
    max_results: int = _MAX_RESULTS,
) -> str:
    """Search file contents using a regex pattern (like ripgrep).

    Args:
        pattern: Regex pattern to search for.
        path: Directory or file to search in.
        include: Glob filter for filenames (e.g. "*.py", "*.ts").
        max_results: Max matching lines to return.
    """
    target = Path(path).expanduser().resolve()
    if not target.exists():
        return f"Error: path not found — {path}"

    try:
        compiled = re.compile(pattern)
    except re.error as e:
        return f"Error: invalid regex — {e}"

    matches: list[str] = []
    files = _walk_files(target, include)

    for fpath in files:
        _search_file(fpath, compiled, matches, max_results)
        if len(matches) >= max_results:
            break

    if not matches:
        return f"No matches found for pattern: {pattern}"

    header = f"Found {len(matches)} match(es):\n"
    truncated = f"\n... (truncated at {max_results})" if len(matches) >= max_results else ""
    return header + "\n".join(matches) + truncated


@tool
def glob_search(pattern: str, path: str = ".") -> str:
    """Find files matching a glob pattern (e.g. '**/*.py', 'src/**/*.ts').

    Args:
        pattern: Glob pattern.
        path: Root directory to search from.
    """
    target = Path(path).expanduser().resolve()
    if not target.exists():
        return f"Error: path not found — {path}"

    results = sorted(target.glob(pattern))
    if not results:
        return f"No files matching: {pattern}"

    lines = [str(r.relative_to(target)) for r in results[:_MAX_RESULTS]]
    header = f"Found {len(results)} file(s):\n"
    truncated = f"\n... ({len(results) - _MAX_RESULTS} more)" if len(results) > _MAX_RESULTS else ""
    return header + "\n".join(lines) + truncated


def _walk_files(root: Path, include: str) -> list[Path]:
    """Collect files, optionally filtered by glob pattern."""
    if root.is_file():
        return [root]
    pattern = include if include else "**/*"
    return [
        p for p in sorted(root.glob(pattern))
        if p.is_file() and p.suffix not in _BINARY_EXTENSIONS
    ]


def _search_file(
    fpath: Path, pattern: re.Pattern, matches: list[str], limit: int
) -> None:
    """Search a single file and append formatted matches."""
    try:
        lines = fpath.read_text(encoding="utf-8", errors="ignore").splitlines()
    except (OSError, UnicodeDecodeError):
        return
    for i, line in enumerate(lines, 1):
        if pattern.search(line):
            matches.append(f"  {fpath}:{i}: {line.rstrip()}")
            if len(matches) >= limit:
                return

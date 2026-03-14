"""Web tools — search the internet and fetch URL content."""

import re

import httpx
from langchain_core.tools import BaseTool, tool

_TIMEOUT = 15
_MAX_CONTENT_LENGTH = 8000


def make_web_tools() -> list[BaseTool]:
    return [web_search, web_fetch]


@tool
def web_search(query: str, max_results: int = 5) -> str:
    """Search the internet using DuckDuckGo.

    Args:
        query: Search query string.
        max_results: Number of results to return (default 5).
    """
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        return "Error: duckduckgo-search not installed. Run: pip install duckduckgo-search"

    try:
        results = DDGS().text(query, max_results=max_results)
    except Exception as e:
        return f"Search error: {e}"

    if not results:
        return f"No results found for: {query}"

    lines = []
    for r in results:
        title = r.get("title", "")
        href = r.get("href", "")
        body = r.get("body", "")
        lines.append(f"**{title}**\n{href}\n{body}\n")
    return "\n".join(lines)


@tool
def web_fetch(url: str, extract_text: bool = True) -> str:
    """Fetch content from a URL.

    Args:
        url: The URL to fetch.
        extract_text: If True, strip HTML tags and return plain text.
    """
    try:
        resp = httpx.get(url, timeout=_TIMEOUT, follow_redirects=True, headers=_headers())
        resp.raise_for_status()
    except httpx.HTTPStatusError as e:
        return f"HTTP error {e.response.status_code}: {url}"
    except httpx.RequestError as e:
        return f"Request error: {e}"

    content_type = resp.headers.get("content-type", "")
    if "text/html" in content_type and extract_text:
        text = _html_to_text(resp.text)
    else:
        text = resp.text

    if len(text) > _MAX_CONTENT_LENGTH:
        text = text[:_MAX_CONTENT_LENGTH] + f"\n\n... (truncated, {len(resp.text)} total chars)"
    return text


def _html_to_text(html: str) -> str:
    """Basic HTML to plain text conversion."""
    text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</(p|div|h[1-6]|li|tr)>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"&lt;", "<", text)
    text = re.sub(r"&gt;", ">", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _headers() -> dict:
    return {"User-Agent": "nerv-mesh/0.1 (httpx)"}

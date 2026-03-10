import asyncio
import os
import subprocess
import textwrap

from langchain_core.tools import tool


# ---------------------------------------------------------------------------
# DuckDuckGo — async, using the ddgs package (formerly duckduckgo-search)
# ---------------------------------------------------------------------------

async def _duckduckgo_search_async(query: str, max_attempts: int = 3) -> str:
    """Run DuckDuckGo search asynchronously with exponential back-off retries."""
    last_error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            from ddgs import DDGS  # noqa: PLC0415

            # DDGS is synchronous — run in thread pool to avoid blocking the event loop
            results = await asyncio.to_thread(
                lambda: list(DDGS().text(query, max_results=6))
            )

            if not results:
                raise ValueError("DuckDuckGo returned no results.")

            return "\n\n".join(
                f"**{r.get('title', 'Result')}**\n{r.get('body', '')}\nURL: {r.get('href', '')}"
                for r in results
            )
        except Exception as exc:
            last_error = exc
            print(f"[web_search] DuckDuckGo attempt {attempt} failed: {exc}")
            if attempt < max_attempts:
                await asyncio.sleep(attempt)  # 1 s, 2 s back-off

    return f"DuckDuckGo search failed after {max_attempts} attempts: {last_error}"


# ---------------------------------------------------------------------------
# Tavily — async via httpx (optional, higher quality; requires TAVILY_API_KEY)
# ---------------------------------------------------------------------------

async def _tavily_search_async(query: str) -> str:
    """Async Tavily search using direct HTTP call (no sync wrapper)."""
    import httpx  # noqa: PLC0415

    api_key = os.environ["TAVILY_API_KEY"]
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            "https://api.tavily.com/search",
            json={
                "api_key": api_key,
                "query": query,
                "max_results": 6,
                "search_depth": "advanced",
            },
        )
        resp.raise_for_status()
        data = resp.json()

    results = data.get("results", [])
    if not results:
        raise ValueError("Tavily returned no results.")

    return "\n\n".join(
        f"**{r.get('title', 'Result')}**\n{r.get('content', '')}\nURL: {r.get('url', '')}"
        for r in results
    )


# ---------------------------------------------------------------------------
# Public tool — Tavily preferred, DuckDuckGo as fallback
# ---------------------------------------------------------------------------

@tool
async def web_search(query: str) -> str:
    """Search the web for current, factual, or up-to-date information.

    Call this tool whenever the user asks about:
    - Current events, news, weather, or recent developments
    - Facts that may have changed after the model's training cutoff
    - Specific people, companies, products, places, or prices
    - Anything where a live web lookup beats relying solely on training data
      (e.g. stock prices, sports scores, upcoming events, local info)

    Args:
        query: A focused search query string. Be specific for better results.

    Returns:
        A formatted summary of the top search results with titles and URLs.
    """
    tavily_key = os.environ.get("TAVILY_API_KEY", "").strip()
    if tavily_key:
        try:
            return await _tavily_search_async(query)
        except Exception as exc:
            print(f"[web_search] Tavily failed ({exc}), falling back to DuckDuckGo")

    return await _duckduckgo_search_async(query)


# ---------------------------------------------------------------------------
# Python REPL — runs in a thread so it doesn't block the event loop
# ---------------------------------------------------------------------------

@tool
async def python_repl(code: str) -> str:
    """Execute Python code in a sandboxed subprocess and return stdout/stderr.
    Use for data analysis, calculations, or code validation.
    """
    def _run() -> str:
        try:
            result = subprocess.run(
                ["python", "-c", textwrap.dedent(code)],
                capture_output=True,
                text=True,
                timeout=15,
            )
            output = result.stdout or ""
            error = result.stderr or ""
            if error:
                return f"STDOUT:\n{output}\nSTDERR:\n{error}"
            return output or "(no output)"
        except subprocess.TimeoutExpired:
            return "Code execution timed out (15s limit)."
        except Exception as exc:
            return f"Execution error: {exc}"

    # Run the blocking subprocess call in a thread pool to avoid blocking the event loop
    return await asyncio.to_thread(_run)


ALL_TOOLS = [web_search, python_repl]
TOOL_MAP = {t.name: t for t in ALL_TOOLS}

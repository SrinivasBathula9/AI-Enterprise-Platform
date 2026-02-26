import subprocess
import textwrap

from langchain_core.tools import tool


@tool
def web_search(query: str) -> str:
    """Search the web for up-to-date information on a topic."""
    try:
        from langchain_community.tools import DuckDuckGoSearchRun
        search = DuckDuckGoSearchRun()
        return search.run(query)
    except Exception as e:
        return f"Search failed: {e}"


@tool
def python_repl(code: str) -> str:
    """Execute Python code in a sandboxed subprocess and return stdout/stderr.
    Use for data analysis, calculations, or code validation.
    """
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
    except Exception as e:
        return f"Execution error: {e}"


ALL_TOOLS = [web_search, python_repl]
TOOL_MAP = {t.name: t for t in ALL_TOOLS}

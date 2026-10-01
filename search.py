"""Free web search (DuckDuckGo, no API key) for current prices and local rules."""


def web_context(query: str, max_results: int = 4) -> str:
    try:
        from ddgs import DDGS
    except ImportError:
        try:
            from duckduckgo_search import DDGS
        except ImportError:
            return ""
    try:
        results = DDGS().text(query, max_results=max_results) or []
        return "\n".join(f"- {r.get('title','')}: {r.get('body','')} ({r.get('href','')})" for r in results)
    except Exception:
        return ""

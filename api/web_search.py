import asyncio
from duckduckgo_search import DDGS


async def search_company(company_name: str) -> list[dict]:
    """Busca información de la empresa en DuckDuckGo."""
    query = f"{company_name} empresa información productos servicios"

    def _search():
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
        return results

    results = await asyncio.to_thread(_search)
    return results

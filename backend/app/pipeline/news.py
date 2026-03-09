"""뉴스 수집 — Brave Search API"""

import os
import httpx


async def fetch_news(query: str, count: int = 3) -> list[dict]:
    """Brave Search로 종목 뉴스 검색"""
    api_key = os.environ.get("BRAVESEARCH_API_KEY", "")
    if not api_key:
        return []

    url = "https://api.search.brave.com/res/v1/news/search"
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": api_key,
    }
    params = {
        "q": query,
        "count": count,
        "freshness": "pw",  # 지난 1주
    }

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get(url, headers=headers, params=params)
            data = resp.json()
            results = data.get("results", [])
            return [
                {
                    "title": r.get("title", ""),
                    "description": r.get("description", ""),
                    "url": r.get("url", ""),
                    "date": r.get("age", ""),
                    "source": r.get("meta_url", {}).get("hostname", ""),
                }
                for r in results[:count]
            ]
        except Exception as e:
            print(f"뉴스 검색 실패: {e}")
            return []


def build_news_query(ticker: str, name_ko: str, market: str) -> str:
    """종목별 뉴스 검색 쿼리 생성"""
    if market == "US":
        return f"{ticker} stock news"
    else:
        return f"{name_ko} 주가"

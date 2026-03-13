"""FMP API — 미국 주식 데이터 수집"""

import os
import httpx
from datetime import datetime, timedelta

FMP_KEY = os.environ.get("FINANCIALMODEL_API_KEY", "")
BASE_URL = "https://financialmodelingprep.com/stable"


async def _fetch_aftermarket_price(ticker: str, client: httpx.AsyncClient) -> dict | None:
    """시간외 최종 거래가 조회"""
    url = f"{BASE_URL}/aftermarket-trade?symbol={ticker}&apikey={FMP_KEY}"
    try:
        resp = await client.get(url)
        if resp.status_code != 200 or not resp.text.strip():
            return None
        data = resp.json()
        if isinstance(data, list) and data:
            return {
                "price": data[0]["price"],
                "timestamp": data[0].get("timestamp"),
            }
    except Exception as e:
        print(f"    ⚠️ FMP aftermarket 예외 ({ticker}): {e}")
    return None


async def fetch_us_quote(ticker: str) -> dict | None:
    """미국 종목 시세 (시간외 최종가 포함)"""
    url = f"{BASE_URL}/quote?symbol={ticker}&apikey={FMP_KEY}"
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get(url)
            if resp.status_code != 200 or not resp.text.strip():
                print(f"    ⚠️ FMP quote 실패 ({ticker}): status={resp.status_code}")
                return None
            data = resp.json()
            if isinstance(data, list) and data:
                d = data[0]

                regular_close = d["price"]
                regular_change = d["change"]
                regular_change_pct = d["changePercentage"]

                # 시간외 최종가 조회
                aftermarket = await _fetch_aftermarket_price(ticker, client)

                if aftermarket and aftermarket["price"]:
                    am_price = aftermarket["price"]
                    am_change = round(am_price - d["previousClose"], 2)
                    am_change_pct = round(am_change / d["previousClose"] * 100, 2) if d["previousClose"] else 0
                else:
                    am_price = None
                    am_change = None
                    am_change_pct = None

                return {
                    "ticker": d["symbol"],
                    # 메인 가격 = 시간외 최종가 (없으면 정규장 종가)
                    "price": am_price if am_price else regular_close,
                    "change": am_change if am_change is not None else regular_change,
                    "change_pct": am_change_pct if am_change_pct is not None else regular_change_pct,
                    "is_aftermarket": am_price is not None,
                    # 정규장 종가도 보존 (기술지표 기준)
                    "regular_close": regular_close,
                    "regular_change": regular_change,
                    "regular_change_pct": regular_change_pct,
                    "volume": d["volume"],
                    "day_high": d["dayHigh"],
                    "day_low": d["dayLow"],
                    "year_high": d["yearHigh"],
                    "year_low": d["yearLow"],
                    "prev_close": d["previousClose"],
                    "avg50": d.get("priceAvg50"),
                    "avg200": d.get("priceAvg200"),
                    "market_cap": d.get("marketCap"),
                }
            elif isinstance(data, dict) and "Error" in str(data):
                print(f"    ⚠️ FMP 에러 ({ticker}): {str(data)[:100]}")
        except Exception as e:
            print(f"    ⚠️ FMP 예외 ({ticker}): {e}")
    return None


async def fetch_us_history(ticker: str, days: int = 90) -> list[dict]:
    """미국 종목 히스토리컬 가격 (RSI/이평선 계산용)"""
    date_from = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    date_to = datetime.now().strftime("%Y-%m-%d")
    url = f"{BASE_URL}/historical-price-eod/full?symbol={ticker}&from={date_from}&to={date_to}&apikey={FMP_KEY}"
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get(url)
            if resp.status_code != 200 or not resp.text.strip():
                return []
            data = resp.json()
            if isinstance(data, list):
                return [
                    {
                        "date": d["date"],
                        "open": d["open"],
                        "high": d["high"],
                        "low": d["low"],
                        "close": d["close"],
                        "volume": d["volume"],
                    }
                    for d in data
                ]
        except Exception as e:
            print(f"    ⚠️ FMP history 예외 ({ticker}): {e}")
    return []


# --- 캐시: 시장 전체 최신 뉴스 (세션당 1회 호출) ---
_market_news_cache: list[dict] | None = None


async def fetch_market_news(limit: int = 50) -> list[dict]:
    """FMP 시장 전체 최신 뉴스 가져오기 (캐시)"""
    global _market_news_cache
    if _market_news_cache is not None:
        return _market_news_cache

    url = f"{BASE_URL}/news/stock?limit={limit}&apikey={FMP_KEY}"
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(url)
            if resp.status_code != 200 or not resp.text.strip():
                print(f"    ⚠️ FMP market news 실패: status={resp.status_code}")
                _market_news_cache = []
                return []
            data = resp.json()
            if isinstance(data, list):
                _market_news_cache = data
                print(f"    📰 FMP 시장 뉴스 {len(data)}건 로드")
                return data
        except Exception as e:
            print(f"    ⚠️ FMP market news 예외: {e}")

    _market_news_cache = []
    return []


def clear_market_news_cache():
    """캐시 초기화 (새 수집 사이클 시작 시)"""
    global _market_news_cache
    _market_news_cache = None


def filter_news_for_ticker(all_news: list[dict], ticker: str, name_ko: str, limit: int = 5) -> list[dict]:
    """시장 전체 뉴스에서 해당 종목 관련 뉴스만 필터링"""
    ticker_lower = ticker.lower()
    name_lower = name_ko.lower()

    # 종목명 변형 (영문 풀네임 매핑)
    name_variants = {
        "NVDA": ["nvidia", "엔비디아"],
        "TSLA": ["tesla", "테슬라"],
        "AAPL": ["apple", "애플"],
        "MSFT": ["microsoft", "마이크로소프트"],
        "GOOGL": ["google", "alphabet", "구글", "알파벳"],
        "AMZN": ["amazon", "아마존"],
        "META": ["meta", "facebook", "메타"],
        "AMD": ["amd", "advanced micro"],
        "SPY": ["s&p 500", "s&p500", "spy"],
        "JPM": ["jpmorgan", "jp morgan", "제이피모건"],
    }
    search_terms = [ticker_lower, name_lower]
    search_terms.extend(name_variants.get(ticker, []))

    matched = []
    for article in all_news:
        # symbol 필드 확인
        article_symbol = str(article.get("symbol", "")).upper()
        if article_symbol == ticker:
            matched.append(article)
            continue

        # 제목 + 본문에서 키워드 검색
        title = article.get("title", "").lower()
        text = article.get("text", article.get("description", "")).lower()
        combined = title + " " + text

        if any(term in combined for term in search_terms):
            matched.append(article)

    # 포맷 변환
    results = []
    for d in matched[:limit]:
        results.append({
            "title": d.get("title", ""),
            "description": d.get("text", d.get("description", "")),
            "url": d.get("url", ""),
            "date": d.get("publishedDate", ""),
            "source": d.get("site", d.get("publisher", "")),
        })

    return results

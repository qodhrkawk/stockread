"""데이터 수집 통합 — 종목별 전체 데이터 수집"""

import json
from datetime import datetime

from app.db import queries as db
from .fmp import fetch_us_quote, fetch_us_history
from .krx import fetch_kr_quote, fetch_kr_history, fetch_kr_disclosures
from .technical import calculate_indicators
from .news import fetch_news, build_news_query


async def collect_stock_data(ticker: str, name_ko: str, market: str) -> dict | None:
    """
    종목 하나의 전체 데이터 수집 → DB 캐시 저장
    
    Returns:
        {
            "ticker": str,
            "name_ko": str,
            "market": str,
            "quote": { price, change, change_pct, year_high, year_low, ... },
            "indicators": { rsi_14, sma_20, above_sma20, ... },
            "news": [{ title, description, url, date }],
            "disclosures": [{ date, title, corp }],  # 한국만
            "pct_from_high": float,  # 52주 고점 대비 %
            "collected_at": str,
        }
    """
    print(f"  📊 {name_ko} ({ticker}) 수집 중...")

    # 1. 시세
    if market == "US":
        quote = await fetch_us_quote(ticker)
        history = await fetch_us_history(ticker, days=90)
    else:
        quote = await fetch_kr_quote(ticker)
        history = await fetch_kr_history(ticker, days=90)

    if not quote:
        print(f"  ❌ {name_ko} 시세 수집 실패")
        return None

    # 2. 기술 지표
    indicators = calculate_indicators(history) if history else {}

    # 3. 뉴스
    news_query = build_news_query(ticker, name_ko, market)
    news = await fetch_news(news_query, count=3)

    # 4. 공시 (한국만)
    disclosures = []
    if market == "KR":
        disclosures = await fetch_kr_disclosures(ticker, limit=3)

    # 52주 고점 대비 %
    pct_from_high = None
    if quote.get("year_high") and quote["year_high"] > 0:
        pct_from_high = round(quote["price"] / quote["year_high"] * 100, 1)

    # 장 마감일 (trade_date)
    trade_date = None
    if market == "KR" and quote.get("trade_date"):
        trade_date = quote["trade_date"]
    elif history:
        # 미국: 히스토리 최신 날짜 = 마지막 장 마감일
        sorted_hist = sorted(history, key=lambda x: x["date"], reverse=True)
        trade_date = sorted_hist[0]["date"]

    result = {
        "ticker": ticker,
        "name_ko": name_ko,
        "market": market,
        "quote": quote,
        "indicators": indicators,
        "news": news,
        "disclosures": disclosures,
        "pct_from_high": pct_from_high,
        "trade_date": trade_date,
        "collected_at": datetime.now().isoformat(),
    }

    # DB 캐시 저장
    today = datetime.now().strftime("%Y-%m-%d")
    await db.save_price(ticker, today, json.dumps(result, ensure_ascii=False))

    print(f"  ✅ {name_ko} | {quote['price']:,} ({quote['change_pct']:+.2f}%) | RSI: {indicators.get('rsi_14', 'N/A')}")
    return result


async def collect_all_stocks() -> list[dict]:
    """MVP 전체 종목 데이터 수집"""
    stocks = await db.get_all_stocks()
    results = []

    print(f"🔄 {len(stocks)}개 종목 데이터 수집 시작")
    print()

    for stock in stocks:
        data = await collect_stock_data(
            ticker=stock["ticker"],
            name_ko=stock["name_ko"],
            market=stock["market"],
        )
        if data:
            results.append(data)

    print()
    print(f"✅ 수집 완료: {len(results)}/{len(stocks)}개 종목")
    return results

"""FMP API — 미국 주식 데이터 수집"""

import os
import httpx
from datetime import datetime, timedelta

FMP_KEY = os.environ.get("FINANCIALMODEL_API_KEY", "")
BASE_URL = "https://financialmodelingprep.com/stable"


async def fetch_us_quote(ticker: str) -> dict | None:
    """미국 종목 실시간 시세"""
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
                return {
                    "ticker": d["symbol"],
                    "price": d["price"],
                    "change": d["change"],
                    "change_pct": d["changePercentage"],
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


async def fetch_us_history(ticker: str, days: int = 60) -> list[dict]:
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

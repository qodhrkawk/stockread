"""KRX — 한국 주식 데이터 (기존 Supabase DB 읽기 전용)"""

import os
from supabase import create_client

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SECRET_KEYS", "")


def _get_sb():
    return create_client(SUPABASE_URL, SUPABASE_KEY)


async def fetch_kr_quote(stock_code: str) -> dict | None:
    """한국 종목 최신 시세 (daily_ohlcv + stock_snapshot)"""
    sb = _get_sb()

    # 최신 OHLCV
    ohlcv_res = (
        sb.table("daily_ohlcv")
        .select("*")
        .eq("stock_code", stock_code)
        .order("trade_date", desc=True)
        .limit(1)
        .execute()
    )

    # 스냅샷 (PER, PBR, 52주 고저)
    snap_res = (
        sb.table("stock_snapshot")
        .select("*")
        .eq("stock_code", stock_code)
        .order("snapshot_date", desc=True)
        .limit(1)
        .execute()
    )

    if not ohlcv_res.data:
        return None

    o = ohlcv_res.data[0]
    s = snap_res.data[0] if snap_res.data else {}

    # 전일 종가 (변동률 계산용)
    prev_res = (
        sb.table("daily_ohlcv")
        .select("close_price")
        .eq("stock_code", stock_code)
        .order("trade_date", desc=True)
        .limit(2)
        .execute()
    )
    prev_close = prev_res.data[1]["close_price"] if len(prev_res.data) >= 2 else o["close_price"]
    change = o["close_price"] - prev_close
    change_pct = (change / prev_close * 100) if prev_close else 0

    return {
        "ticker": stock_code,
        "price": o["close_price"],
        "change": change,
        "change_pct": round(change_pct, 2),
        "volume": o["volume"],
        "day_high": o["high_price"],
        "day_low": o["low_price"],
        "year_high": s.get("year_high"),
        "year_low": s.get("year_low"),
        "prev_close": prev_close,
        "per": s.get("per"),
        "pbr": s.get("pbr"),
        "roe": s.get("roe"),
        "market_cap": s.get("market_cap"),
        "trade_date": o["trade_date"],
    }


async def fetch_kr_history(stock_code: str, days: int = 90) -> list[dict]:
    """한국 종목 히스토리컬 가격 (RSI/이평선 계산용)"""
    sb = _get_sb()

    res = (
        sb.table("daily_ohlcv")
        .select("trade_date, open_price, high_price, low_price, close_price, volume")
        .eq("stock_code", stock_code)
        .order("trade_date", desc=True)
        .limit(days)
        .execute()
    )

    return [
        {
            "date": r["trade_date"],
            "open": r["open_price"],
            "high": r["high_price"],
            "low": r["low_price"],
            "close": r["close_price"],
            "volume": r["volume"],
        }
        for r in res.data
    ]


async def fetch_kr_disclosures(stock_code: str, limit: int = 5) -> list[dict]:
    """한국 종목 최근 공시"""
    sb = _get_sb()

    res = (
        sb.table("disclosure")
        .select("*")
        .eq("stock_code", stock_code)
        .order("receipt_date", desc=True)
        .limit(limit)
        .execute()
    )

    return [
        {
            "date": r["receipt_date"],
            "title": r["report_name"],
            "corp": r["corp_name"],
        }
        for r in res.data
    ]

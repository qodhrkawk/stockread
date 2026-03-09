"""기술 지표 계산 — RSI, 이평선 등 (pandas + ta)"""

import pandas as pd
import ta


def calculate_indicators(history: list[dict]) -> dict:
    """
    히스토리컬 가격 → 기술 지표 계산
    
    Args:
        history: [{"date": ..., "open": ..., "high": ..., "low": ..., "close": ..., "volume": ...}]
                 최신 날짜가 첫 번째 (desc 정렬)
    
    Returns:
        {
            "rsi_14": float,
            "sma_20": float,
            "sma_50": float,
            "above_sma20": bool,  # 현재가 > 20일 이평선
            "above_sma50": bool,
            "pct_from_high_52w": float,  # 52주 고점 대비 %
        }
    """
    if len(history) < 20:
        return {
            "rsi_14": None,
            "sma_20": None,
            "sma_50": None,
            "above_sma20": None,
            "above_sma50": None,
        }

    # DataFrame 생성 (오래된 순 정렬)
    df = pd.DataFrame(history[::-1])
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df["high"] = pd.to_numeric(df["high"], errors="coerce")
    df["low"] = pd.to_numeric(df["low"], errors="coerce")

    current_price = df["close"].iloc[-1]

    # RSI (14)
    rsi_series = ta.momentum.RSIIndicator(df["close"], window=14).rsi()
    rsi_14 = round(rsi_series.iloc[-1], 1) if not pd.isna(rsi_series.iloc[-1]) else None

    # SMA 20
    sma_20_series = ta.trend.SMAIndicator(df["close"], window=20).sma_indicator()
    sma_20 = round(sma_20_series.iloc[-1], 2) if not pd.isna(sma_20_series.iloc[-1]) else None

    # SMA 50 (데이터 충분할 때만)
    sma_50 = None
    if len(df) >= 50:
        sma_50_series = ta.trend.SMAIndicator(df["close"], window=50).sma_indicator()
        sma_50 = round(sma_50_series.iloc[-1], 2) if not pd.isna(sma_50_series.iloc[-1]) else None

    return {
        "rsi_14": rsi_14,
        "sma_20": sma_20,
        "sma_50": sma_50,
        "above_sma20": bool(current_price > sma_20) if sma_20 else None,
        "above_sma50": bool(current_price > sma_50) if sma_50 else None,
    }

"""랜딩 페이지용 데이터 생성 — DB에서 가격 + 리포트 읽어서 JSON 저장"""

import json
import os
from datetime import datetime
from app.db.database import get_db

# 랜딩에 표시할 종목 5개
PREVIEW_STOCKS = [
    {"ticker": "NVDA",   "tab_key": "nvda"},
    {"ticker": "TSLA",   "tab_key": "tsla"},
    {"ticker": "005930", "tab_key": "samsung"},
    {"ticker": "AAPL",   "tab_key": "aapl"},
    {"ticker": "000660", "tab_key": "hynix"},
]

RISK_MAP = {"안정": "safe", "중립": "mid", "공격": "aggr"}
OUTPATH = os.path.expanduser("~/stockread/web/public/landing-data.json")


def _parse_report_sections(text: str) -> dict:
    """리포트 텍스트에서 4개 섹션 파싱
    
    형식:
    1️⃣ 지금 어디쯤이에요?
    • ...
    2️⃣ 차트가 말해주는 것
    • ...
    3️⃣ 무슨 일이 있었나요?
    • ...
    4️⃣ 이렇게 보시면 돼요 (...)
    ...
    """
    sections = {"section1": "", "section2": "", "section3": "", "interpret": ""}
    
    markers = [
        ("section1", "1️⃣"),
        ("section2", "2️⃣"),
        ("section3", "3️⃣"),
        ("interpret", "4️⃣"),
    ]
    
    for i, (key, marker) in enumerate(markers):
        start = text.find(marker)
        if start < 0:
            continue
        
        # 마커 줄 제목 스킵 → 다음 줄부터
        newline = text.find("\n", start)
        if newline < 0:
            continue
        content_start = newline + 1
        
        # 다음 마커까지
        end = len(text)
        for j in range(i + 1, len(markers)):
            next_pos = text.find(markers[j][1], content_start)
            if next_pos >= 0:
                end = next_pos
                break
        
        sections[key] = text[content_start:end].strip()
    
    return sections


async def generate_and_save():
    """price_cache + daily_reports → landing-data.json"""
    today = datetime.now().strftime("%Y-%m-%d")
    result = {"date": today, "stocks": {}}
    
    db = await get_db()
    try:
        for s in PREVIEW_STOCKS:
            ticker = s["ticker"]
            tab_key = s["tab_key"]
            
            # 1) price_cache에서 가격
            cursor = await db.execute(
                "SELECT data_json FROM price_cache WHERE ticker = ? AND price_date = ?",
                (ticker, today),
            )
            row = await cursor.fetchone()
            if not row:
                print(f"  ⚠️ {ticker} 가격 없음, 스킵")
                continue
            
            price_data = json.loads(row[0])
            q = price_data["quote"]
            market = price_data["market"]
            
            if market == "US":
                price_str = f"${q['price']:,.2f}"
            else:
                price_str = f"{q['price']:,}원"
            
            # 52주 고점 대비
            pct_from_high = 0
            if q.get("year_high") and q["year_high"] > 0:
                pct_from_high = round(q["price"] / q["year_high"] * 100, 1)
            
            # 장 마감일
            trade_date = price_data.get("trade_date", "")
            if not trade_date and market == "US":
                # fallback: price_date 사용
                trade_date = today

            stock_entry = {
                "ticker": ticker,
                "name": price_data["name_ko"],
                "flag": "🇺🇸" if market == "US" else "🇰🇷",
                "price": price_str,
                "change": f"{q['change_pct']:+.1f}%",
                "positive": q["change_pct"] >= 0,
                "high52": f"{pct_from_high}%",
                "tradeDate": trade_date,
                "sections": {},
            }
            
            # 2) daily_reports에서 성향별 리포트
            for risk_ko, risk_key in RISK_MAP.items():
                cursor = await db.execute(
                    "SELECT report_json FROM daily_reports WHERE ticker = ? AND report_date = ? AND risk_type = ?",
                    (ticker, today, risk_ko),
                )
                rrow = await cursor.fetchone()
                if rrow:
                    report_data = json.loads(rrow[0])
                    text = report_data.get("text", "")
                    stock_entry["sections"][risk_key] = _parse_report_sections(text)
                    print(f"  ✅ {price_data['name_ko']} ({risk_ko})")
                else:
                    stock_entry["sections"][risk_key] = {
                        "section1": "", "section2": "", "section3": "", "interpret": ""
                    }
                    print(f"  ⚠️ {ticker} ({risk_ko}) 리포트 없음")
            
            result["stocks"][tab_key] = stock_entry
    
    finally:
        await db.close()
    
    with open(OUTPATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 landing-data.json 저장 ({len(result['stocks'])}개 종목)")

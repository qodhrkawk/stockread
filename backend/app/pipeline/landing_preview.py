"""랜딩 페이지용 실시간 리포트 프리뷰 데이터 생성"""

import json
import os
from datetime import datetime
from openai import AsyncOpenAI
from app.db.database import init_db
from app.pipeline.collector import collect_stock_data

client = AsyncOpenAI(
    base_url="http://127.0.0.1:8317/v1",
    api_key="sk-my-claude-proxy",
)
MODEL = "claude-opus-4-6"

PREVIEW_STOCKS = [
    {"ticker": "NVDA",   "name_ko": "엔비디아",   "market": "US",  "tab_key": "nvda"},
    {"ticker": "TSLA",   "name_ko": "테슬라",    "market": "US",  "tab_key": "tsla"},
    {"ticker": "005930", "name_ko": "삼성전자",   "market": "KR",  "tab_key": "samsung"},
    {"ticker": "AAPL",   "name_ko": "애플",      "market": "US",  "tab_key": "aapl"},
    {"ticker": "000660", "name_ko": "SK하이닉스",  "market": "KR",  "tab_key": "hynix"},
]

RISK_TYPES = ["안정", "중립", "공격"]
RISK_MAP = {"안정": "safe", "중립": "mid", "공격": "aggr"}

LANDING_PROMPT = """너는 "주읽이" 서비스의 AI야. 랜딩 페이지 프리뷰용으로 아주 짧게 답변해.

반드시 아래 4개 섹션으로 답변해. 각 섹션은 1~2문장만. 섹션 구분을 꼭 지켜.

[위치]
종가, 등락률, 52주 고점 대비 위치를 1~2문장으로

[차트]
RSI, 이평선 해석을 1~2문장으로

[이슈]
최근 뉴스/이슈 1~2문장으로

[해석]
성향에 맞는 투자 해석 2~3문장

규칙:
- 해요체, 친근하게
- 전문 용어 쓰면 바로 풀어서 설명
- 매수/매도 추천 금지
- 짧게! 각 섹션 최대 2문장"""


def _parse_sections(text: str) -> dict:
    """[위치] [차트] [이슈] [해석] 파싱"""
    result = {"section1": "", "section2": "", "section3": "", "interpret": ""}
    
    markers = {
        "section1": ["[위치]"],
        "section2": ["[차트]"],
        "section3": ["[이슈]"],
        "interpret": ["[해석]"],
    }
    
    order = ["section1", "section2", "section3", "interpret"]
    
    for i, key in enumerate(order):
        marker = markers[key][0]
        start = text.find(marker)
        if start < 0:
            continue
        start += len(marker)
        
        # 다음 마커까지
        end = len(text)
        for j in range(i + 1, len(order)):
            next_marker = markers[order[j]][0]
            next_pos = text.find(next_marker, start)
            if next_pos >= 0:
                end = next_pos
                break
        
        result[key] = text[start:end].strip()
    
    return result


async def _generate_landing_report(data: dict, risk_type: str) -> dict:
    """랜딩용 짧은 리포트 생성"""
    q = data["quote"]
    ind = data.get("indicators", {})
    news = data.get("news", [])
    
    risk_labels = {"안정": "🛡 안정형", "중립": "⚖️ 중립형", "공격": "🔥 공격형"}
    
    if data["market"] == "US":
        price_str = f"${q['price']:,.2f}"
    else:
        price_str = f"{q['price']:,}원"
    
    news_text = "\n".join(f"- {n['title']}" for n in news[:2]) if news else "최근 주요 뉴스 없음"
    
    user_msg = f"""종목: {data['name_ko']} ({data['ticker']})
종가: {price_str} ({q['change_pct']:+.2f}%)
52주 고점 대비: {data.get('pct_from_high', 'N/A')}%
RSI(14): {ind.get('rsi_14', 'N/A')}
20일 이평선: 현재가 {'위' if ind.get('above_sma20') else '아래'}
최근 뉴스:
{news_text}
유저 성향: {risk_labels.get(risk_type, '⚖️ 중립형')}"""

    resp = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": LANDING_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        max_tokens=400,
        temperature=0.7,
    )
    
    text = resp.choices[0].message.content.strip()
    return _parse_sections(text)


async def generate_landing_data() -> dict:
    await init_db()
    today = datetime.now().strftime("%Y-%m-%d")
    result = {"date": today, "stocks": {}}

    for stock_info in PREVIEW_STOCKS:
        ticker = stock_info["ticker"]
        name = stock_info["name_ko"]
        market = stock_info["market"]
        tab_key = stock_info["tab_key"]

        print(f"  📊 {name} ({ticker}) 수집 중...")
        data = await collect_stock_data(ticker, name, market)
        if not data:
            print(f"  ❌ {name} 스킵")
            continue

        q = data["quote"]
        if market == "US":
            price_str = f"${q['price']:,.2f}"
        else:
            price_str = f"{q['price']:,}원"

        sections_by_risk = {}
        for risk_type in RISK_TYPES:
            risk_key = RISK_MAP[risk_type]
            try:
                report = await _generate_landing_report(data, risk_type)
                sections_by_risk[risk_key] = report
                print(f"    ✅ {risk_type} 완료")
            except Exception as e:
                print(f"    ⚠️ {risk_type} 실패: {e}")
                sections_by_risk[risk_key] = {"section1": "", "section2": "", "section3": "", "interpret": ""}

        result["stocks"][tab_key] = {
            "ticker": ticker,
            "name": name,
            "flag": "🇺🇸" if market == "US" else "🇰🇷",
            "price": price_str,
            "change": f"{q['change_pct']:+.1f}%",
            "positive": q["change_pct"] >= 0,
            "high52": f"{data.get('pct_from_high', 0)}%",
            "sections": sections_by_risk,
        }
        print(f"  ✅ {name} 완료")

    return result


async def generate_and_save():
    data = await generate_landing_data()
    outpath = os.path.expanduser("~/stockread/web/public/landing-data.json")
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n📄 저장: {outpath}")
    print(f"📅 날짜: {data['date']}, 📊 종목: {len(data['stocks'])}개")

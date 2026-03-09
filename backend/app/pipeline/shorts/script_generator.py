"""쇼츠 스크립트 생성 — 풍부한 데이터 + 개선된 프롬프트"""
import json
import logging
from datetime import date

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

client = AsyncOpenAI(
    base_url="http://127.0.0.1:8317/v1",
    api_key="sk-my-claude-proxy",
)
MODEL = "claude-sonnet-4-20250514"

BASE_SYSTEM_PROMPT = """너는 주식 초보(주린이)를 위한 YouTube Shorts 나레이션 작가야.

## 말투
- 존댓말 (해요체)
- 친구가 쉽게 설명해주는 느낌
- 짧은 문장 위주 (한 문장 40자 이내)

## 절대 금지
- "지정학적", "밸류에이션", "시총", "극명하게" 등 전문 용어 그대로 사용 금지
  → 반드시 풀어서 설명 (예: "시가총액" → "회사의 전체 가치")
- 매수/매도 추천, 목표가 제시
- "반드시", "확실히" 등 단정 표현

## 필수 규칙
- 수치 반드시 포함 (%, 원, 달러)
- RSI, SMA 등 지표 쓸 때 바로 풀어서 설명
  예: "RSI가 72예요. 70 넘으면 과열 신호로 봐요"
- summary와 detail 내용이 겹치면 안 됨
  - summary = 전체 시장 분위기 (숲)
  - detail = 개별 종목 분석 (나무)

## 스크립트 구조 & 문장 수 (엄격히 지킬 것)

① hook (5초, 2문장)
   - 가장 임팩트 있는 숫자/사건으로 시작
   - 질문형 필수: "~했는데, 왜 그런 걸까요?"

② summary (10초, 3문장)
   - 시장 전체 분위기만 (개별 종목 X)
   - 어떤 섹터가 올랐고 빠졌는지

③ detail (25초, 6문장 이상)
   - 핵심 종목 2~3개, 종목당 최소 2문장
   - 종목당 반드시: 가격 + 등락% + 왜 올랐는지/빠졌는지 이유 1줄
   - 이유 없이 숫자만 나열 금지
   - 기술지표(RSI, SMA) 언급 시 쉽게 풀어서
   - 여기가 전체의 40% — 가장 길고 구체적이어야 함
   - 좋은 예: "현대모비스는 12만원대로 10% 넘게 급락했어요. 자동차 부품 수출 차질 우려가 반영된 거예요."
   - 나쁜 예: "현대모비스는 10% 넘게 급락했고, 네이버와 카카오도 5% 이상 빠졌어요."

④ context (15초, 3문장)
   - 왜 이런 일이 벌어졌는지 배경/원인
   - 초보자가 인과관계를 이해할 수 있게

⑤ closing (5초, 2문장)
   - 앞으로 어떻게 볼 수 있는지
   - "~해 보여요", "지켜보는 게 좋겠어요" 톤

## 분량 (매우 중요!!!)
- tts_script: 350~450자 (한국어 기준)
- 300자 미만 절대 금지
- 합계 최소 16문장
- detail의 tts_text가 가장 길어야 함

## 출력 형식
JSON만 출력. 다른 텍스트 없이.

⚠️ 절대 규칙: scenes에 "text" 필드를 넣지 마세요. 대신:
- hook → headline, number
- summary → sectors
- detail → cards
- context → flow
- closing → message
이 필드들을 반드시 사용하세요.

중요:
- tts_script = 모든 scenes의 tts_text를 순서대로 이어붙인 전체 나레이션
- tts_script와 scenes.tts_text 내용이 불일치하면 안 됨

{
  "date": "YYYY-MM-DD",
  "title": "영상 제목 (후킹용, 15자 이내)",
  "tts_script": "전체 나레이션 (350~450자)",
  "scenes": [
    {"label": "hook", "text": "화면 문구 (줄바꿈)", "tts_text": "TTS 2문장", "duration": 5},
    {"label": "summary", "text": "화면 문구", "tts_text": "TTS 3문장", "duration": 10},
    {"label": "detail", "text": "종목별 수치", "tts_text": "TTS 6문장 이상", "duration": 25},
    {"label": "context", "text": "배경 키워드", "tts_text": "TTS 3문장", "duration": 15},
    {"label": "closing", "text": "마무리", "tts_text": "TTS 2문장", "duration": 5}
  ]
}

## scenes.text 규칙 (화면용)
- 핵심 키워드/수치만 (TTS 전체 넣지 않음)
- 줄바꿈(\\n)으로 구분, 3줄 이내
- hook: 핵심 숫자 크게 (예: "-8%")
- detail: 종목별 한 줄씩 "삼성전자 -8% · 170,200원"
- 숫자와 등락률 필수 포함"""

MARKET_CONTEXT = {
    "US": {
        "intro": "어젯밤 미국 증시를 요약해줘.",
        "flag": "🇺🇸",
        "label": "미국 증시",
    },
    "KR": {
        "intro": "오늘 한국 증시를 요약해줘.",
        "flag": "🇰🇷",
        "label": "한국 증시",
    },
}

US_TICKERS = ["NVDA", "TSLA", "AAPL", "MSFT", "GOOGL", "AMZN", "META", "AMD", "SPY", "JPM"]
KR_TICKERS = ["005930", "000660", "373220", "035420", "035720", "006400", "012330"]


def format_stock_data(item: dict, market: str) -> str:
    """종목 데이터를 프롬프트용 텍스트로 포맷"""
    data = item.get("data_json", {})
    if isinstance(data, str):
        data = json.loads(data)

    quote = data.get("quote", {})
    indicators = data.get("indicators", {})
    ticker = item.get("ticker", "")
    name = quote.get("name", data.get("name_ko", ticker))

    # 가격
    price = quote.get("price", 0)
    change_pct = quote.get("changesPercentage", quote.get("change_pct", 0))
    change = quote.get("change", 0)
    volume = quote.get("volume", 0)

    if market == "KR":
        price_str = f"{int(price):,}원"
        change_str = f"{int(change):+,}원"
    else:
        price_str = f"${price:,.2f}"
        change_str = f"${change:+,.2f}"

    lines = [f"### {name} ({ticker})"]
    lines.append(f"- 종가: {price_str} ({change_pct:+.2f}%) {change_str}")
    lines.append(f"- 거래량: {volume:,}")

    # 52주 고저
    year_high = quote.get("year_high", 0)
    year_low = quote.get("year_low", 0)
    pct_from_high = data.get("pct_from_high", 0)
    if year_high:
        lines.append(f"- 52주 고점: {year_high:,} (현재 고점 대비 {pct_from_high:.1f}%)")

    # 기술지표
    rsi = indicators.get("rsi_14")
    sma20 = indicators.get("sma_20")
    sma50 = indicators.get("sma_50")
    if rsi is not None:
        lines.append(f"- RSI(14): {rsi:.1f}")
    if sma20 is not None:
        above20 = "위" if indicators.get("above_sma20") else "아래"
        lines.append(f"- 20일 이평선: {sma20:,.0f} (현재가 {above20})")
    if sma50 is not None:
        above50 = "위" if indicators.get("above_sma50") else "아래"
        lines.append(f"- 50일 이평선: {sma50:,.0f} (현재가 {above50})")

    # PER, PBR
    per = quote.get("per")
    pbr = quote.get("pbr")
    if per:
        lines.append(f"- PER: {per}")
    if pbr:
        lines.append(f"- PBR: {pbr}")

    # 뉴스 (최대 3개)
    news = data.get("news", [])[:3]
    if news:
        lines.append("- 뉴스:")
        for n in news:
            lines.append(f"  · {n.get('title', '')[:80]}")

    # 공시 (최대 2개)
    disclosures = data.get("disclosures", [])[:2]
    if disclosures:
        lines.append("- 공시:")
        for d in disclosures:
            lines.append(f"  · {d.get('title', d.get('report_nm', ''))[:80]}")

    return "\n".join(lines)


async def generate_shorts_script(
    price_data: list[dict],
    target_date: date | None = None,
    market: str = "US",
) -> dict:
    """시장별 쇼츠 스크립트 JSON 생성"""
    if target_date is None:
        target_date = date.today()

    ctx = MARKET_CONTEXT[market]

    # 해당 시장 종목만 필터링
    filtered = []
    for item in price_data:
        ticker = item.get("ticker", "")
        is_kr = ticker.isdigit()
        if (market == "KR" and is_kr) or (market == "US" and not is_kr):
            filtered.append(item)

    if not filtered:
        raise RuntimeError(f"{ctx['label']} 가격 데이터가 없습니다.")

    # 풍부한 종목 데이터 텍스트
    stock_texts = []
    for item in filtered:
        stock_texts.append(format_stock_data(item, market))

    system_prompt = BASE_SYSTEM_PROMPT + f"\n\n## 이번 영상\n{ctx['flag']} {ctx['intro']}\n{ctx['label']} 데이터만 다뤄."

    user_prompt = f"""오늘 날짜: {target_date.isoformat()}

## {ctx['flag']} {ctx['label']} 주요 종목 데이터

{chr(10).join(stock_texts)}

위 데이터를 기반으로 쇼츠 스크립트 JSON을 생성해줘.
기술지표, 뉴스, 52주 고저 등을 활용해서 풍부하게 작성해.
JSON만 출력해. 다른 텍스트 없이."""

    response = await client.chat.completions.create(
        model=MODEL,
        max_tokens=2048,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    text = response.choices[0].message.content.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]

    script = json.loads(text)
    script["date"] = target_date.isoformat()
    script["market"] = market

    # Claude가 구조화 필드를 문자열로 줄 수 있으므로 후처리
    for scene in script.get("scenes", []):
        # sectors: 문자열 → 배열
        if "sectors" in scene and isinstance(scene["sectors"], str):
            lines = [l.strip() for l in scene["sectors"].split("\n") if l.strip()]
            scene["sectors"] = [
                {"name": l, "direction": "down" if any(w in l for w in ["하락", "급락", "↓", "빠", "폭락", "-", "약세"]) else "up"}
                for l in lines
            ]
        # cards: 문자열 → 배열
        if "cards" in scene and isinstance(scene["cards"], str):
            lines = [l.strip() for l in scene["cards"].split("\n") if l.strip()]
            cards = []
            for l in lines:
                parts = l.replace("·", "|").replace("•", "|").split("|")
                name_change = parts[0].strip()
                price = parts[1].strip() if len(parts) > 1 else ""
                # "삼성전자 -9.6%" 파싱
                tokens = name_change.rsplit(" ", 1)
                name = tokens[0].strip()
                change = tokens[1].strip() if len(tokens) > 1 else ""
                cards.append({"name": name, "price": price, "change": change, "indicators": []})
            scene["cards"] = cards
        # flow: 문자열 → 배열
        if "flow" in scene and isinstance(scene["flow"], str):
            scene["flow"] = [l.strip() for l in scene["flow"].split("\n") if l.strip()]
        # message: 줄바꿈 유지
        if "message" in scene and isinstance(scene["message"], str):
            scene["message"] = scene["message"].replace("\n", "\n")

    total_sec = sum(s["duration"] for s in script["scenes"])
    script["audioDurationSec"] = max(30, min(70, total_sec))

    logger.info(
        f"쇼츠 스크립트 생성 [{market}]: {script['title']} "
        f"({len(script['tts_script'])}자, {script['audioDurationSec']}초)"
    )
    return script

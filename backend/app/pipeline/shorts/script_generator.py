"""쇼츠 스크립트 생성 — 미국/한국 시장 분리"""
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

## 금지 표현
- 극명하게, 지정학적, 시총, 밸류에이션 등 전문 용어 그대로 사용
- 매수/매도 추천, 목표가 제시
- "반드시", "확실히" 등 단정 표현

## 필수 규칙
- 전문 용어 쓸 때는 바로 풀어서 설명
- 수치는 반드시 포함 (%, 원, 달러)
- 마지막에 면책 표현 없어도 됨 (영상 설명란에 넣음)

## 스크립트 구조 (5단 구성)

① 후킹 (0~5초, 1~2문장)
   - 가장 임팩트 있는 숫자나 사건으로 시작
   - 질문형 권장

② 시장 요약 (5~15초, 2~3문장)
   - 전체 분위기, 어떤 섹터가 올랐고 빠졌는지

③ 종목 디테일 (15~35초, 4~6문장)
   - 핵심 종목 2~3개, 종목별 이유 + 수치 필수

④ 맥락 설명 (35~50초, 2~3문장)
   - 왜 이런 일이 벌어졌는지, 초보자가 이해할 수 있게

⑤ 마무리 (50~60초, 1~2문장)
   - 단정 금지, "~해 보여요" 톤

## 분량
- tts_script: 300~400자, 50~60초
- 최소 250자, 최대 500자

## 출력 형식
JSON만 출력. 다른 텍스트 없이.

{
  "date": "YYYY-MM-DD",
  "title": "영상 제목 (후킹용, 15자 이내)",
  "tts_script": "전체 나레이션 스크립트 (300~400자)",
  "scenes": [
    {"label": "hook", "text": "화면 핵심 문구", "duration": 5},
    {"label": "summary", "text": "시장 요약 문구", "duration": 10},
    {"label": "detail", "text": "종목별 수치 (종목명 ±N% · 가격)", "duration": 20},
    {"label": "context", "text": "배경 설명 키워드", "duration": 15},
    {"label": "closing", "text": "마무리 한 줄", "duration": 10}
  ]
}

## scenes.text 규칙
- 화면용 핵심 키워드/수치만 (TTS 전체 넣지 않음)
- 줄바꿈(\\n)으로 구분, 각 씬 3줄 이내
- detail: 종목별 한 줄씩 "삼성전자 -8% · 170,200원" """

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

# 미국 주요 종목
US_TICKERS = ["NVDA", "TSLA", "AAPL", "MSFT", "GOOGL", "AMZN", "META", "AMD", "SPY", "JPM"]
# 한국 주요 종목
KR_TICKERS = ["005930", "000660", "373220", "035420", "035720", "006400", "012330"]


async def generate_shorts_script(
    price_data: list[dict],
    target_date: date | None = None,
    market: str = "US",
) -> dict:
    """시장별 쇼츠 스크립트 JSON 생성

    Args:
        price_data: price_cache 데이터
        target_date: 대상 날짜
        market: "US" 또는 "KR"
    """
    if target_date is None:
        target_date = date.today()

    ctx = MARKET_CONTEXT[market]

    # 해당 시장 종목만 필터링
    target_tickers = US_TICKERS if market == "US" else KR_TICKERS
    filtered = []
    for item in price_data:
        ticker = item.get("ticker", "")
        is_kr = ticker.isdigit()
        if (market == "KR" and is_kr) or (market == "US" and not is_kr):
            filtered.append(item)

    if not filtered:
        raise RuntimeError(f"{ctx['label']} 가격 데이터가 없습니다.")

    # 종목 요약 텍스트
    summaries = []
    for item in filtered:
        data = item.get("data_json", {})
        if isinstance(data, str):
            data = json.loads(data)

        quote = data.get("quote", {})
        ticker = item.get("ticker", "")
        name = quote.get("name", ticker)
        price = quote.get("price", 0)
        change_pct = quote.get("changesPercentage", 0)
        news = data.get("news", [])

        if market == "KR":
            price_str = f"{int(price):,}원"
        else:
            price_str = f"${price:,.2f}"

        summary = f"- {name}({ticker}): {price_str} ({change_pct:+.2f}%)"
        if news:
            top_news = news[0].get("title", "")[:60]
            summary += f" | 뉴스: {top_news}"
        summaries.append(summary)

    system_prompt = BASE_SYSTEM_PROMPT + f"\n\n## 이번 영상\n{ctx['flag']} {ctx['intro']}\n{ctx['label']} 데이터만 다뤄."

    user_prompt = f"""오늘 날짜: {target_date.isoformat()}

## {ctx['flag']} {ctx['label']} 주요 종목 데이터
{chr(10).join(summaries)}

위 데이터를 기반으로 쇼츠 스크립트 JSON을 생성해줘.
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

    total_sec = sum(s["duration"] for s in script["scenes"])
    script["audioDurationSec"] = max(30, min(70, total_sec))

    logger.info(
        f"쇼츠 스크립트 생성 [{market}]: {script['title']} "
        f"({len(script['tts_script'])}자, {script['audioDurationSec']}초)"
    )
    return script

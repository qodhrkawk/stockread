"""쇼츠 스크립트 생성 — CLIAPIProxy (OpenAI compatible) 경유 Claude"""
import json
import logging
from datetime import date

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

# 기존 리포트 생성기와 동일한 프록시 설정
client = AsyncOpenAI(
    base_url="http://127.0.0.1:8317/v1",
    api_key="sk-my-claude-proxy",
)
MODEL = "claude-sonnet-4-20250514"

SYSTEM_PROMPT = """너는 유튜브 쇼츠용 증시 요약 스크립트 작성 AI야.

## 규칙
- 존댓말(해요체) 사용
- 주린이(주식 초보)가 이해할 수 있는 쉬운 말
- 매수/매도 추천 금지
- 30~60초 분량 (tts_script 기준 150~300자)
- 후킹 되는 제목 (짧고 임팩트 있게)
- highlights는 2~3개 (핵심만)

## 출력 JSON 형식 (이 형식만 출력, 다른 텍스트 없이)
{
  "date": "YYYY-MM-DD",
  "title": "후킹 제목",
  "market_summary": "시장 한 줄 요약",
  "highlights": ["핵심1", "핵심2", "핵심3"],
  "interpretation": "시장 해석 (2~3문장)",
  "tts_script": "TTS용 전체 스크립트 (자연스러운 말투, 150~300자)"
}"""


async def generate_shorts_script(
    price_data: list[dict],
    target_date: date | None = None,
) -> dict:
    """price_cache 데이터를 기반으로 쇼츠 스크립트 JSON 생성"""
    if target_date is None:
        target_date = date.today()

    # 주요 종목 요약 만들기
    summaries = []
    for item in price_data:
        data = item.get("data_json", {})
        if isinstance(data, str):
            data = json.loads(data)

        quote = data.get("quote", {})
        ticker = item.get("ticker", "")
        name = quote.get("name", ticker)
        price = quote.get("price", 0)
        change_pct = quote.get("changesPercentage", 0)
        news = data.get("news", [])

        summary = f"- {name}({ticker}): ${price:,.2f} ({change_pct:+.2f}%)"
        if news:
            top_news = news[0].get("title", "")[:60]
            summary += f" | 뉴스: {top_news}"
        summaries.append(summary)

    user_prompt = f"""오늘 날짜: {target_date.isoformat()}

## 주요 종목 데이터
{chr(10).join(summaries)}

위 데이터를 기반으로 쇼츠 스크립트 JSON을 생성해줘.
JSON만 출력해. 다른 텍스트 없이."""

    response = await client.chat.completions.create(
        model=MODEL,
        max_tokens=1024,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )

    # 응답에서 JSON 추출
    text = response.choices[0].message.content.strip()
    # ```json ... ``` 래핑 제거
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]

    script = json.loads(text)
    script["date"] = target_date.isoformat()

    logger.info(f"쇼츠 스크립트 생성 완료: {script['title']}")
    return script

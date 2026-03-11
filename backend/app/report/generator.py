"""AI 리포트 생성 — CLIAPIProxy (OpenAI compatible) 경유 Claude"""

import json
from openai import AsyncOpenAI

# CLIAPIProxy 설정
client = AsyncOpenAI(
    base_url="http://127.0.0.1:8317/v1",
    api_key="sk-my-claude-proxy",
)
MODEL = "claude-opus-4-6"


SYSTEM_PROMPT = """너는 "주읽이"라는 서비스의 AI 투자 해석 도우미야.
주식 초보자(주린이)를 위해 종목 데이터를 쉽고 친근하게 해석해줘.

## 규칙
- 해요체 사용 (친근하게)
- 전문 용어 쓸 때는 바로 풀어서 설명
- 매수/매도 추천 절대 금지
- "리스크 높음", "변동성 가능성", "참고 정보" 등 표현 사용
- 단정적 표현 금지 ("반드시", "확실히" 등)
- 제공된 숫자만 인용하고, 직접 계산하지 마 (예: 차이 금액, 비율 등을 새로 계산하지 마)

## 성향별 톤
- 안정형(🛡): 보수적. 리스크 강조, 분할/관망 권유
- 중립형(⚖️): 균형. 양면 분석, 조건부 접근  
- 공격형(🔥): 적극적. 기회 강조, 단기 모멘텀 언급

## 출력 형식
반드시 아래 4개 섹션으로 답변해. 마크다운이나 특수 포맷 없이 텔레그램 텍스트로 보낼 수 있는 형태로.

1️⃣ 지금 어디쯤이에요?
• (현재가, 등락률, 52주 고점 대비 위치)

2️⃣ 차트가 말해주는 것
• (RSI 해석, 이평선 위치 해석)

3️⃣ 무슨 일이 있었나요?
• (최근 뉴스/공시 요약, 호재/악재 표시)

4️⃣ 이렇게 보시면 돼요 ({성향} 기준)
(성향에 맞는 해석 2~3문장)"""


def _build_user_prompt(data: dict, risk_type: str) -> str:
    """수집 데이터 → 유저 프롬프트"""
    q = data["quote"]
    ind = data.get("indicators", {})
    news = data.get("news", [])
    disclosures = data.get("disclosures", [])

    risk_labels = {"안정": "🛡 안정형", "중립": "⚖️ 중립형", "공격": "🔥 공격형"}
    risk_label = risk_labels.get(risk_type, "⚖️ 중립형")

    # 가격 포맷
    if data["market"] == "US":
        price_str = f"${q['price']:,.2f}"
        change_str = f"${q['change']:+,.2f}"
        price_label = "시간외 최종가" if q.get("is_aftermarket") else "종가"
    else:
        price_str = f"{q['price']:,}원"
        change_str = f"{q['change']:+,}원"
        price_label = "종가"

    # 뉴스 텍스트
    news_text = ""
    if news:
        for i, n in enumerate(news, 1):
            news_text += f"\n  {i}. {n['title']} ({n.get('date', '')})"
    else:
        news_text = "\n  최근 주요 뉴스 없음"

    # 공시 텍스트
    disc_text = ""
    if disclosures:
        for d in disclosures:
            disc_text += f"\n  - {d['date']}: {d['title']}"

    prompt = f"""[종목 정보]
종목: {data['name_ko']} ({data['ticker']})
시장: {"미국" if data['market'] == 'US' else "한국"}

[시세]
{price_label}: {price_str} ({q['change_pct']:+.2f}%)
전일비: {change_str}
52주 고점 대비: {data.get('pct_from_high', 'N/A')}%

[기술 지표]
RSI(14): {ind.get('rsi_14', 'N/A')}
20일 이평선: {ind.get('sma_20', 'N/A')} (현재가 {'위' if ind.get('above_sma20') else '아래'})
50일 이평선: {ind.get('sma_50', 'N/A')} (현재가 {'위' if ind.get('above_sma50') else '아래'})

[최근 뉴스]{news_text}

[유저 성향]
{risk_label}

위 데이터를 바탕으로 리포트를 작성해줘."""

    if disc_text:
        prompt += f"\n\n[최근 공시]{disc_text}"

    return prompt


async def generate_report(data: dict, risk_type: str) -> str:
    """종목 데이터 → AI 리포트 텍스트 생성"""
    user_prompt = _build_user_prompt(data, risk_type)

    response = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=1500,
        temperature=0.7,
    )

    return response.choices[0].message.content


def format_report_message(
    data: dict, risk_type: str, report_text: str
) -> str:
    """최종 텔레그램 메시지 포맷"""
    from datetime import datetime

    q = data["quote"]
    risk_emojis = {"안정": "🛡", "중립": "⚖️", "공격": "🔥"}
    risk_labels = {"안정": "안정형", "중립": "중립형", "공격": "공격형"}
    risk_emoji = risk_emojis.get(risk_type, "⚖️")
    risk_label = risk_labels.get(risk_type, "중립형")

    # 장 마감일 (trade_date)
    trade_date = data.get("trade_date")
    if trade_date:
        # "2026-03-07" → "03/07"
        try:
            td = datetime.strptime(trade_date, "%Y-%m-%d")
            date_suffix = td.strftime("%m/%d")
        except ValueError:
            date_suffix = trade_date
    else:
        date_suffix = datetime.now().strftime("%m/%d")

    # 가격 + 표기
    if data["market"] == "US":
        if q.get("is_aftermarket"):
            price_label = f"{date_suffix} 시간외"
        else:
            price_label = f"{date_suffix} 종가"
        price_str = f"${q['price']:,.2f} ({q['change_pct']:+.2f}%) · {price_label}"
        flag = "🇺🇸"
    else:
        price_str = f"{q['price']:,}원 ({q['change_pct']:+.2f}%) · {date_suffix} 종가"
        flag = "🇰🇷"

    # 등락 색상 이모지
    color = "💚" if q["change_pct"] >= 0 else "❤️"

    today = datetime.now().strftime("%Y.%m.%d")

    msg = (
        f"📊 {today} 주읽이 리포트\n"
        f"\n"
        f"━━━━━━━━━━━━━━━\n"
        f"{color} {data['name_ko']} ({data['ticker']})\n"
        f"{flag} {price_str}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"\n"
        f"{report_text}\n"
        f"\n"
        f"⚠️ 이 리포트는 참고용이에요.\n"
        f"투자 판단은 본인이 직접 해주세요!"
    )

    return msg

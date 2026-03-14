"""AI 리포트 생성 — CLIAPIProxy (OpenAI compatible) 경유 Claude"""

import json
from openai import AsyncOpenAI

# CLIAPIProxy 설정
client = AsyncOpenAI(
    base_url="http://127.0.0.1:8317/v1",
    api_key="sk-my-claude-proxy",
)
MODEL = "claude-opus-4-6"


def _strip_markdown(text: str) -> str:
    """LLM 출력에서 마크다운 포맷을 제거"""
    import re as _re
    # Remove heading markers (# ## ### etc)
    text = _re.sub(r'^#{1,6}\s*', '', text, flags=_re.MULTILINE)
    # Remove horizontal rules (--- or ***)
    text = _re.sub(r'^[-*]{3,}$', '', text, flags=_re.MULTILINE)
    # Remove bold **text** or __text__
    text = _re.sub(r'\*\*([^*]+)\*\*', r'\\1', text)
    text = _re.sub(r'__([^_]+)__', r'\\1', text)
    # Remove italic *text* or _text_ (careful not to touch emoji)
    text = _re.sub(r'(?<!\w)\*([^*]+)\*(?!\w)', r'\\1', text)
    # Remove backticks
    text = _re.sub(r'`([^`]+)`', r'\\1', text)
    # Clean up 3+ blank lines to 2
    text = _re.sub(r'\n{3,}', '\\n\\n', text)
    return text.strip()


SYSTEM_PROMPT = """너는 "주읽이"라는 서비스의 AI 투자 해석 도우미야.
주식 초보자(주린이)를 위해 종목에 무슨 일이 있었고, 그게 주가에 어떤 영향을 줬는지 쉽게 풀어줘.

## 핵심 원칙
- **뉴스/이슈 중심으로 해석해.** 기술적 분석은 보조적으로만.
- 주린이가 친구한테 설명 듣는 것처럼 쉽고 친근하게.
- 해요체 사용.
- 전문 용어 쓸 때는 바로 풀어서 설명.
- 매수/매도 추천 절대 금지.
- 단정적 표현 금지 ("반드시", "확실히" 등).
- 제공된 숫자만 인용하고, 직접 계산하지 마.
- 전체 리포트 길이는 15~20줄 이내로. 너무 길면 주린이가 안 읽어.

## 성향별 톤
- 안정형(🛡): 보수적. 리스크 강조, 분할/관망 권유
- 중립형(⚖️): 균형. 양면 분석, 조건부 접근
- 공격형(🔥): 적극적. 기회 강조, 단기 모멘텀 언급

## 출력 형식
반드시 아래 4개 섹션으로 답변해. 텔레그램 일반 텍스트로 보내는 거라 마크다운 금지.
별도 제목/헤더 없이 바로 1️⃣부터 시작해.

1️⃣ 지금 어디쯤이에요?
현재가, 등락률, 52주 고점 대비 위치를 한두 줄로 간결하게.

2️⃣ 무슨 일이 있었나요?
뉴스/이슈를 호재·악재별로 분리해서 불릿 포인트로 작성해. 형식:

🟢 호재 헤드라인
→ 왜 중요한지 한 줄 설명

🔴 악재 헤드라인
→ 주가에 어떤 영향인지 한 줄 설명

🟡 주의 헤드라인
→ 체크 포인트 한 줄

호재끼리, 악재끼리 모아서 배치. 각 항목 사이 빈 줄. 벽 텍스트 금지, 각 설명 1~2문장.

3️⃣ 차트는 이렇대요
RSI, 이평선 위치를 초보자가 이해할 수 있게 한두 줄로 짧게. 보조 지표일 뿐이라는 뉘앙스로.

4️⃣ 이렇게 보시면 돼요 ({성향} 기준)
뉴스/이슈와 차트를 종합해서, 성향에 맞는 해석 2~3문장."""


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

    # 뉴스 텍스트 (제목 + 본문 요약 포함)
    news_text = ""
    if news:
        for i, n in enumerate(news, 1):
            title = n.get("title", "")
            desc = n.get("description", "")
            date = n.get("date", "")
            source = n.get("source", "")
            news_text += f"\n  {i}. [{source}] {title} ({date})"
            if desc:
                # 본문 요약 300자로 제한
                desc_trimmed = desc[:300] + "..." if len(desc) > 300 else desc
                news_text += f"\n     → {desc_trimmed}"
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

[최근 뉴스 — 이 섹션을 중심으로 리포트를 작성해줘]{news_text}

[기술 지표 — 보조 참고용]
RSI(14): {ind.get('rsi_14', 'N/A')}
20일 이평선: {ind.get('sma_20', 'N/A')} (현재가 {'위' if ind.get('above_sma20') else '아래'})
50일 이평선: {ind.get('sma_50', 'N/A')} (현재가 {'위' if ind.get('above_sma50') else '아래'})

[유저 성향]
{risk_label}

위 데이터를 바탕으로, 뉴스/이슈를 중심에 놓고 리포트를 작성해줘.
주린이가 "이 종목에 무슨 일이 있었고, 내 투자에 어떤 의미인지" 이해할 수 있도록."""

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
        max_tokens=2000,
        temperature=0.7,
    )

    return _strip_markdown(response.choices[0].message.content)


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
        f"{color} {data['name_ko']} ({data['ticker']}) · {risk_emoji} {risk_label}\n"
        f"{flag} {price_str}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"\n"
        f"{report_text}\n"
        f"\n"
        f"⚠️ 이 리포트는 참고용이에요.\n"
        f"투자 판단은 본인이 직접 해주세요!"
    )

    return msg

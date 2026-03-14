"""AI 리포트 생성 — JSON 구조화 출력 + 코드 포매팅"""

import json
from openai import AsyncOpenAI

# CLIAPIProxy 설정
client = AsyncOpenAI(
    base_url="http://127.0.0.1:8317/v1",
    api_key="sk-my-claude-proxy",
)
MODEL = "claude-opus-4-6"


SYSTEM_PROMPT = """너는 "주읽이"라는 서비스의 AI 투자 해석 도우미야.
주식 초보자(주린이)를 위해 종목에 무슨 일이 있었고, 그게 주가에 어떤 영향을 줬는지 쉽게 풀어줘.

## 핵심 원칙
- 뉴스/이슈 중심으로 해석해. 기술적 분석은 보조적으로만.
- 주린이가 친구한테 설명 듣는 것처럼 쉽고 친근하게.
- 해요체 사용.
- 전문 용어 쓸 때는 바로 풀어서 설명.
- 매수/매도 추천 절대 금지.
- 단정적 표현 금지 ("반드시", "확실히" 등).
- 제공된 숫자만 인용하고, 직접 계산하지 마.

## 성향별 톤
- 안정형: 보수적. 리스크 강조, 분할/관망 권유
- 중립형: 균형. 양면 분석, 조건부 접근
- 공격형: 적극적. 기회 강조, 단기 모멘텀 언급

## 출력
반드시 아래 JSON 스키마로만 응답해. 다른 텍스트 없이 JSON만.

{
  "position": "현재가 위치 설명 1~2문장",
  "news": [
    {
      "type": "bullish | bearish | caution",
      "headline": "짧은 헤드라인 (15자 이내 권장)",
      "detail": "왜 중요한지 / 주가에 어떤 영향인지 1~2문장"
    }
  ],
  "chart": "RSI, 이평선 설명 1~2문장. 보조 지표일 뿐이라는 뉘앙스로.",
  "advice": "뉴스와 차트를 종합한 성향별 해석 2~3문장"
}

규칙:
- news 배열은 2~5개. 각 항목은 반드시 type, headline, detail 포함.
- type은 bullish(호재), bearish(악재), caution(주의) 중 하나.
- 모든 텍스트는 해요체, 마크다운 없이 일반 텍스트로.
- JSON 외 다른 텍스트(설명, 코드블록 마커 등) 절대 포함하지 마."""


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
            title = n.get("title", "")
            desc = n.get("description", "")
            date = n.get("date", "")
            source = n.get("source", "")
            news_text += f"\n  {i}. [{source}] {title} ({date})"
            if desc:
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

위 데이터를 바탕으로 JSON으로 응답해줘."""

    if disc_text:
        prompt += f"\n\n[최근 공시]{disc_text}"

    return prompt


def _parse_report_json(raw: str) -> dict:
    """LLM 응답에서 JSON 추출 및 파싱"""
    text = raw.strip()
    # 코드블록 마커 제거
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    # json 태그 제거
    if text.startswith("json"):
        text = text[4:].strip()

    return json.loads(text)


def _format_news_section(news_items: list) -> str:
    """뉴스 항목 → 포매팅된 텍스트"""
    type_emoji = {
        "bullish": "🟢",
        "bearish": "🔴",
        "caution": "🟡",
    }
    # 호재 → 주의 → 악재 순서로 정렬
    type_order = {"bullish": 0, "caution": 1, "bearish": 2}
    sorted_news = sorted(news_items, key=lambda x: type_order.get(x.get("type", "caution"), 1))

    lines = []
    for item in sorted_news:
        emoji = type_emoji.get(item.get("type", "caution"), "🟡")
        headline = item.get("headline", "")
        detail = item.get("detail", "")
        lines.append(f"{emoji} {headline}")
        if detail:
            lines.append(f"→ {detail}")
        lines.append("")  # 빈 줄

    # 마지막 빈 줄 제거
    if lines and lines[-1] == "":
        lines.pop()

    return "\n".join(lines)


async def generate_report(data: dict, risk_type: str) -> dict:
    """종목 데이터 → AI 리포트 JSON 생성"""
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

    raw = response.choices[0].message.content
    try:
        return _parse_report_json(raw)
    except (json.JSONDecodeError, KeyError) as e:
        # JSON 파싱 실패 시 폴백: 원문 텍스트 그대로
        return {
            "position": "",
            "news": [],
            "chart": "",
            "advice": raw,
            "_fallback": True,
        }


def format_report_message(
    data: dict, risk_type: str, report: dict | str
) -> str:
    """최종 텔레그램 메시지 포맷"""
    from datetime import datetime

    # 하위 호환: report가 문자열이면 기존 방식
    if isinstance(report, str):
        report_text = report
        return _format_legacy(data, risk_type, report_text)

    q = data["quote"]
    risk_emojis = {"안정": "🛡", "중립": "⚖️", "공격": "🔥"}
    risk_labels = {"안정": "안정형", "중립": "중립형", "공격": "공격형"}
    risk_emoji = risk_emojis.get(risk_type, "⚖️")
    risk_label = risk_labels.get(risk_type, "중립형")

    # 장 마감일
    trade_date = data.get("trade_date")
    if trade_date:
        try:
            td = datetime.strptime(trade_date, "%Y-%m-%d")
            date_suffix = td.strftime("%m/%d")
        except ValueError:
            date_suffix = trade_date
    else:
        date_suffix = datetime.now().strftime("%m/%d")

    # 가격
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

    color = "💚" if q["change_pct"] >= 0 else "❤️"
    today = datetime.now().strftime("%Y.%m.%d")

    # 폴백 처리
    if report.get("_fallback"):
        report_text = report.get("advice", "")
        return _format_legacy_with_header(data, risk_type, report_text, today, color, flag, price_str, risk_emoji, risk_label)

    # 섹션 조합
    position = report.get("position", "")
    news_section = _format_news_section(report.get("news", []))
    chart = report.get("chart", "")
    advice = report.get("advice", "")

    msg = (
        f"📊 {today} 주읽이 리포트\n"
        f"\n"
        f"━━━━━━━━━━━━━━━\n"
        f"{color} {data['name_ko']} ({data['ticker']}) · {risk_emoji} {risk_label}\n"
        f"{flag} {price_str}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"\n"
        f"1️⃣ 지금 어디쯤이에요?\n"
        f"{position}\n"
        f"\n"
        f"2️⃣ 무슨 일이 있었나요?\n"
        f"\n"
        f"{news_section}\n"
        f"\n"
        f"3️⃣ 차트는 이렇대요\n"
        f"{chart}\n"
        f"\n"
        f"4️⃣ 이렇게 보시면 돼요 ({risk_emoji} {risk_label} 기준)\n"
        f"{advice}\n"
        f"\n"
        f"⚠️ 이 리포트는 참고용이에요.\n"
        f"투자 판단은 본인이 직접 해주세요!"
    )

    return msg


def _format_legacy(data, risk_type, report_text):
    """기존 문자열 방식 폴백"""
    from datetime import datetime
    q = data["quote"]
    risk_emojis = {"안정": "🛡", "중립": "⚖️", "공격": "🔥"}
    risk_labels = {"안정": "안정형", "중립": "중립형", "공격": "공격형"}
    risk_emoji = risk_emojis.get(risk_type, "⚖️")
    risk_label = risk_labels.get(risk_type, "중립형")
    trade_date = data.get("trade_date")
    if trade_date:
        try:
            td = datetime.strptime(trade_date, "%Y-%m-%d")
            date_suffix = td.strftime("%m/%d")
        except ValueError:
            date_suffix = trade_date
    else:
        date_suffix = datetime.now().strftime("%m/%d")
    if data["market"] == "US":
        price_label = f"{date_suffix} 시간외" if q.get("is_aftermarket") else f"{date_suffix} 종가"
        price_str = f"${q['price']:,.2f} ({q['change_pct']:+.2f}%) · {price_label}"
        flag = "🇺🇸"
    else:
        price_str = f"{q['price']:,}원 ({q['change_pct']:+.2f}%) · {date_suffix} 종가"
        flag = "🇰🇷"
    color = "💚" if q["change_pct"] >= 0 else "❤️"
    today = datetime.now().strftime("%Y.%m.%d")
    return (
        f"📊 {today} 주읽이 리포트\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"{color} {data['name_ko']} ({data['ticker']}) · {risk_emoji} {risk_label}\n"
        f"{flag} {price_str}\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"{report_text}\n\n"
        f"⚠️ 이 리포트는 참고용이에요.\n"
        f"투자 판단은 본인이 직접 해주세요!"
    )


def _format_legacy_with_header(data, risk_type, report_text, today, color, flag, price_str, risk_emoji, risk_label):
    """폴백용 헤더 포함 포매팅"""
    return (
        f"📊 {today} 주읽이 리포트\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"{color} {data['name_ko']} ({data['ticker']}) · {risk_emoji} {risk_label}\n"
        f"{flag} {price_str}\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"{report_text}\n\n"
        f"⚠️ 이 리포트는 참고용이에요.\n"
        f"투자 판단은 본인이 직접 해주세요!"
    )

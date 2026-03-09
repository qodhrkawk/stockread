"""쇼츠 스크립트 생성 — 2단계: TTS 먼저 → 화면 데이터 추출"""
import json
import logging
import re
from datetime import date

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

client = AsyncOpenAI(
    base_url="http://127.0.0.1:8317/v1",
    api_key="sk-my-claude-proxy",
)
MODEL = "claude-sonnet-4-20250514"

# ========== STEP 1: TTS 스크립트 생성 ==========
STEP1_SYSTEM = """너는 주식 초보(주린이)를 위한 YouTube Shorts 나레이션 작가야.

## 말투
- 존댓말 (해요체)
- 친구가 쉽게 설명해주는 느낌
- 짧은 문장 위주 (한 문장 40자 이내)

## 뉴스 활용 (필수!!!)
- 뉴스 헤드라인에 나온 핵심 이벤트(서킷 브레이커, 급등/급락 이유 등)를 반드시 스크립트에 반영
- 여러 종목 뉴스에 공통적으로 등장하는 키워드 → context의 핵심 원인으로 활용
- 뉴스에서 언급된 구체적 사건/수치가 있으면 나레이션에 포함

## 절대 금지
- "지정학적", "밸류에이션", "시총", "극명하게" 등 전문 용어 그대로 사용 금지
  → 반드시 풀어서 설명 (예: "시가총액" → "회사의 전체 가치")
- 매수/매도 추천, 목표가 제시
- "반드시", "확실히" 등 단정 표현

## 필수 규칙
- 수치 반드시 포함 (%, 원, 달러)
- RSI, SMA 등 지표 쓸 때 바로 풀어서 설명
- summary와 detail 내용이 겹치면 안 됨
  - summary = 전체 시장 분위기 (숲, 개별 종목명 X)
  - detail = 개별 종목 분석 (나무)

## 구조 (5파트, 각 파트를 --- 로 구분)

hook (2문장)
- 가장 임팩트 있는 숫자/사건으로 시작
- 질문형 필수: "~했는데, 왜 그런 걸까요?"
---
summary (3문장)
- 시장 전체 분위기만 (개별 종목명 X)
- 어떤 섹터가 올랐고 빠졌는지
---
detail (4~5문장, 15~20초)
- 핵심 종목 2~3개만 TTS로 언급 (종목당 1~2문장)
- 종목당: 가격 + 등락% + 한줄 이유
- 길게 늘어지지 말고 핵심만 짧게!
- 화면에는 카드로 표시되니까 TTS는 간결하게
- 전체 나레이션의 30% 정도 (과하게 길면 안 됨)
---
context (3문장)
- 왜 이런 일이 벌어졌는지 배경/원인
- 원인→결과 인과관계가 명확하게
---
closing (2문장)
- "~해 보여요", "지켜보는 게 좋겠어요" 톤

## 분량: 300~400자 (한국어), 250자 미만 절대 금지
## 전체 나레이션 30~50초 분량 (너무 길면 영상이 잘림!)
## 출력: 5파트를 --- 로 구분. 다른 텍스트 없이 나레이션만."""

# ========== STEP 2: 화면 데이터 추출 ==========
STEP2_SYSTEM = """주어진 TTS 나레이션에서 화면 표시용 데이터를 추출해.

규칙:
- TTS에서 실제로 말하는 내용만 추출 (없는 정보 추가 금지)
- TTS에서 언급한 종목만 cards에 포함 (언급 안 한 종목 추가 금지)
- flow의 각 항목은 TTS context에서 언급한 원인/결과만
- JSON만 출력

출력 형식:
{
  "title": "영상 제목 (후킹용, 15자 이내)",
  "hook": {
    "headline": "핵심 한줄 (TTS 첫 문장 기반)",
    "number": "핵심 숫자 (부호 포함, 예: -9.5%)"
  },
  "summary": {
    "sectors": [{"name": "섹터명", "direction": "up 또는 down"}]
  },
  "detail": {
    "cards": [
      {"name": "종목명", "price": "가격", "change": "등락% (부호 포함)", "indicators": ["지표1"]}
    ]
  },
  "context": {
    "flow": ["원인1", "원인2", "결과"]
  },
  "closing": {
    "message": "마무리 핵심 메시지"
  }
}"""

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


def format_stock_data(item: dict, market: str) -> str:
    """종목 데이터를 프롬프트용 텍스트로 포맷"""
    data = item.get("data_json", {})
    if isinstance(data, str):
        data = json.loads(data)

    quote = data.get("quote", {})
    indicators = data.get("indicators", {})
    ticker = item.get("ticker", "")
    name = quote.get("name", data.get("name_ko", ticker))

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

    year_high = quote.get("year_high", 0)
    pct_from_high = data.get("pct_from_high", 0)
    if year_high:
        lines.append(f"- 52주 고점: {year_high:,} (현재 고점 대비 {pct_from_high:.1f}%)")

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

    per = quote.get("per")
    pbr = quote.get("pbr")
    if per:
        lines.append(f"- PER: {per}")
    if pbr:
        lines.append(f"- PBR: {pbr}")

    news = data.get("news", [])[:3]
    if news:
        lines.append("- 뉴스:")
        for n in news:
            lines.append(f"  · {n.get('title', '')[:80]}")

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
    """2단계 생성: TTS 나레이션 → 화면 데이터 추출"""
    if target_date is None:
        target_date = date.today()

    ctx = MARKET_CONTEXT[market]

    filtered = []
    for item in price_data:
        ticker = item.get("ticker", "")
        is_kr = ticker.isdigit()
        if (market == "KR" and is_kr) or (market == "US" and not is_kr):
            filtered.append(item)

    if not filtered:
        raise RuntimeError(f"{ctx['label']} 가격 데이터가 없습니다.")

    stock_texts = [format_stock_data(item, market) for item in filtered]

    # ===== STEP 1: TTS 나레이션 생성 =====
    step1_system = STEP1_SYSTEM + f"\n\n## 이번 영상\n{ctx['flag']} {ctx['intro']}\n{ctx['label']} 데이터만 다뤄."

    step1_user = f"""오늘 날짜: {target_date.isoformat()}

## {ctx['flag']} {ctx['label']} 주요 종목 데이터

{chr(10).join(stock_texts)}

위 데이터를 기반으로 나레이션을 작성해줘.
기술지표, 뉴스, 52주 고저 등을 활용해서 풍부하게.
5파트를 --- 로 구분해서 출력."""

    logger.info(f"[STEP1] TTS 생성 시작 [{market}]")
    resp1 = await client.chat.completions.create(
        model=MODEL, max_tokens=2048,
        messages=[
            {"role": "system", "content": step1_system},
            {"role": "user", "content": step1_user},
        ],
    )
    tts_raw = resp1.choices[0].message.content.strip()
    logger.info(f"[STEP1] TTS 원본:\n{tts_raw}")

    # --- 로 파트 분리
    parts = re.split(r'\n-{3,}\n', tts_raw)
    if len(parts) < 5:
        # 줄바꿈 패턴 다시 시도
        parts = re.split(r'-{3,}', tts_raw)
    
    labels = ["hook", "summary", "detail", "context", "closing"]
    scene_tts = {}
    for i, label in enumerate(labels):
        scene_tts[label] = parts[i].strip() if i < len(parts) else ""

    tts_script = " ".join(scene_tts[l] for l in labels)
    total_chars = len(tts_script.replace(" ", ""))
    logger.info(f"[STEP1] TTS 완성: {total_chars}자")

    # 300자 미만이면 재생성
    if total_chars < 300:
        logger.warning(f"TTS 분량 부족 ({total_chars}자), 재생성")
        resp1 = await client.chat.completions.create(
            model=MODEL, max_tokens=2048,
            messages=[
                {"role": "system", "content": step1_system},
                {"role": "user", "content": step1_user + "\n\n⚠️ 반드시 350자 이상 작성해줘!"},
            ],
        )
        tts_raw = resp1.choices[0].message.content.strip()
        parts = re.split(r'\n-{3,}\n', tts_raw)
        if len(parts) < 5:
            parts = re.split(r'-{3,}', tts_raw)
        for i, label in enumerate(labels):
            scene_tts[label] = parts[i].strip() if i < len(parts) else ""
        tts_script = " ".join(scene_tts[l] for l in labels)

    # ===== STEP 2: 화면 데이터 추출 =====
    step2_user = f"""아래 TTS 나레이션에서 화면 표시용 데이터를 추출해줘.

## TTS 나레이션 (5파트)

[hook]
{scene_tts['hook']}

[summary]
{scene_tts['summary']}

[detail]
{scene_tts['detail']}

[context]
{scene_tts['context']}

[closing]
{scene_tts['closing']}

JSON만 출력해. 다른 텍스트 없이."""

    logger.info(f"[STEP2] 화면 데이터 추출 시작")
    resp2 = await client.chat.completions.create(
        model=MODEL, max_tokens=1024,
        messages=[
            {"role": "system", "content": STEP2_SYSTEM},
            {"role": "user", "content": step2_user},
        ],
    )

    text2 = resp2.choices[0].message.content.strip()
    if text2.startswith("```"):
        text2 = text2.split("\n", 1)[1]
        text2 = text2.rsplit("```", 1)[0]

    visual = json.loads(text2)
    logger.info(f"[STEP2] 화면 데이터 추출 완료")

    # ===== 최종 JSON 조립 =====
    # 기본 duration 비율
    durations = {"hook": 5, "summary": 10, "detail": 25, "context": 15, "closing": 5}

    scenes = []
    for label in labels:
        scene = {
            "label": label,
            "tts_text": scene_tts[label],
            "duration": durations[label],
        }
        v = visual.get(label, {})
        if label == "hook":
            scene["headline"] = v.get("headline", "")
            scene["number"] = v.get("number", "")
        elif label == "summary":
            scene["sectors"] = v.get("sectors", [])
        elif label == "detail":
            scene["cards"] = v.get("cards", [])
        elif label == "context":
            flow = v.get("flow", [])
            # "→" 기호 제거 (빈 박스 방지)
            scene["flow"] = [f.strip().lstrip("→").strip() for f in flow if f.strip().lstrip("→").strip()]
        elif label == "closing":
            scene["message"] = v.get("message", "")
        scenes.append(scene)

    script = {
        "date": target_date.isoformat(),
        "title": visual.get("title", "오늘의 증시"),
        "tts_script": tts_script,
        "scenes": scenes,
        "market": market,
    }

    total_sec = sum(s["duration"] for s in scenes)
    script["audioDurationSec"] = max(30, min(70, total_sec))

    logger.info(
        f"쇼츠 스크립트 생성 [{market}]: {script['title']} "
        f"({len(tts_script)}자, {script['audioDurationSec']}초)"
    )
    return script

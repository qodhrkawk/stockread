"""60초 상식 스크립트 생성 — 2단계: TTS 먼저 → 화면 데이터 추출"""
import json
import logging
import random
import re
from datetime import date
from pathlib import Path

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

TOPICS_PATH = Path(__file__).parent / "topics.json"

client = AsyncOpenAI(
    base_url="http://127.0.0.1:8317/v1",
    api_key="sk-my-claude-proxy",
)
MODEL = "claude-sonnet-4-20250514"


# ========== STEP 1: TTS 나레이션 생성 ==========
STEP1_SYSTEM = """너는 '60초 상식' YouTube Shorts의 나레이션 작가야.
주어진 상식 주제에 대해 재미있고 쉽게 설명하는 나레이션을 작성해.

## 말투
- 존댓말 (해요체)
- 친구가 쉽게 설명해주는 느낌
- 짧은 문장 위주 (한 문장 35자 이내)

## 절대 금지
- 어려운 전문 용어 그대로 사용 금지 → 반드시 풀어서 설명
- "반드시", "확실히" 등 단정 표현
- 영어 단어 남발 (꼭 필요한 경우만)

## 구조 (4파트, 각 파트를 --- 로 구분)

hook (2문장)
- 질문으로 시작 (호기심 자극)
- 충격적인 팩트 한 줄 추가
---
explain (4~5문장)
- 주제를 쉽게 풀어서 설명
- 구체적인 숫자나 비유 활용
- 단계별로 이해하기 쉽게
---
twist (2~3문장)
- 반전 포인트! 예상 못한 사실
- "그런데 사실은..." 느낌
---
closing (1~2문장)
- 인상적인 마무리
- "~라고 해요", "~인 셈이에요" 톤

## 분량: 250~350자 (한국어), 40~55초 분량
## 출력: 4파트를 --- 로 구분. 다른 텍스트 없이 나레이션만."""


# ========== STEP 2: 화면 데이터 추출 ==========
STEP2_SYSTEM = """주어진 TTS 나레이션에서 화면 표시용 데이터를 추출해.

규칙:
- TTS에서 실제로 말하는 내용을 기반으로 화면 데이터 구성
- 화면 데이터는 TTS 내용을 보조하는 역할
- image_prompt는 반드시 영어로 작성
- image_prompt 스타일: "dark digital illustration of [주제], cinematic lighting, moody atmosphere, 9:16 vertical"
- JSON만 출력

출력 형식:
{
  "title": "영상 제목 (후킹용, 15자 이내)",
  "hook": {
    "question": "질문 (TTS의 첫 질문)",
    "fact": "충격 팩트 (TTS의 두번째 문장 핵심)",
    "image_prompt": "dark digital illustration of ..."
  },
  "explain": {
    "steps": [
      {"icon": "emoji", "text": "설명 포인트 1 (15자 이내)"},
      {"icon": "emoji", "text": "설명 포인트 2"},
      {"icon": "emoji", "text": "설명 포인트 3"}
    ],
    "image_prompt": "dark digital illustration of ..."
  },
  "twist": {
    "highlight": "반전 핵심 (강조 텍스트, 20자 이내)",
    "detail": "부연 설명 (30자 이내)",
    "image_prompt": "dark digital illustration of ..."
  },
  "closing": {
    "message": "키워드 요약 1~2줄",
    "image_prompt": "dark digital illustration of ..."
  }
}

중요:
- explain의 steps는 3~4개, 각 text는 15자 이내로 간결하게
- hook의 question과 fact은 TTS 내용에서 추출
- twist의 highlight는 반전 포인트의 핵심 (크게 표시됨)
- closing의 message는 핵심 키워드 요약
- 모든 image_prompt는 영어, 어두운 톤, 세로(9:16) 구도"""


def load_topics() -> list[dict]:
    """topics.json 로드"""
    with open(TOPICS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_topics(topics: list[dict]):
    """topics.json 저장"""
    with open(TOPICS_PATH, "w", encoding="utf-8") as f:
        json.dump(topics, f, ensure_ascii=False, indent=2)


def pick_random_topic() -> dict:
    """used=false인 주제 중 랜덤 선택, used 마킹"""
    topics = load_topics()
    available = [t for t in topics if not t.get("used", False)]
    if not available:
        raise RuntimeError("사용 가능한 주제가 없습니다. topics.json을 확인하세요.")

    topic = random.choice(available)

    # used 마킹
    for t in topics:
        if t["id"] == topic["id"]:
            t["used"] = True
            t["used_date"] = date.today().isoformat()
            break
    save_topics(topics)

    logger.info(f"주제 선택: [{topic['category']}] {topic['question']}")
    return topic


async def generate_trivia_script(topic: dict | None = None) -> dict:
    """2단계 생성: TTS 나레이션 → 화면 데이터 추출"""
    if topic is None:
        topic = pick_random_topic()

    # ===== STEP 1: TTS 나레이션 생성 =====
    step1_user = f"""주제 정보:
- 카테고리: {topic['category']} {topic['emoji']}
- 질문: {topic['question']}
- 힌트(hook): {topic['hook']}
- 반전 포인트: {topic['twist']}
- 요약: {topic['summary']}
- 키워드: {', '.join(topic['keywords'])}

위 정보를 바탕으로 나레이션을 작성해줘.
4파트를 --- 로 구분해서 출력."""

    logger.info(f"[STEP1] TTS 생성 시작: {topic['question']}")
    resp1 = await client.chat.completions.create(
        model=MODEL, max_tokens=2048,
        messages=[
            {"role": "system", "content": STEP1_SYSTEM},
            {"role": "user", "content": step1_user},
        ],
    )
    tts_raw = resp1.choices[0].message.content.strip()
    logger.info(f"[STEP1] TTS 원본:\n{tts_raw}")

    # --- 로 파트 분리
    parts = re.split(r'\n-{3,}\n', tts_raw)
    if len(parts) < 4:
        parts = re.split(r'-{3,}', tts_raw)

    labels = ["hook", "explain", "twist", "closing"]
    scene_tts = {}
    for i, label in enumerate(labels):
        scene_tts[label] = parts[i].strip() if i < len(parts) else ""

    tts_script = " ".join(scene_tts[l] for l in labels)
    total_chars = len(tts_script.replace(" ", ""))
    logger.info(f"[STEP1] TTS 완성: {total_chars}자")

    # 250자 미만이면 재생성
    if total_chars < 250:
        logger.warning(f"TTS 분량 부족 ({total_chars}자), 재생성")
        resp1 = await client.chat.completions.create(
            model=MODEL, max_tokens=2048,
            messages=[
                {"role": "system", "content": STEP1_SYSTEM},
                {"role": "user", "content": step1_user + "\n\n⚠️ 반드시 300자 이상 작성해줘!"},
            ],
        )
        tts_raw = resp1.choices[0].message.content.strip()
        parts = re.split(r'\n-{3,}\n', tts_raw)
        if len(parts) < 4:
            parts = re.split(r'-{3,}', tts_raw)
        for i, label in enumerate(labels):
            scene_tts[label] = parts[i].strip() if i < len(parts) else ""
        tts_script = " ".join(scene_tts[l] for l in labels)

    # ===== STEP 2: 화면 데이터 추출 =====
    step2_user = f"""아래 TTS 나레이션에서 화면 표시용 데이터를 추출해줘.

## 주제 정보
- 카테고리: {topic['category']} {topic['emoji']}
- 질문: {topic['question']}

## TTS 나레이션 (4파트)

[hook]
{scene_tts['hook']}

[explain]
{scene_tts['explain']}

[twist]
{scene_tts['twist']}

[closing]
{scene_tts['closing']}

JSON만 출력해. 다른 텍스트 없이."""

    logger.info("[STEP2] 화면 데이터 추출 시작")
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
    logger.info("[STEP2] 화면 데이터 추출 완료")

    # ===== 최종 JSON 조립 =====
    durations = {"hook": 8, "explain": 18, "twist": 12, "closing": 7}

    scenes = []
    for label in labels:
        scene = {
            "label": label,
            "tts_text": scene_tts[label],
            "duration": durations[label],
        }
        v = visual.get(label, {})
        if label == "hook":
            scene["question"] = v.get("question", topic["question"])
            scene["fact"] = v.get("fact", topic["hook"])
            scene["image_prompt"] = v.get("image_prompt", "")
        elif label == "explain":
            scene["steps"] = v.get("steps", [])
            scene["image_prompt"] = v.get("image_prompt", "")
        elif label == "twist":
            scene["highlight"] = v.get("highlight", topic["twist"])
            scene["detail"] = v.get("detail", "")
            scene["image_prompt"] = v.get("image_prompt", "")
        elif label == "closing":
            scene["message"] = v.get("message", topic["summary"])
            scene["image_prompt"] = v.get("image_prompt", "")
        scenes.append(scene)

    script = {
        "date": date.today().isoformat(),
        "title": visual.get("title", topic["question"][:15]),
        "tts_script": tts_script,
        "scenes": scenes,
        "topic_id": topic["id"],
        "category": topic["category"],
        "emoji": topic["emoji"],
    }

    total_sec = sum(s["duration"] for s in scenes)
    script["audioDurationSec"] = max(30, min(60, total_sec))

    logger.info(
        f"상식 스크립트 생성: {script['title']} "
        f"({len(tts_script)}자, {script['audioDurationSec']}초)"
    )
    return script

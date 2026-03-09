"""쇼츠 전체 파이프라인 — 섹션별 TTS 싱크"""
import json
import logging
import os
import math
from datetime import date
from pathlib import Path

import aiosqlite

from .script_generator import generate_shorts_script
from .tts import generate_tts_per_scene
from .renderer import render_short
from .notifier import send_shorts_to_owner

logger = logging.getLogger(__name__)

DB_PATH = Path.home() / "stockread" / "backend" / "data" / "stockread.db"


async def get_price_data_for_shorts(target_date: date) -> list[dict]:
    """DB에서 쇼츠용 가격 데이터 가져오기"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        rows = await db.execute_fetchall(
            "SELECT ticker, data_json FROM price_cache ORDER BY price_date DESC"
        )

    result = []
    seen = set()
    for row in rows:
        ticker = row["ticker"]
        if ticker in seen:
            continue
        seen.add(ticker)
        data_json = row["data_json"]
        if isinstance(data_json, str):
            data_json = json.loads(data_json)
        result.append({"ticker": ticker, "data_json": data_json})

    return result


async def save_shorts_to_db(script: dict, mp4_path: str, target_date: date, market: str):
    """shorts_content 테이블에 저장"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT OR REPLACE INTO shorts_content
               (content_date, script_json, mp4_path, status, market)
               VALUES (?, ?, ?, 'generated', ?)""",
            (
                target_date.isoformat(),
                json.dumps(script, ensure_ascii=False),
                str(mp4_path),
                market,
            ),
        )
        await db.commit()


async def run_shorts_pipeline(target_date: date | None = None, market: str = "US") -> dict:
    """쇼츠 파이프라인 실행 (시장별)"""
    if target_date is None:
        target_date = date.today()

    market_label = "🇺🇸 미국" if market == "US" else "🇰🇷 한국"
    logger.info(f"=== 쇼츠 파이프라인 시작: {target_date} [{market_label}] ===")

    # 1. 가격 데이터
    price_data = await get_price_data_for_shorts(target_date)
    if not price_data:
        raise RuntimeError("가격 데이터가 없습니다.")

    # 2. 스크립트 생성 (300자 미만이면 1회 재생성)
    script = await generate_shorts_script(price_data, target_date, market=market)
    if len(script.get('tts_script', '')) < 300:
        logger.warning(f"스크립트 너무 짧음 ({len(script['tts_script'])}자), 재생성...")
        script = await generate_shorts_script(price_data, target_date, market=market)
    logger.info(f"스크립트 생성: {script['title']} ({len(script['tts_script'])}자)")

    # 3. 섹션별 TTS
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    audio_path = None
    has_audio = False

    if openai_key:
        audio_dir = Path.home() / "stockread" / "backend" / "data" / "shorts" / f"{target_date.isoformat()}_{market.lower()}"
        audio_dir.mkdir(parents=True, exist_ok=True)

        try:
            merged_path, scene_durations = await generate_tts_per_scene(
                scenes=script["scenes"],
                output_dir=audio_dir,
                api_key=openai_key,
                voice="onyx",
                speed=1.0,
            )
            has_audio = True

            # 각 scene의 duration을 실제 TTS 길이로 설정
            for i, scene in enumerate(script["scenes"]):
                if i < len(scene_durations):
                    scene["duration"] = math.ceil(scene_durations[i])

            total_sec = sum(s["duration"] for s in script["scenes"])
            
            # 70초 초과 시 비례 축소 (영상이 잘리지 않도록)
            MAX_SEC = 65
            if total_sec > MAX_SEC:
                ratio = MAX_SEC / total_sec
                logger.warning(f"TTS 총 {total_sec}초 > {MAX_SEC}초, 비례 축소 (ratio={ratio:.2f})")
                for s in script["scenes"]:
                    s["duration"] = max(3, math.ceil(s["duration"] * ratio))
                total_sec = sum(s["duration"] for s in script["scenes"])
            
            script["audioDurationSec"] = total_sec
            audio_path = merged_path

            logger.info(f"섹션별 TTS 완료: 총 {total_sec}초")
            for i, s in enumerate(script["scenes"]):
                logger.info(f"  {s['label']}: {s['duration']}초")

        except Exception as e:
            logger.warning(f"TTS 생성 실패 (오디오 없이 진행): {e}")
            import traceback
            traceback.print_exc()
            audio_path = None
    else:
        logger.info("OPENAI_API_KEY 없음 — TTS 스킵")
        script["audioDurationSec"] = sum(s["duration"] for s in script["scenes"])

    # 4. Remotion 렌더링
    mp4_path = await render_short(
        script=script,
        audio_path=audio_path,
        output_filename=f"short_{target_date.isoformat()}_{market.lower()}.mp4",
    )

    # 5. DB 저장
    await save_shorts_to_db(script, str(mp4_path), target_date, market)

    logger.info(f"=== 쇼츠 파이프라인 완료 [{market_label}]: {mp4_path} ===")

    return {
        "script": script,
        "mp4_path": str(mp4_path),
        "has_audio": has_audio,
    }


async def send_shorts_notification(market: str = "US", target_date: date | None = None):
    """DB에서 쇼츠 가져와서 오너에게 OpenClaw 봇으로 전송"""
    if target_date is None:
        target_date = date.today()

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        row = await db.execute_fetchall(
            "SELECT * FROM shorts_content WHERE content_date = ? AND market = ? ORDER BY id DESC LIMIT 1",
            (target_date.isoformat(), market),
        )

    if not row:
        logger.warning(f"쇼츠 데이터 없음: {target_date} [{market}]")
        return

    row = row[0]
    script = json.loads(row["script_json"]) if isinstance(row["script_json"], str) else row["script_json"]
    mp4_path = row["mp4_path"]

    if not Path(mp4_path).exists():
        logger.error(f"MP4 파일 없음: {mp4_path}")
        return

    await send_shorts_to_owner(mp4_path, script)

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE shorts_content SET status = 'sent' WHERE content_date = ? AND market = ?",
            (target_date.isoformat(), market),
        )
        await db.commit()

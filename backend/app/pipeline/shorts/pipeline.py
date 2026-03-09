"""쇼츠 전체 파이프라인 오케스트레이터"""
import json
import logging
import os
from datetime import date
from pathlib import Path

import aiosqlite

from .script_generator import generate_shorts_script
from .tts import generate_tts
from .renderer import render_short
from .notifier import send_shorts_to_owner

logger = logging.getLogger(__name__)

DB_PATH = Path.home() / "stockread" / "backend" / "data" / "stockread.db"


async def get_price_data_for_shorts(target_date: date) -> list[dict]:
    """DB에서 쇼츠용 가격 데이터 가져오기 (랜딩 5종목 + 주요 종목)"""
    # 주요 종목 (시장 전체 흐름 파악용)
    key_tickers = [
        "NVDA", "TSLA", "AAPL", "MSFT", "GOOGL",
        "005930", "000660", "373220",  # 삼성전자, SK하이닉스, LG에너지
    ]
    placeholders = ",".join(["?" for _ in key_tickers])

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        rows = await db.execute_fetchall(
            f"""SELECT ticker, data_json FROM price_cache
                WHERE ticker IN ({placeholders})
                ORDER BY price_date DESC""",
            key_tickers,
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


async def save_shorts_to_db(script: dict, mp4_path: str, target_date: date):
    """shorts_content 테이블에 저장"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT OR REPLACE INTO shorts_content
               (content_date, script_json, mp4_path, status)
               VALUES (?, ?, ?, 'generated')""",
            (
                target_date.isoformat(),
                json.dumps(script, ensure_ascii=False),
                str(mp4_path),
            ),
        )
        await db.commit()
    logger.info(f"쇼츠 DB 저장 완료: {target_date}")


async def run_shorts_pipeline(target_date: date | None = None) -> dict:
    """쇼츠 전체 파이프라인 실행

    1. 가격 데이터 조회
    2. Claude로 스크립트 생성
    3. OpenAI TTS로 음성 생성 (API 키 있을 때만)
    4. Remotion으로 MP4 렌더링
    5. DB 저장

    Returns:
        {"script": dict, "mp4_path": str, "has_audio": bool}
    """
    if target_date is None:
        target_date = date.today()

    logger.info(f"=== 쇼츠 파이프라인 시작: {target_date} ===")

    # 1. 가격 데이터
    price_data = await get_price_data_for_shorts(target_date)
    if not price_data:
        raise RuntimeError("가격 데이터가 없습니다. 먼저 데이터 수집을 실행하세요.")
    logger.info(f"가격 데이터 {len(price_data)}건 조회")

    # 2. 스크립트 생성
    script = await generate_shorts_script(price_data, target_date)
    logger.info(f"스크립트 생성: {script['title']}")

    # 3. TTS (API 키가 있을 때만)
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    audio_path = None
    has_audio = False

    if openai_key:
        audio_dir = Path.home() / "stockread" / "backend" / "data" / "shorts"
        audio_dir.mkdir(parents=True, exist_ok=True)
        audio_path = audio_dir / f"tts_{target_date.isoformat()}.mp3"
        
        try:
            await generate_tts(
                text=script["tts_script"],
                output_path=audio_path,
                api_key=openai_key,
                voice="onyx",
                speed=1.0,
            )
            has_audio = True
            
            # mp3 길이 추정 (대략 1분당 1MB, 더 정확하려면 mutagen 사용)
            # 우선 글자수 기반 추정: 한국어 약 4자/초
            char_count = len(script["tts_script"])
            estimated_sec = max(30, min(60, int(char_count / 4)))
            script["audioDurationSec"] = estimated_sec
            logger.info(f"TTS 생성 완료, 추정 길이: {estimated_sec}초")
        except Exception as e:
            logger.warning(f"TTS 생성 실패 (오디오 없이 진행): {e}")
            audio_path = None
    else:
        logger.info("OPENAI_API_KEY 없음 — TTS 스킵, 영상만 생성")

    # 4. Remotion 렌더링
    mp4_path = await render_short(
        script=script,
        audio_path=audio_path,
        output_filename=f"short_{target_date.isoformat()}.mp4",
    )

    # 5. DB 저장
    await save_shorts_to_db(script, str(mp4_path), target_date)

    logger.info(f"=== 쇼츠 파이프라인 완료: {mp4_path} ===")

    return {
        "script": script,
        "mp4_path": str(mp4_path),
        "has_audio": has_audio,
    }


async def send_shorts_notification(target_date: date | None = None):
    """DB에서 쇼츠 가져와서 오너에게 전송"""
    if target_date is None:
        target_date = date.today()

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        row = await db.execute_fetchall(
            "SELECT * FROM shorts_content WHERE content_date = ? ORDER BY id DESC LIMIT 1",
            (target_date.isoformat(),),
        )

    if not row:
        logger.warning(f"쇼츠 데이터 없음: {target_date}")
        return

    row = row[0]
    script = json.loads(row["script_json"]) if isinstance(row["script_json"], str) else row["script_json"]
    mp4_path = row["mp4_path"]

    if not Path(mp4_path).exists():
        logger.error(f"MP4 파일 없음: {mp4_path}")
        return

    await send_shorts_to_owner(mp4_path, script)

    # 상태 업데이트
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE shorts_content SET status = 'sent' WHERE content_date = ?",
            (target_date.isoformat(),),
        )
        await db.commit()

    logger.info(f"쇼츠 전송 완료: {target_date}")

"""60초 상식 전체 파이프라인"""
import asyncio
import json
import logging
import math
import os
import shutil
from datetime import date
from pathlib import Path

from .script_generator import generate_trivia_script
from .tts import generate_trivia_tts
from .image_generator import generate_trivia_images

logger = logging.getLogger(__name__)

SHORTS_DIR = Path.home() / "stockread" / "shorts"
OUTPUT_DIR = Path.home() / "stockread" / "backend" / "data" / "trivia"


async def render_trivia(
    script: dict,
    audio_path: str | Path | None = None,
    output_filename: str | None = None,
) -> Path:
    """Remotion으로 60초 상식 MP4 렌더링"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if output_filename is None:
        output_filename = f"trivia_{script['date']}.mp4"
    output_path = OUTPUT_DIR / output_filename

    # TTS 오디오 → Remotion public 폴더에 복사
    if audio_path:
        audio_path = Path(audio_path)
        public_dir = SHORTS_DIR / "public" / "trivia"
        public_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(audio_path, public_dir / "tts.mp3")
        logger.info(f"TTS 오디오 복사: {audio_path} → {public_dir / 'tts.mp3'}")

    # duration 클램핑
    duration_sec = script.get("audioDurationSec", 45)
    duration_sec = max(30, min(60, duration_sec))
    script["audioDurationSec"] = duration_sec

    props = json.dumps(script, ensure_ascii=False)

    cmd = [
        "npx", "remotion", "render",
        "TriviaVideo",
        str(output_path),
        f"--props={props}",
        "--concurrency=4",
    ]

    logger.info(f"Remotion 렌더링 시작: {duration_sec}초, {output_path}")

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=str(SHORTS_DIR),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        error_msg = stderr.decode() if stderr else stdout.decode()
        logger.error(f"Remotion 렌더링 실패: {error_msg}")
        raise RuntimeError(f"Remotion render failed: {error_msg}")

    size_mb = output_path.stat().st_size / (1024 * 1024)
    logger.info(f"렌더링 완료: {output_path} ({size_mb:.1f} MB)")
    return output_path


async def run_trivia_pipeline(topic: dict | None = None) -> dict:
    """60초 상식 파이프라인 실행"""
    today = date.today()
    logger.info(f"=== 60초 상식 파이프라인 시작: {today} ===")

    # 1. 스크립트 생성 (주제 선정 포함)
    script = await generate_trivia_script(topic)
    logger.info(f"스크립트 생성: {script['title']} ({len(script['tts_script'])}자)")

    openai_key = os.environ.get("OPENAI_API_KEY", "")
    audio_path = None
    has_audio = False

    work_dir = OUTPUT_DIR / f"{today.isoformat()}_{script['topic_id']}"
    work_dir.mkdir(parents=True, exist_ok=True)

    # 2. 이미지 4장 생성
    if openai_key:
        try:
            image_paths = await generate_trivia_images(
                scenes=script["scenes"],
                output_dir=work_dir / "images",
            )

            # Remotion public/trivia/ 에 이미지 복사
            public_trivia = SHORTS_DIR / "public" / "trivia"
            public_trivia.mkdir(parents=True, exist_ok=True)
            for label, img_path in image_paths.items():
                if img_path and Path(img_path).exists():
                    shutil.copy2(img_path, public_trivia / f"{label}.png")
                    logger.info(f"이미지 복사: {label}.png → {public_trivia}")

        except Exception as e:
            logger.warning(f"이미지 생성 실패 (기본 배경으로 진행): {e}")
            import traceback
            traceback.print_exc()

    # 3. TTS 생성
    if openai_key:
        try:
            merged_path, scene_durations = await generate_trivia_tts(
                scenes=script["scenes"],
                output_dir=work_dir / "tts",
                api_key=openai_key,
                voice="onyx",
                speed=1.15,
            )
            has_audio = True

            # 실제 TTS 길이로 duration 업데이트
            for i, scene in enumerate(script["scenes"]):
                if i < len(scene_durations):
                    scene["duration"] = math.ceil(scene_durations[i])

            total_sec = sum(s["duration"] for s in script["scenes"])
            script["audioDurationSec"] = total_sec
            audio_path = merged_path

            logger.info(f"섹션별 TTS 완료: 총 {total_sec}초")
            for s in script["scenes"]:
                logger.info(f"  {s['label']}: {s['duration']}초")

        except Exception as e:
            logger.warning(f"TTS 생성 실패 (오디오 없이 진행): {e}")
            import traceback
            traceback.print_exc()
    else:
        logger.info("OPENAI_API_KEY 없음 — TTS + 이미지 스킵")
        script["audioDurationSec"] = sum(s["duration"] for s in script["scenes"])

    # 스크립트 JSON 저장 (파일 기반)
    script_path = work_dir / "script.json"
    with open(script_path, "w", encoding="utf-8") as f:
        json.dump(script, f, ensure_ascii=False, indent=2)
    logger.info(f"스크립트 저장: {script_path}")

    # 4. Remotion 렌더링
    mp4_path = await render_trivia(
        script=script,
        audio_path=audio_path,
        output_filename=f"trivia_{today.isoformat()}_{script['topic_id']}.mp4",
    )

    logger.info(f"=== 60초 상식 파이프라인 완료: {mp4_path} ===")

    return {
        "script": script,
        "mp4_path": str(mp4_path),
        "has_audio": has_audio,
    }

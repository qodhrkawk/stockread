"""Remotion CLI를 호출하여 MP4 렌더링"""
import asyncio
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

SHORTS_DIR = Path.home() / "stockread" / "shorts"
OUTPUT_DIR = Path.home() / "stockread" / "backend" / "data" / "shorts"


async def render_short(
    script: dict,
    audio_path: str | Path | None = None,
    output_filename: str | None = None,
) -> Path:
    """Remotion으로 쇼츠 MP4 렌더링"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if output_filename is None:
        output_filename = f"short_{script['date']}.mp4"
    output_path = OUTPUT_DIR / output_filename

    # TTS 오디오가 있으면 Remotion public 폴더에 복사
    if audio_path:
        audio_path = Path(audio_path)
        public_dir = SHORTS_DIR / "public"
        public_dir.mkdir(parents=True, exist_ok=True)
        import shutil
        shutil.copy2(audio_path, public_dir / "tts.mp3")
        logger.info(f"TTS 오디오 복사: {audio_path} → {public_dir / 'tts.mp3'}")

    # audioDurationSec가 props에 있으면 calculateMetadata가 duration 결정
    duration_sec = script.get("audioDurationSec", 30)
    duration_sec = max(30, min(60, duration_sec))
    script["audioDurationSec"] = duration_sec

    # props JSON
    props = json.dumps(script, ensure_ascii=False)

    cmd = [
        "npx", "remotion", "render",
        "ShortVideo",
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

"""OpenAI TTS — 섹션별 생성 + 합치기"""
import logging
import subprocess
from pathlib import Path

import httpx
from mutagen.mp3 import MP3

logger = logging.getLogger(__name__)

OPENAI_TTS_URL = "https://api.openai.com/v1/audio/speech"


async def generate_tts_single(
    text: str,
    output_path: str | Path,
    api_key: str,
    voice: str = "onyx",
    model: str = "tts-1",
    speed: float = 1.0,
) -> tuple[Path, float]:
    """단일 TTS mp3 생성 → (경로, 길이 초)"""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            OPENAI_TTS_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "input": text,
                "voice": voice,
                "response_format": "mp3",
                "speed": speed,
            },
        )
        resp.raise_for_status()
        output_path.write_bytes(resp.content)

    audio = MP3(str(output_path))
    duration = audio.info.length
    return output_path, duration


async def generate_tts_per_scene(
    scenes: list[dict],
    output_dir: str | Path,
    api_key: str,
    voice: str = "onyx",
    model: str = "tts-1",
    speed: float = 1.0,
) -> tuple[Path, list[float]]:
    """섹션별 TTS 생성 → 합친 mp3 + 각 섹션 길이 리스트

    Returns:
        (합친 mp3 경로, [hook 길이, summary 길이, ...])
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    scene_paths: list[Path] = []
    scene_durations: list[float] = []

    for i, scene in enumerate(scenes):
        tts_text = scene.get("tts_text", scene.get("text", ""))
        if not tts_text.strip():
            # 텍스트 없으면 빈 구간 (0.5초 무음 대체)
            scene_durations.append(0.5)
            continue

        path = output_dir / f"scene_{i}_{scene['label']}.mp3"
        path, duration = await generate_tts_single(
            text=tts_text,
            output_path=path,
            api_key=api_key,
            voice=voice,
            model=model,
            speed=speed,
        )
        scene_paths.append(path)
        scene_durations.append(duration)
        logger.info(f"  TTS [{scene['label']}]: {duration:.1f}초 ({len(tts_text)}자)")

    # ffmpeg로 mp3 합치기
    merged_path = output_dir / "tts.mp3"
    concat_file = output_dir / "concat.txt"

    with open(concat_file, "w") as f:
        for p in scene_paths:
            f.write(f"file '{p}'\n")

    subprocess.run(
        [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",
            str(merged_path),
        ],
        capture_output=True,
        check=True,
    )

    # 정리
    concat_file.unlink(missing_ok=True)

    total = sum(scene_durations)
    logger.info(f"TTS 합치기 완료: {merged_path} (총 {total:.1f}초, {len(scenes)}개 섹션)")

    return merged_path, scene_durations


# 하위 호환용
async def generate_tts(
    text: str,
    output_path: str | Path,
    api_key: str,
    voice: str = "onyx",
    model: str = "tts-1",
    speed: float = 1.0,
) -> tuple[Path, float]:
    """단일 TTS (하위 호환)"""
    return await generate_tts_single(text, output_path, api_key, voice, model, speed)

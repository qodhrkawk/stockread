"""OpenAI TTS로 음성 mp3 생성 + 길이 측정"""
import logging
from pathlib import Path

import httpx
from mutagen.mp3 import MP3

logger = logging.getLogger(__name__)

OPENAI_TTS_URL = "https://api.openai.com/v1/audio/speech"


async def generate_tts(
    text: str,
    output_path: str | Path,
    api_key: str,
    voice: str = "onyx",
    model: str = "tts-1",
    speed: float = 1.0,
) -> tuple[Path, float]:
    """OpenAI TTS API로 음성 mp3 생성

    Returns:
        (mp3 파일 경로, 오디오 길이 초)
    """
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

    # mp3 실제 길이 측정
    audio = MP3(str(output_path))
    duration_sec = audio.info.length

    size_kb = output_path.stat().st_size / 1024
    logger.info(f"TTS 생성 완료: {output_path} ({size_kb:.1f} KB, {duration_sec:.1f}초)")
    return output_path, duration_sec

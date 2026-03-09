"""OpenAI TTS로 음성 mp3 생성"""
import logging
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)

OPENAI_TTS_URL = "https://api.openai.com/v1/audio/speech"


async def generate_tts(
    text: str,
    output_path: str | Path,
    api_key: str,
    voice: str = "onyx",
    model: str = "tts-1",
    speed: float = 1.0,
) -> Path:
    """OpenAI TTS API로 음성 mp3 생성

    Args:
        text: TTS 스크립트
        output_path: 출력 mp3 경로
        api_key: OpenAI API 키
        voice: 음성 (onyx=남성 차분)
        model: tts-1 또는 tts-1-hd
        speed: 속도 (0.25~4.0)

    Returns:
        mp3 파일 경로
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

    size_kb = output_path.stat().st_size / 1024
    logger.info(f"TTS 생성 완료: {output_path} ({size_kb:.1f} KB)")
    return output_path

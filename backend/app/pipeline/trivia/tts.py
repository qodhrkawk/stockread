"""60초 상식 — TTS 생성 (기존 shorts/tts.py 재사용 패턴)"""
import logging
import re
import subprocess
from pathlib import Path

import httpx
from mutagen.mp3 import MP3

logger = logging.getLogger(__name__)

OPENAI_TTS_URL = "https://api.openai.com/v1/audio/speech"


def normalize_korean_numbers(text: str) -> str:
    """TTS용 숫자 전처리: comma 포함 숫자를 한국어 읽기로 변환"""
    def convert_won(match):
        raw = match.group(1).replace(",", "")
        suffix = match.group(2)
        num = int(raw)

        if num >= 100_000_000:
            eok = num // 100_000_000
            remainder = num % 100_000_000
            if remainder >= 10_000:
                man = remainder // 10_000
                rest = remainder % 10_000
                if rest > 0:
                    return f"{eok}억 {man}만 {rest}{suffix}"
                return f"{eok}억 {man}만{suffix}"
            elif remainder > 0:
                return f"{eok}억 {remainder}{suffix}"
            return f"{eok}억{suffix}"
        elif num >= 10_000:
            man = num // 10_000
            remainder = num % 10_000
            if remainder > 0:
                return f"{man}만 {remainder}{suffix}"
            return f"{man}만{suffix}"
        else:
            return f"{num}{suffix}"

    text = re.sub(r'(\d{1,3}(?:,\d{3})+)(원|달러|주|개|명|마리|km|kg|톤|리터)', convert_won, text)
    text = re.sub(r'(\d{1,3}),(\d{3})', lambda m: m.group(1) + m.group(2), text)
    return text


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

    processed_text = normalize_korean_numbers(text)
    if processed_text != text:
        logger.info(f"  TTS 숫자 변환: {text[:60]}... → {processed_text[:60]}...")

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            OPENAI_TTS_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "input": processed_text,
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


async def generate_trivia_tts(
    scenes: list[dict],
    output_dir: str | Path,
    api_key: str,
    voice: str = "onyx",
    model: str = "tts-1",
    speed: float = 1.15,
) -> tuple[Path, list[float]]:
    """4파트 TTS 생성 → 합친 mp3 + 각 섹션 길이 리스트"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    scene_paths: list[Path] = []
    scene_durations: list[float] = []

    for i, scene in enumerate(scenes):
        tts_text = scene.get("tts_text", "")
        if not tts_text.strip():
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
    concat_file.unlink(missing_ok=True)

    total = sum(scene_durations)
    logger.info(f"TTS 합치기 완료: {merged_path} (총 {total:.1f}초, {len(scenes)}개 섹션)")

    return merged_path, scene_durations

"""60초 상식 — DALL-E 3 씬별 이미지 생성"""
import logging
import os
from pathlib import Path

import httpx
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

SCENE_LABELS = ["hook", "explain", "twist", "closing"]


async def generate_trivia_images(
    scenes: list[dict],
    output_dir: str | Path,
) -> dict[str, str]:
    """씬별 DALL-E 3 이미지 4장 생성 → {label: path} 반환"""
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY가 설정되지 않았습니다.")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    client = AsyncOpenAI(api_key=api_key)
    result: dict[str, str] = {}

    for scene in scenes:
        label = scene["label"]
        if label not in SCENE_LABELS:
            continue

        prompt = scene.get("image_prompt", "")
        if not prompt:
            prompt = f"dark digital illustration, cinematic lighting, moody atmosphere, 9:16 vertical composition"

        # 안전성 + 스타일 보강
        full_prompt = f"{prompt}. No text, no words, no letters, no watermarks. Dark moody digital art style."

        logger.info(f"[이미지] {label} 생성 중: {prompt[:80]}...")

        try:
            response = await client.images.generate(
                model="dall-e-3",
                prompt=full_prompt,
                size="1024x1792",
                quality="standard",
                n=1,
            )

            image_url = response.data[0].url
            output_path = output_dir / f"{label}.png"

            # 이미지 다운로드
            async with httpx.AsyncClient(timeout=60) as http:
                img_resp = await http.get(image_url)
                img_resp.raise_for_status()
                output_path.write_bytes(img_resp.content)

            result[label] = str(output_path)
            logger.info(f"[이미지] {label} 저장: {output_path}")

        except Exception as e:
            logger.error(f"[이미지] {label} 생성 실패: {e}")
            result[label] = ""

    return result

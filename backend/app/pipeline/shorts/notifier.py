"""쇼츠 MP4를 OpenClaw 봇으로 윤재에게 전송"""
import logging
import os
from pathlib import Path

from telegram import Bot

logger = logging.getLogger(__name__)

OWNER_CHAT_ID = "7923407207"


def _get_openclaw_bot() -> Bot:
    """OpenClaw 봇 인스턴스 (서비스 봇이 아닌 알림 전용)"""
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN 환경변수 없음 (OpenClaw 봇)")
    return Bot(token=token)


async def send_shorts_to_owner(
    mp4_path: str | Path,
    script: dict,
    bot: Bot | None = None,
) -> None:
    """렌더링된 MP4를 윤재에게 OpenClaw 봇으로 전송

    Args:
        mp4_path: MP4 파일 경로
        script: 스크립트 JSON (캡션용)
        bot: Bot 인스턴스 (없으면 OpenClaw 봇 사용)
    """
    if bot is None:
        bot = _get_openclaw_bot()

    mp4_path = Path(mp4_path)

    caption = (
        f"🎬 쇼츠 검토용 ({script['date']})\n\n"
        f"📌 {script['title']}\n"
        f"📝 {script['market_summary']}\n\n"
        f"확인 후 유튜브에 업로드해주세요!"
    )

    with open(mp4_path, "rb") as f:
        await bot.send_video(
            chat_id=OWNER_CHAT_ID,
            video=f,
            caption=caption,
            supports_streaming=True,
        )

    logger.info(f"쇼츠 MP4 전송 완료 (OpenClaw 봇): {mp4_path.name} → 오너")

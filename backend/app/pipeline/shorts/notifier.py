"""쇼츠 MP4를 텔레그램으로 전송"""
import logging
from pathlib import Path

from telegram import Bot

logger = logging.getLogger(__name__)

OWNER_CHAT_ID = "7923407207"


async def send_shorts_to_owner(
    bot: Bot,
    mp4_path: str | Path,
    script: dict,
) -> None:
    """렌더링된 MP4를 윤재에게 텔레그램으로 전송

    Args:
        bot: Telegram Bot 인스턴스
        mp4_path: MP4 파일 경로
        script: 스크립트 JSON (캡션용)
    """
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

    logger.info(f"쇼츠 MP4 전송 완료: {mp4_path.name} → 오너")

"""텔레그램 봇 실행"""

import os
import asyncio
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
)

from app.db.database import init_db
from .handlers import (
    start_command,
    my_command,
    edit_command,
    help_command,
    callback_handler,
)


async def run_bot_async():
    """봇 비동기 실행"""
    await init_db()
    print("✅ DB initialized")

    token = os.environ.get("StockRead_BOT_TOKEN")
    if not token:
        raise ValueError("StockRead_BOT_TOKEN 환경변수가 필요합니다")

    app = ApplicationBuilder().token(token).build()

    # 핸들러 등록
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("my", my_command))
    app.add_handler(CommandHandler("edit", edit_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(callback_handler))

    # 수동 초기화 + 폴링
    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)

    print("🤖 주읽이 봇 시작!")

    # 종료 시그널 대기
    stop_event = asyncio.Event()

    import signal
    def _signal_handler(sig, frame):
        stop_event.set()

    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    await stop_event.wait()

    # 정리
    await app.updater.stop()
    await app.stop()
    await app.shutdown()
    print("👋 봇 종료")


def run_bot():
    asyncio.run(run_bot_async())

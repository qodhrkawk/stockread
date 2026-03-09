"""텔레그램 봇 + 스케줄러 실행"""

import os
import asyncio
import signal
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
)

from app.db.database import init_db
from app.scheduler import create_scheduler, print_schedule
from .handlers import (
    start_command,
    my_command,
    edit_command,
    help_command,
    callback_handler,
)


async def run_bot_async():
    """봇 + 스케줄러 비동기 실행"""
    await init_db()
    print("✅ DB initialized")

    token = os.environ.get("StockRead_BOT_TOKEN")
    if not token:
        raise ValueError("StockRead_BOT_TOKEN 환경변수가 필요합니다")

    # 봇 빌드
    app = ApplicationBuilder().token(token).build()

    # 핸들러 등록
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("my", my_command))
    app.add_handler(CommandHandler("edit", edit_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(callback_handler))

    # 스케줄러 시작
    scheduler = create_scheduler()
    scheduler.start()
    print_schedule(scheduler)

    # 봇 시작
    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)

    print("🤖 주읽이 봇 + 스케줄러 실행 중!")
    print("   봇: 텔레그램 폴링")
    print("   스케줄: 06:00 수집 / 07:00 발송 (KST)")
    print()

    # 종료 시그널 대기
    stop_event = asyncio.Event()

    def _signal_handler(sig, frame):
        stop_event.set()

    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    await stop_event.wait()

    # 정리
    scheduler.shutdown()
    await app.updater.stop()
    await app.stop()
    await app.shutdown()
    print("👋 봇 + 스케줄러 종료")


def run_bot():
    asyncio.run(run_bot_async())

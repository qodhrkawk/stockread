"""매일 자동 파이프라인 스케줄러"""

import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.db.database import init_db
from app.pipeline.collector import collect_all_stocks, collect_stock_data
from app.report.sender import generate_and_send_all
from app.pipeline.landing_preview import generate_and_save as generate_landing
from app.db import queries as db


_collected_data: list[dict] = []


async def job_collect():
    """06:00 KST — 데이터 수집"""
    global _collected_data
    print(f"\n{'='*50}")
    print(f"⏰ [{datetime.now().strftime('%H:%M:%S')}] 데이터 수집 시작")
    print(f"{'='*50}")
    try:
        _collected_data = await collect_all_stocks()
        print(f"✅ 수집 완료: {len(_collected_data)}개 종목")
    except Exception as e:
        print(f"❌ 수집 실패: {e}")
        _collected_data = []


async def job_collect_kr():
    """16:20 KST — 한국 종목만 재수집 (장 마감 후 최신 데이터)"""
    print(f"\n{'='*50}")
    print(f"⏰ [{datetime.now().strftime('%H:%M:%S')}] 🇰🇷 한국 종목 재수집 시작")
    print(f"{'='*50}")
    try:
        stocks = await db.get_all_stocks()
        kr_stocks = [s for s in stocks if s["market"] == "KR"]
        count = 0
        for stock in kr_stocks:
            data = await collect_stock_data(
                ticker=stock["ticker"],
                name_ko=stock["name_ko"],
                market=stock["market"],
            )
            if data:
                count += 1
        print(f"✅ 한국 종목 재수집 완료: {count}/{len(kr_stocks)}개")
    except Exception as e:
        print(f"❌ 한국 종목 재수집 실패: {e}")


async def job_shorts_us():
    """06:30 KST — 미국 쇼츠 생성 (어젯밤 미국 증시)"""
    print(f"\n{'='*50}")
    print(f"⏰ [{datetime.now().strftime('%H:%M:%S')}] 🇺🇸 미국 쇼츠 생성 시작")
    print(f"{'='*50}")
    try:
        from app.pipeline.shorts.pipeline import run_shorts_pipeline
        result = await run_shorts_pipeline(market="US")
        print(f"✅ 미국 쇼츠 완료: {result['mp4_path']}")
    except Exception as e:
        print(f"❌ 미국 쇼츠 실패: {e}")


async def job_send():
    """07:00 KST — 리포트 생성 + 발송"""
    print(f"\n{'='*50}")
    print(f"⏰ [{datetime.now().strftime('%H:%M:%S')}] 리포트 생성 + 발송 시작")
    print(f"{'='*50}")
    try:
        await generate_and_send_all()
    except Exception as e:
        print(f"❌ 발송 실패: {e}")


async def job_shorts_us_notify():
    """07:01 KST — 미국 쇼츠 윤재에게 전송"""
    print(f"\n{'='*50}")
    print(f"⏰ [{datetime.now().strftime('%H:%M:%S')}] 🇺🇸 미국 쇼츠 전송")
    print(f"{'='*50}")
    try:
        from app.pipeline.shorts.pipeline import send_shorts_notification
        await send_shorts_notification(market="US")
        print(f"✅ 미국 쇼츠 전송 완료")
    except Exception as e:
        print(f"❌ 미국 쇼츠 전송 실패: {e}")


async def job_landing():
    """07:10 KST — 랜딩 페이지 데이터 갱신"""
    print(f"\n{'='*50}")
    print(f"⏰ [{datetime.now().strftime('%H:%M:%S')}] 랜딩 데이터 생성")
    print(f"{'='*50}")
    try:
        await generate_landing()
    except Exception as e:
        print(f"❌ 랜딩 데이터 실패: {e}")


async def job_shorts_kr():
    """16:30 KST — 한국 쇼츠 생성 (오늘 한국 증시)"""
    print(f"\n{'='*50}")
    print(f"⏰ [{datetime.now().strftime('%H:%M:%S')}] 🇰🇷 한국 쇼츠 생성 시작")
    print(f"{'='*50}")
    try:
        from app.pipeline.shorts.pipeline import run_shorts_pipeline
        result = await run_shorts_pipeline(market="KR")
        print(f"✅ 한국 쇼츠 완료: {result['mp4_path']}")
    except Exception as e:
        print(f"❌ 한국 쇼츠 실패: {e}")


async def job_shorts_kr_notify():
    """17:00 KST — 한국 쇼츠 윤재에게 전송"""
    print(f"\n{'='*50}")
    print(f"⏰ [{datetime.now().strftime('%H:%M:%S')}] 🇰🇷 한국 쇼츠 전송")
    print(f"{'='*50}")
    try:
        from app.pipeline.shorts.pipeline import send_shorts_notification
        await send_shorts_notification(market="KR")
        print(f"✅ 한국 쇼츠 전송 완료")
    except Exception as e:
        print(f"❌ 한국 쇼츠 전송 실패: {e}")


def create_scheduler() -> AsyncIOScheduler:
    """스케줄러 생성"""
    scheduler = AsyncIOScheduler(timezone="Asia/Seoul")

    # 매일 06:00 — 데이터 수집
    scheduler.add_job(
        job_collect,
        CronTrigger(hour=6, minute=0, timezone="Asia/Seoul"),
        id="daily_collect",
        name="매일 데이터 수집",
        replace_existing=True,
    )

    # 매일 06:30 — 🇺🇸 미국 쇼츠 생성
    scheduler.add_job(
        job_shorts_us,
        CronTrigger(hour=6, minute=30, timezone="Asia/Seoul"),
        id="daily_shorts_us",
        name="🇺🇸 미국 쇼츠 생성",
        replace_existing=True,
    )

    # 매일 07:00 — 리포트 발송
    scheduler.add_job(
        job_send,
        CronTrigger(hour=7, minute=0, timezone="Asia/Seoul"),
        id="daily_send",
        name="매일 리포트 발송",
        replace_existing=True,
    )

    # 매일 07:01 — 🇺🇸 미국 쇼츠 전송
    scheduler.add_job(
        job_shorts_us_notify,
        CronTrigger(hour=7, minute=1, timezone="Asia/Seoul"),
        id="daily_shorts_us_notify",
        name="🇺🇸 미국 쇼츠 전송",
        replace_existing=True,
    )

    # 매일 07:10 — 랜딩 갱신
    scheduler.add_job(
        job_landing,
        CronTrigger(hour=7, minute=10, timezone="Asia/Seoul"),
        id="daily_landing",
        name="랜딩 데이터 갱신",
        replace_existing=True,
    )

    # 매일 16:20 — 🇰🇷 한국 종목 재수집 (장 마감 후)
    scheduler.add_job(
        job_collect_kr,
        CronTrigger(hour=16, minute=20, timezone="Asia/Seoul"),
        id="daily_collect_kr",
        name="🇰🇷 한국 종목 재수집",
        replace_existing=True,
    )

    # 매일 16:30 — 🇰🇷 한국 쇼츠 생성
    scheduler.add_job(
        job_shorts_kr,
        CronTrigger(hour=16, minute=30, timezone="Asia/Seoul"),
        id="daily_shorts_kr",
        name="🇰🇷 한국 쇼츠 생성",
        replace_existing=True,
    )

    # 매일 17:00 — 🇰🇷 한국 쇼츠 전송
    scheduler.add_job(
        job_shorts_kr_notify,
        CronTrigger(hour=17, minute=0, timezone="Asia/Seoul"),
        id="daily_shorts_kr_notify",
        name="🇰🇷 한국 쇼츠 전송",
        replace_existing=True,
    )

    return scheduler


def print_schedule(scheduler: AsyncIOScheduler):
    """등록된 작업 출력"""
    print("\n📅 스케줄 등록 완료:")
    for job in scheduler.get_jobs():
        print(f"  • {job.name} → {job.trigger}")
    print()

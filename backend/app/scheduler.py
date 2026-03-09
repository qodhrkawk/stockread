"""매일 자동 파이프라인 스케줄러"""

import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.db.database import init_db
from app.pipeline.collector import collect_all_stocks
from app.report.sender import generate_and_send_all
from app.pipeline.landing_preview import generate_and_save as generate_landing


# 수집된 데이터 임시 저장 (수집 → 발송 사이 공유)
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


async def job_shorts():
    """06:30 KST — 쇼츠 스크립트 + TTS + MP4 생성"""
    print(f"\n{'='*50}")
    print(f"⏰ [{datetime.now().strftime('%H:%M:%S')}] 쇼츠 파이프라인 시작")
    print(f"{'='*50}")
    try:
        from app.pipeline.shorts.pipeline import run_shorts_pipeline
        result = await run_shorts_pipeline()
        print(f"✅ 쇼츠 완료: {result['mp4_path']} (오디오: {result['has_audio']})")
    except Exception as e:
        print(f"❌ 쇼츠 실패: {e}")


async def job_send():
    """07:00 KST — 리포트 생성 + 발송"""
    print(f"\n{'='*50}")
    print(f"⏰ [{datetime.now().strftime('%H:%M:%S')}] 리포트 생성 + 발송 시작")
    print(f"{'='*50}")
    try:
        await generate_and_send_all()
    except Exception as e:
        print(f"❌ 발송 실패: {e}")


async def job_landing():
    """07:10 KST — 랜딩 페이지 데이터 갱신"""
    print(f"\n{'='*50}")
    print(f"⏰ [{datetime.now().strftime('%H:%M:%S')}] 랜딩 데이터 생성")
    print(f"{'='*50}")
    try:
        await generate_landing()
    except Exception as e:
        print(f"❌ 랜딩 데이터 실패: {e}")


async def job_shorts_notify():
    """09:00 KST — 쇼츠 MP4 윤재에게 전송"""
    print(f"\n{'='*50}")
    print(f"⏰ [{datetime.now().strftime('%H:%M:%S')}] 쇼츠 알림 전송")
    print(f"{'='*50}")
    try:
        from app.pipeline.shorts.pipeline import send_shorts_notification
        await send_shorts_notification()
        print(f"✅ 쇼츠 전송 완료")
    except Exception as e:
        print(f"❌ 쇼츠 전송 실패: {e}")


def create_scheduler() -> AsyncIOScheduler:
    """스케줄러 생성"""
    scheduler = AsyncIOScheduler(timezone="Asia/Seoul")

    # 매일 06:00 KST — 데이터 수집
    scheduler.add_job(
        job_collect,
        CronTrigger(hour=6, minute=0, timezone="Asia/Seoul"),
        id="daily_collect",
        name="매일 데이터 수집",
        replace_existing=True,
    )

    # 매일 06:30 KST — 쇼츠 생성
    scheduler.add_job(
        job_shorts,
        CronTrigger(hour=6, minute=30, timezone="Asia/Seoul"),
        id="daily_shorts",
        name="매일 쇼츠 생성",
        replace_existing=True,
    )

    # 매일 07:00 KST — 리포트 생성 + 발송
    scheduler.add_job(
        job_send,
        CronTrigger(hour=7, minute=0, timezone="Asia/Seoul"),
        id="daily_send",
        name="매일 리포트 발송",
        replace_existing=True,
    )

    # 매일 07:10 KST — 랜딩 페이지 갱신 (리포트 생성 후)
    scheduler.add_job(
        job_landing,
        CronTrigger(hour=7, minute=10, timezone="Asia/Seoul"),
        id="daily_landing",
        name="랜딩 데이터 갱신",
        replace_existing=True,
    )

    # 매일 09:00 KST — 쇼츠 MP4 오너에게 전송 (검토용)
    scheduler.add_job(
        job_shorts_notify,
        CronTrigger(hour=9, minute=0, timezone="Asia/Seoul"),
        id="daily_shorts_notify",
        name="쇼츠 오너 전송",
        replace_existing=True,
    )

    return scheduler


def print_schedule(scheduler: AsyncIOScheduler):
    """등록된 작업 출력"""
    print("\n📅 스케줄 등록 완료:")
    for job in scheduler.get_jobs():
        print(f"  • {job.name} → {job.trigger}")
    print()

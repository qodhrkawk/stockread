"""리포트 발송 — 텔레그램으로 리포트 전송"""

import os
import json
from datetime import datetime
from telegram import Bot

from app.db import queries as db
from app.pipeline.collector import collect_all_stocks
from .generator import generate_report, format_report_message

BOT_TOKEN = os.environ.get("StockRead_BOT_TOKEN", "")

# 랜딩 페이지 프리뷰 종목 (구독 여부 무관하게 매일 리포트 생성)
LANDING_STOCKS = ["NVDA", "TSLA", "005930", "AAPL", "000660"]
LANDING_RISK_TYPES = ["안정", "중립", "공격"]


async def _get_or_generate_report(data: dict, risk_type: str, today: str) -> dict | str | None:
    """DB 캐시 먼저 확인 → 없으면 Claude 호출 → DB 저장. dict(JSON) 또는 str(레거시) 반환."""
    ticker = data["ticker"]

    # 1. DB 캐시 확인
    cached = await db.get_report(ticker, today, risk_type)
    if cached and cached.get("report_json"):
        try:
            report_data = json.loads(cached["report_json"])
            # 새 JSON 구조 (position, news 등)
            if "position" in report_data and "news" in report_data:
                print(f"   💾 캐시 사용 (JSON): {data['name_ko']} ({risk_type})")
                return report_data
            # 레거시 text 구조
            text = report_data.get("text")
            if text:
                print(f"   💾 캐시 사용: {data['name_ko']} ({risk_type})")
                return text
        except (json.JSONDecodeError, KeyError):
            pass

    # 2. Claude 호출 (이제 dict 반환)
    print(f"   🤖 리포트 생성: {data['name_ko']} ({risk_type})")
    try:
        report = await generate_report(data, risk_type)
    except Exception as e:
        print(f"   ❌ 생성 실패 ({ticker}/{risk_type}): {e}")
        return None

    # 3. DB 저장
    await db.save_report(
        ticker, today, risk_type,
        json.dumps(report, ensure_ascii=False),
    )

    return report


async def _generate_landing_reports(data_map: dict, today: str):
    """랜딩 페이지용 5종목 × 3성향 리포트 자동 생성 (구독 여부 무관)"""
    print("\n🌐 [4/4] 랜딩 프리뷰 리포트 생성...")
    generated = 0
    cached = 0

    for ticker in LANDING_STOCKS:
        if ticker not in data_map:
            print(f"   ⚠️ {ticker} 데이터 없음, 스킵")
            continue

        data = data_map[ticker]
        for risk_type in LANDING_RISK_TYPES:
            # DB에 이미 있으면 스킵
            existing = await db.get_report(ticker, today, risk_type)
            if existing and existing.get("report_json"):
                try:
                    rd = json.loads(existing["report_json"])
                    if rd.get("text"):
                        cached += 1
                        continue
                except (json.JSONDecodeError, KeyError):
                    pass

            # 생성
            print(f"   🤖 랜딩용: {data['name_ko']} ({risk_type})")
            try:
                report = await generate_report(data, risk_type)
                await db.save_report(
                    ticker, today, risk_type,
                    json.dumps(report, ensure_ascii=False),
                )
                generated += 1
            except Exception as e:
                print(f"   ❌ 실패 ({ticker}/{risk_type}): {e}")

    print(f"   ✅ 랜딩 리포트: 신규 {generated}건, 캐시 {cached}건")


async def generate_and_send_all():
    """전체 파이프라인: 데이터 수집 → 리포트 생성 → 발송 → 랜딩 리포트"""
    bot = Bot(token=BOT_TOKEN)
    today = datetime.now().strftime("%Y-%m-%d")

    # 1. 데이터 수집
    print("📊 [1/3] 데이터 수집 시작...")
    all_data = await collect_all_stocks()
    data_map = {d["ticker"]: d for d in all_data}

    # 2. 구독자 조회
    print("👥 [2/3] 구독자 조회...")
    subscribers = await db.get_all_subscribers()

    if not subscribers:
        print("⚠️ 구독자가 없습니다")
    
    # 유저별 그룹핑
    user_subs = {}
    for s in (subscribers or []):
        tg_id = s["telegram_id"]
        if tg_id not in user_subs:
            user_subs[tg_id] = {"risk_type": s["risk_type"], "tickers": []}
        user_subs[tg_id]["tickers"].append(s["ticker"])

    print(f"   {len(user_subs)}명, 총 {len(subscribers or [])}건 발송 예정")

    # 3. 리포트 생성 + 발송
    print("📝 [3/3] 리포트 생성 + 발송...")
    sent_count = 0
    error_count = 0
    cache_hit = 0
    cache_miss = 0

    # 메모리 캐시 (같은 실행 내 중복 방지)
    mem_cache: dict[str, str] = {}

    for tg_id, info in user_subs.items():
        risk_type = info["risk_type"]

        for ticker in info["tickers"]:
            if ticker not in data_map:
                print(f"   ⚠️ {ticker} 데이터 없음, 스킵")
                continue

            data = data_map[ticker]
            cache_key = f"{ticker}:{risk_type}:{today}"

            # 메모리 캐시 확인 (같은 실행 내)
            if cache_key in mem_cache:
                report = mem_cache[cache_key]
                cache_hit += 1
            else:
                # DB 캐시 or Claude 호출
                report = await _get_or_generate_report(data, risk_type, today)
                if report:
                    mem_cache[cache_key] = report
                    cache_miss += 1
                else:
                    error_count += 1
                    continue

            # 텔레그램 발송
            message = format_report_message(data, risk_type, report)
            try:
                await bot.send_message(chat_id=tg_id, text=message)
                sent_count += 1
                print(f"   ✅ {tg_id} ← {data['name_ko']}")
            except Exception as e:
                print(f"   ❌ 발송 실패 ({tg_id}/{ticker}): {e}")
                error_count += 1

    print()
    print(f"🎉 발송 완료! 성공: {sent_count}건, 실패: {error_count}건")
    print(f"   캐시 히트: {cache_hit}건, 신규 생성: {cache_miss}건")

    # 4. 랜딩 페이지용 리포트 생성
    await _generate_landing_reports(data_map, today)

    # 오너에게 발송 요약 알림
    OWNER_ID = "7923407207"
    summary = (
        f"📋 주읽이 발송 완료 ({today})\n"
        f"\n"
        f"👥 구독자: {len(user_subs)}명\n"
        f"✅ 발송 성공: {sent_count}건\n"
        f"❌ 발송 실패: {error_count}건\n"
        f"🤖 신규 생성: {cache_miss}건 / 💾 캐시: {cache_hit}건"
    )
    try:
        await bot.send_message(chat_id=OWNER_ID, text=summary)
    except Exception as e:
        print(f"   ⚠️ 오너 알림 실패: {e}")


async def send_test_report(telegram_id: str, ticker: str, risk_type: str = "중립"):
    """테스트용 단일 리포트 발송"""
    from app.pipeline.collector import collect_stock_data
    from app.db.database import init_db

    await init_db()
    bot = Bot(token=BOT_TOKEN)
    today = datetime.now().strftime("%Y-%m-%d")

    # 종목 정보 조회
    stocks = await db.get_all_stocks()
    stock = next((s for s in stocks if s["ticker"] == ticker), None)
    if not stock:
        print(f"❌ 종목 없음: {ticker}")
        return

    # 데이터 수집
    data = await collect_stock_data(ticker, stock["name_ko"], stock["market"])
    if not data:
        print("❌ 데이터 수집 실패")
        return

    # DB 캐시 or 생성
    report = await _get_or_generate_report(data, risk_type, today)
    if not report:
        print("❌ 리포트 생성 실패")
        return

    # 메시지 포맷 + 발송
    message = format_report_message(data, risk_type, report)
    await bot.send_message(chat_id=telegram_id, text=message)
    print(f"✅ 발송 완료! → {telegram_id}")

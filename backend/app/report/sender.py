"""리포트 발송 — 텔레그램으로 리포트 전송"""

import os
import json
from datetime import datetime
from telegram import Bot

from app.db import queries as db
from app.pipeline.collector import collect_all_stocks
from .generator import generate_report, format_report_message

BOT_TOKEN = os.environ.get("StockRead_BOT_TOKEN", "")


async def generate_and_send_all():
    """전체 파이프라인: 데이터 수집 → 리포트 생성 → 발송"""
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
        return

    # 유저별 그룹핑
    user_subs = {}
    for s in subscribers:
        tg_id = s["telegram_id"]
        if tg_id not in user_subs:
            user_subs[tg_id] = {"risk_type": s["risk_type"], "tickers": []}
        user_subs[tg_id]["tickers"].append(s["ticker"])

    print(f"   {len(user_subs)}명, 총 {len(subscribers)}건 발송 예정")

    # 3. 리포트 생성 + 발송
    print("📝 [3/3] 리포트 생성 + 발송...")
    sent_count = 0
    error_count = 0

    # 리포트 캐시 (같은 종목+성향은 1번만 생성)
    report_cache = {}

    for tg_id, info in user_subs.items():
        risk_type = info["risk_type"]

        for ticker in info["tickers"]:
            if ticker not in data_map:
                print(f"   ⚠️ {ticker} 데이터 없음, 스킵")
                continue

            data = data_map[ticker]
            cache_key = f"{ticker}:{risk_type}"

            # 캐시 확인
            if cache_key not in report_cache:
                try:
                    # AI 리포트 생성
                    report_text = await generate_report(data, risk_type)
                    report_cache[cache_key] = report_text

                    # DB 저장
                    await db.save_report(
                        ticker, today, risk_type,
                        json.dumps({"text": report_text}, ensure_ascii=False),
                    )
                except Exception as e:
                    print(f"   ❌ 리포트 생성 실패 ({ticker}/{risk_type}): {e}")
                    error_count += 1
                    continue

            report_text = report_cache[cache_key]

            # 텔레그램 메시지 포맷
            message = format_report_message(data, risk_type, report_text)

            # 발송
            try:
                await bot.send_message(
                    chat_id=tg_id,
                    text=message,
                    parse_mode=None,  # 플레인 텍스트
                )
                sent_count += 1
                print(f"   ✅ {tg_id} ← {data['name_ko']}")
            except Exception as e:
                print(f"   ❌ 발송 실패 ({tg_id}/{ticker}): {e}")
                error_count += 1

    print()
    print(f"🎉 발송 완료! 성공: {sent_count}건, 실패: {error_count}건")


async def send_test_report(telegram_id: str, ticker: str, risk_type: str = "중립"):
    """테스트용 단일 리포트 발송"""
    from app.pipeline.collector import collect_stock_data
    from app.db.database import init_db

    await init_db()
    bot = Bot(token=BOT_TOKEN)

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

    # 리포트 생성
    print(f"📝 리포트 생성 중 ({stock['name_ko']}, {risk_type})...")
    report_text = await generate_report(data, risk_type)

    # 메시지 포맷
    message = format_report_message(data, risk_type, report_text)

    # 발송
    await bot.send_message(chat_id=telegram_id, text=message)
    print(f"✅ 발송 완료! → {telegram_id}")

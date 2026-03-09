"""텔레그램 봇 핸들러"""

from telegram import Update
from telegram.ext import ContextTypes

from app.db import queries
from .constants import (
    RISK_TYPES,
    RISK_PREFIX,
    STOCK_PREFIX,
    DONE_PREFIX,
    EDIT_PREFIX,
    MSG_WELCOME,
    MSG_RISK_SELECTED,
    MSG_ONBOARDING_DONE,
    MSG_MY,
    MSG_NO_ONBOARDING,
    MSG_STOCK_LIMIT,
    MSG_HELP,
    MSG_EDIT_CHOOSE,
)
from .keyboards import risk_keyboard, stock_keyboard, edit_keyboard


# ==================== 명령어 핸들러 ====================


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start — 온보딩 시작"""
    tg_id = str(update.effective_user.id)

    # 유저 생성 (이미 있으면 무시)
    await queries.create_user(tg_id)

    # 기존 구독 초기화
    await queries.clear_subscriptions(tg_id)

    await update.message.reply_text(
        MSG_WELCOME,
        parse_mode="HTML",
        reply_markup=risk_keyboard(),
    )


async def my_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/my — 현재 설정 확인"""
    tg_id = str(update.effective_user.id)
    user = await queries.get_user(tg_id)

    if not user or not user["onboarding_done"]:
        await update.message.reply_text(MSG_NO_ONBOARDING)
        return

    subs = await queries.get_subscriptions(tg_id)
    risk_info = RISK_TYPES.get(user["risk_type"], RISK_TYPES["중립"])
    stock_names = ", ".join(s["name_ko"] for s in subs) if subs else "없음"

    await update.message.reply_text(
        MSG_MY.format(
            risk_emoji=risk_info["emoji"],
            risk_label=risk_info["label"],
            stocks=stock_names,
        ),
        parse_mode="HTML",
    )


async def edit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/edit — 설정 변경"""
    tg_id = str(update.effective_user.id)
    user = await queries.get_user(tg_id)

    if not user or not user["onboarding_done"]:
        await update.message.reply_text(MSG_NO_ONBOARDING)
        return

    await update.message.reply_text(
        MSG_EDIT_CHOOSE,
        parse_mode="HTML",
        reply_markup=edit_keyboard(),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/help — 명령어 안내"""
    await update.message.reply_text(MSG_HELP, parse_mode="HTML")


# ==================== 콜백 핸들러 ====================


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """인라인 버튼 콜백 라우터"""
    query = update.callback_query
    await query.answer()

    data = query.data
    if data == "noop":
        return

    if data.startswith(RISK_PREFIX):
        await _handle_risk(query, context)
    elif data.startswith(STOCK_PREFIX):
        await _handle_stock(query, context)
    elif data.startswith(DONE_PREFIX):
        await _handle_done(query, context)
    elif data.startswith(EDIT_PREFIX):
        await _handle_edit(query, context)


async def _handle_risk(query, context):
    """성향 선택 처리"""
    risk_type = query.data.replace(RISK_PREFIX, "")
    tg_id = str(query.from_user.id)

    await queries.update_risk_type(tg_id, risk_type)

    # context에 저장 (온보딩 플로우 추적)
    context.user_data["editing_risk"] = False

    risk_info = RISK_TYPES[risk_type]

    # edit에서 온 성향 변경인지 확인
    if context.user_data.get("editing_risk"):
        context.user_data["editing_risk"] = False
        user = await queries.get_user(tg_id)
        subs = await queries.get_subscriptions(tg_id)
        stock_names = ", ".join(s["name_ko"] for s in subs) if subs else "없음"

        await query.edit_message_text(
            f"✅ 성향이 {risk_info['emoji']} <b>{risk_info['label']}</b>으로 변경됐어요!\n\n"
            f"📊 구독 종목: {stock_names}",
            parse_mode="HTML",
        )
        return

    # 온보딩: 종목 선택으로 이동
    all_stocks = await queries.get_all_stocks()
    subs = await queries.get_subscriptions(tg_id)
    selected = [s["ticker"] for s in subs]

    await query.edit_message_text(
        MSG_RISK_SELECTED.format(emoji=risk_info["emoji"], label=risk_info["label"]),
        parse_mode="HTML",
        reply_markup=stock_keyboard(all_stocks, selected),
    )


async def _handle_stock(query, context):
    """종목 토글 처리"""
    ticker = query.data.replace(STOCK_PREFIX, "")
    tg_id = str(query.from_user.id)

    # 현재 구독 목록 확인
    subs = await queries.get_subscriptions(tg_id)
    selected = [s["ticker"] for s in subs]

    if ticker in selected:
        # 이미 구독 중 → 해제
        await queries.remove_subscription(tg_id, ticker)
        selected.remove(ticker)
    else:
        # 새로 추가
        if len(selected) >= 3:
            # 3개 제한 — 알림만 보내고 키보드 유지
            await query.answer(MSG_STOCK_LIMIT, show_alert=True)
            return
        await queries.add_subscription(tg_id, ticker)
        selected.append(ticker)

    # 키보드 업데이트
    all_stocks = await queries.get_all_stocks()
    user = await queries.get_user(tg_id)
    risk_info = RISK_TYPES.get(user["risk_type"], RISK_TYPES["중립"])

    # 메시지 텍스트 (현재 선택 상태 표시)
    if selected:
        stock_names = []
        for t in selected:
            st = next((s for s in all_stocks if s["ticker"] == t), None)
            if st:
                stock_names.append(st["name_ko"])
        status = f"선택: {', '.join(stock_names)} ({len(selected)}/3)"
    else:
        status = "아직 선택 안 했어요"

    text = (
        f"{risk_info['emoji']} <b>{risk_info['label']}</b>으로 설정했어요!\n\n"
        f"관심 종목을 선택해주세요 (최대 3개):\n"
        f"📌 {status}\n\n"
        f"선택이 끝나면 아래 <b>완료</b> 버튼을 눌러주세요."
    )

    await query.edit_message_text(
        text,
        parse_mode="HTML",
        reply_markup=stock_keyboard(all_stocks, selected),
    )


async def _handle_done(query, context):
    """완료 버튼 처리"""
    tg_id = str(query.from_user.id)

    subs = await queries.get_subscriptions(tg_id)
    if not subs:
        await query.answer("최소 1개 종목을 선택해주세요!", show_alert=True)
        return

    user = await queries.get_user(tg_id)
    risk_info = RISK_TYPES.get(user["risk_type"], RISK_TYPES["중립"])

    # 온보딩 완료 처리
    await queries.set_onboarding_done(tg_id)

    stock_names = ", ".join(s["name_ko"] for s in subs)

    await query.edit_message_text(
        MSG_ONBOARDING_DONE.format(
            stocks=stock_names,
            risk_emoji=risk_info["emoji"],
            risk_label=risk_info["label"],
        ),
        parse_mode="HTML",
    )


async def _handle_edit(query, context):
    """설정 변경 메뉴 처리"""
    action = query.data.replace(EDIT_PREFIX, "")
    tg_id = str(query.from_user.id)

    if action == "risk":
        context.user_data["editing_risk"] = True
        await query.edit_message_text(
            "🎯 <b>투자 성향 변경</b>\n\n새로운 성향을 선택해주세요:",
            parse_mode="HTML",
            reply_markup=risk_keyboard(),
        )
    elif action == "stocks":
        all_stocks = await queries.get_all_stocks()
        # edit에서는 기존 구독 초기화하고 새로 선택
        await queries.clear_subscriptions(tg_id)

        user = await queries.get_user(tg_id)
        risk_info = RISK_TYPES.get(user["risk_type"], RISK_TYPES["중립"])

        await query.edit_message_text(
            f"{risk_info['emoji']} <b>{risk_info['label']}</b>\n\n"
            f"관심 종목을 다시 선택해주세요 (최대 3개):\n\n"
            f"선택이 끝나면 아래 <b>완료</b> 버튼을 눌러주세요.",
            parse_mode="HTML",
            reply_markup=stock_keyboard(all_stocks, []),
        )

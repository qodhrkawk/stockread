"""인라인 키보드 생성"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from .constants import RISK_TYPES, RISK_PREFIX, STOCK_PREFIX, DONE_PREFIX, EDIT_PREFIX


def risk_keyboard() -> InlineKeyboardMarkup:
    """성향 선택 키보드"""
    buttons = []
    for key, info in RISK_TYPES.items():
        buttons.append(
            InlineKeyboardButton(
                f"{info['emoji']} {info['label']}",
                callback_data=f"{RISK_PREFIX}{key}",
            )
        )
    return InlineKeyboardMarkup([buttons])


def stock_keyboard(
    stocks: list[dict], selected_tickers: list[str]
) -> InlineKeyboardMarkup:
    """종목 선택 키보드 (토글 방식)"""
    us_stocks = [s for s in stocks if s["market"] == "US"]
    kr_stocks = [s for s in stocks if s["market"] == "KR"]

    rows = []

    # 🇺🇸 미국
    rows.append([InlineKeyboardButton("🇺🇸 미국", callback_data="noop")])
    us_row = []
    for s in us_stocks:
        check = "✅ " if s["ticker"] in selected_tickers else ""
        label = s.get("name_ko", s["ticker"])
        # ETF는 티커 그대로
        if s["ticker"] in ("SPY", "QQQ"):
            label = s["ticker"]
        us_row.append(
            InlineKeyboardButton(
                f"{check}{label}",
                callback_data=f"{STOCK_PREFIX}{s['ticker']}",
            )
        )
        if len(us_row) == 3:
            rows.append(us_row)
            us_row = []
    if us_row:
        rows.append(us_row)

    # 🇰🇷 한국
    rows.append([InlineKeyboardButton("🇰🇷 한국", callback_data="noop")])
    kr_row = []
    for s in kr_stocks:
        check = "✅ " if s["ticker"] in selected_tickers else ""
        kr_row.append(
            InlineKeyboardButton(
                f"{check}{s['name_ko']}",
                callback_data=f"{STOCK_PREFIX}{s['ticker']}",
            )
        )
        if len(kr_row) == 3:
            rows.append(kr_row)
            kr_row = []
    if kr_row:
        rows.append(kr_row)

    # 완료 버튼
    rows.append(
        [InlineKeyboardButton("✅ 완료", callback_data=f"{DONE_PREFIX}stocks")]
    )

    return InlineKeyboardMarkup(rows)


def edit_keyboard() -> InlineKeyboardMarkup:
    """설정 변경 메뉴"""
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🎯 투자 성향 변경", callback_data=f"{EDIT_PREFIX}risk"
                ),
                InlineKeyboardButton(
                    "📊 종목 변경", callback_data=f"{EDIT_PREFIX}stocks"
                ),
            ]
        ]
    )

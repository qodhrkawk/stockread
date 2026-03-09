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


# 버튼용 짧은 이름 (텔레그램 인라인 버튼 글자수 제한 대응)
SHORT_NAMES = {
    "S&P 500 ETF": "S&P 500",
    "나스닥 100 ETF": "나스닥100",
    "반도체 ETF": "반도체ETF",
    "마이크로소프트": "MS",
    "삼성바이오로직스": "삼바",
    "LG에너지솔루션": "LG에솔",
    "에코프로비엠": "에코프로BM",
    "KODEX 200": "KODEX200",
    "KODEX 레버리지": "KODEX레버",
    "TIGER 미국S&P500": "TIGER S&P",
}


def _stock_label(stock: dict, selected_tickers: list[str]) -> str:
    """종목 버튼 라벨 생성"""
    check = "✅ " if stock["ticker"] in selected_tickers else ""
    name = SHORT_NAMES.get(stock["name_ko"], stock["name_ko"])
    if len(name) > 8:
        name = name[:8]
    return f"{check}{name}"


def stock_keyboard(
    stocks: list[dict], selected_tickers: list[str]
) -> InlineKeyboardMarkup:
    """종목 선택 키보드 (토글 방식, 2열)"""
    us_stocks = [s for s in stocks if s["market"] == "US"]
    kr_stocks = [s for s in stocks if s["market"] == "KR"]

    rows = []

    # 🇺🇸 미국
    rows.append([InlineKeyboardButton("🇺🇸 미국", callback_data="noop")])
    row = []
    for s in us_stocks:
        row.append(
            InlineKeyboardButton(
                _stock_label(s, selected_tickers),
                callback_data=f"{STOCK_PREFIX}{s['ticker']}",
            )
        )
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)

    # 🇰🇷 한국
    rows.append([InlineKeyboardButton("🇰🇷 한국", callback_data="noop")])
    row = []
    for s in kr_stocks:
        row.append(
            InlineKeyboardButton(
                _stock_label(s, selected_tickers),
                callback_data=f"{STOCK_PREFIX}{s['ticker']}",
            )
        )
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)

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

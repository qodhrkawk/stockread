"""
StockRead DB Queries
- 모든 DB 조회/수정은 여기서만
"""

from .database import get_db


# ==================== USERS ====================

async def get_user(telegram_id: str) -> dict | None:
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None
    finally:
        await db.close()


async def create_user(telegram_id: str, risk_type: str = "중립") -> int:
    db = await get_db()
    try:
        cursor = await db.execute(
            "INSERT INTO users (telegram_id, risk_type) VALUES (?, ?) "
            "ON CONFLICT(telegram_id) DO UPDATE SET risk_type = ?, updated_at = datetime('now')",
            (telegram_id, risk_type, risk_type),
        )
        await db.commit()
        return cursor.lastrowid
    finally:
        await db.close()


async def update_risk_type(telegram_id: str, risk_type: str):
    db = await get_db()
    try:
        await db.execute(
            "UPDATE users SET risk_type = ?, updated_at = datetime('now') WHERE telegram_id = ?",
            (risk_type, telegram_id),
        )
        await db.commit()
    finally:
        await db.close()


async def set_onboarding_done(telegram_id: str):
    db = await get_db()
    try:
        await db.execute(
            "UPDATE users SET onboarding_done = 1, updated_at = datetime('now') WHERE telegram_id = ?",
            (telegram_id,),
        )
        await db.commit()
    finally:
        await db.close()


# ==================== SUBSCRIPTIONS ====================

async def get_subscriptions(telegram_id: str) -> list[dict]:
    db = await get_db()
    try:
        cursor = await db.execute(
            """
            SELECT s.ticker, st.name_ko, st.name_en, st.market
            FROM subscriptions s
            JOIN users u ON s.user_id = u.id
            JOIN stocks st ON s.ticker = st.ticker
            WHERE u.telegram_id = ?
            ORDER BY st.market, st.name_ko
            """,
            (telegram_id,),
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        await db.close()


async def add_subscription(telegram_id: str, ticker: str) -> bool:
    """구독 추가. 성공=True, 이미 3개면 False"""
    db = await get_db()
    try:
        # 유저 id 조회
        cursor = await db.execute(
            "SELECT id FROM users WHERE telegram_id = ?", (telegram_id,)
        )
        user = await cursor.fetchone()
        if not user:
            return False

        # 현재 구독 수 확인
        cursor = await db.execute(
            "SELECT COUNT(*) as cnt FROM subscriptions WHERE user_id = ?",
            (user["id"],),
        )
        count = (await cursor.fetchone())["cnt"]
        if count >= 3:
            return False

        await db.execute(
            "INSERT OR IGNORE INTO subscriptions (user_id, ticker) VALUES (?, ?)",
            (user["id"], ticker),
        )
        await db.commit()
        return True
    finally:
        await db.close()


async def remove_subscription(telegram_id: str, ticker: str):
    db = await get_db()
    try:
        await db.execute(
            """
            DELETE FROM subscriptions
            WHERE user_id = (SELECT id FROM users WHERE telegram_id = ?)
            AND ticker = ?
            """,
            (telegram_id, ticker),
        )
        await db.commit()
    finally:
        await db.close()


async def clear_subscriptions(telegram_id: str):
    db = await get_db()
    try:
        await db.execute(
            "DELETE FROM subscriptions WHERE user_id = (SELECT id FROM users WHERE telegram_id = ?)",
            (telegram_id,),
        )
        await db.commit()
    finally:
        await db.close()


# ==================== STOCKS ====================

async def get_all_stocks() -> list[dict]:
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM stocks WHERE is_active = 1 ORDER BY market, name_ko"
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        await db.close()


async def get_stocks_by_market(market: str) -> list[dict]:
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM stocks WHERE market = ? AND is_active = 1 ORDER BY name_ko",
            (market,),
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        await db.close()


# ==================== REPORTS ====================

async def save_report(ticker: str, report_date: str, risk_type: str, report_json: str):
    db = await get_db()
    try:
        await db.execute(
            """
            INSERT INTO daily_reports (ticker, report_date, risk_type, report_json)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(ticker, report_date, risk_type) DO UPDATE SET
                report_json = ?, status = 'generated'
            """,
            (ticker, report_date, risk_type, report_json, report_json),
        )
        await db.commit()
    finally:
        await db.close()


async def get_report(ticker: str, report_date: str, risk_type: str) -> dict | None:
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM daily_reports WHERE ticker = ? AND report_date = ? AND risk_type = ?",
            (ticker, report_date, risk_type),
        )
        row = await cursor.fetchone()
        return dict(row) if row else None
    finally:
        await db.close()


async def get_all_subscribers() -> list[dict]:
    """리포트 발송 대상: 온보딩 완료 + 구독 종목 있는 유저"""
    db = await get_db()
    try:
        cursor = await db.execute(
            """
            SELECT u.telegram_id, u.risk_type, s.ticker, st.name_ko, st.market
            FROM users u
            JOIN subscriptions s ON u.id = s.user_id
            JOIN stocks st ON s.ticker = st.ticker
            WHERE u.onboarding_done = 1
            ORDER BY u.telegram_id, st.market, st.name_ko
            """
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        await db.close()


# ==================== PRICE CACHE ====================

async def save_price(ticker: str, price_date: str, data_json: str):
    db = await get_db()
    try:
        await db.execute(
            """
            INSERT INTO price_cache (ticker, price_date, data_json)
            VALUES (?, ?, ?)
            ON CONFLICT(ticker, price_date) DO UPDATE SET data_json = ?
            """,
            (ticker, price_date, data_json, data_json),
        )
        await db.commit()
    finally:
        await db.close()


async def get_price(ticker: str, price_date: str) -> dict | None:
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM price_cache WHERE ticker = ? AND price_date = ?",
            (ticker, price_date),
        )
        row = await cursor.fetchone()
        return dict(row) if row else None
    finally:
        await db.close()

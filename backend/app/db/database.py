"""
StockRead SQLite Database Layer
- 비동기 SQLite (aiosqlite)
- 나중에 다른 DB로 마이그레이션 대비, DB 로직 이 레이어에 격리
"""

import aiosqlite
import os
from pathlib import Path

DB_DIR = Path(__file__).parent.parent.parent / "data"
DB_PATH = DB_DIR / "stockread.db"


def get_db_path() -> str:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    return str(DB_PATH)


async def get_db() -> aiosqlite.Connection:
    db = await aiosqlite.connect(get_db_path())
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    return db


async def init_db():
    """DB 초기화 — 테이블 생성"""
    db = await get_db()
    try:
        await db.executescript(SCHEMA)
        await db.executescript(SEED_DATA)
        await db.commit()
    finally:
        await db.close()


SCHEMA = """
-- 사용자
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id     TEXT UNIQUE NOT NULL,
    risk_type       TEXT NOT NULL DEFAULT '중립',  -- 안정 / 중립 / 공격
    onboarding_done INTEGER NOT NULL DEFAULT 0,
    created_at      TEXT DEFAULT (datetime('now')),
    updated_at      TEXT DEFAULT (datetime('now'))
);

-- 지원 종목
CREATE TABLE IF NOT EXISTS stocks (
    ticker      TEXT PRIMARY KEY,
    name_ko     TEXT NOT NULL,
    name_en     TEXT NOT NULL,
    market      TEXT NOT NULL,  -- US / KR
    is_active   INTEGER DEFAULT 1
);

-- 구독 (유저 ↔ 종목)
CREATE TABLE IF NOT EXISTS subscriptions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    ticker      TEXT NOT NULL REFERENCES stocks(ticker),
    created_at  TEXT DEFAULT (datetime('now')),
    UNIQUE(user_id, ticker)
);

-- 일일 리포트
CREATE TABLE IF NOT EXISTS daily_reports (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker          TEXT NOT NULL,
    report_date     TEXT NOT NULL,  -- YYYY-MM-DD
    risk_type       TEXT NOT NULL,  -- 성향별 리포트
    report_json     TEXT,           -- JSON string
    status          TEXT DEFAULT 'generated',  -- generated / sent
    created_at      TEXT DEFAULT (datetime('now')),
    UNIQUE(ticker, report_date, risk_type)
);

-- 쇼츠 콘텐츠
CREATE TABLE IF NOT EXISTS shorts_content (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    content_date    TEXT NOT NULL UNIQUE,  -- YYYY-MM-DD
    script_json     TEXT,           -- JSON string
    mp4_path        TEXT,
    status          TEXT DEFAULT 'generated',  -- generated / sent / uploaded
    created_at      TEXT DEFAULT (datetime('now'))
);

-- 시세 데이터 캐시
CREATE TABLE IF NOT EXISTS price_cache (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker          TEXT NOT NULL,
    price_date      TEXT NOT NULL,  -- YYYY-MM-DD
    data_json       TEXT,           -- 종가, 변동률, RSI 등 전부 JSON
    created_at      TEXT DEFAULT (datetime('now')),
    UNIQUE(ticker, price_date)
);
"""

SEED_DATA = """
-- MVP 지원 종목 (미국 15 + 한국 15)
INSERT OR IGNORE INTO stocks (ticker, name_ko, name_en, market) VALUES
    -- 🇺🇸 미국 빅테크
    ('AAPL',    '애플',           'Apple',              'US'),
    ('MSFT',    '마이크로소프트',    'Microsoft',          'US'),
    ('GOOGL',   '구글',           'Alphabet',           'US'),
    ('AMZN',    '아마존',          'Amazon',             'US'),
    ('META',    '메타',           'Meta Platforms',     'US'),
    -- 🇺🇸 AI/반도체
    ('NVDA',    '엔비디아',        'NVIDIA',             'US'),
    ('AMD',     'AMD',           'AMD',                'US'),
    ('AVGO',    '브로드컴',        'Broadcom',           'US'),
    -- 🇺🇸 전기차
    ('TSLA',    '테슬라',         'Tesla',              'US'),
    -- 🇺🇸 ETF
    ('SPY',     'S&P 500 ETF',   'SPDR S&P 500',       'US'),
    ('QQQ',     '나스닥 100 ETF',  'Invesco QQQ',        'US'),
    ('SOXX',    '반도체 ETF',      'iShares Semiconductor','US'),
    -- 🇺🇸 금융/기타
    ('JPM',     'JP모건',         'JPMorgan Chase',     'US'),
    ('V',       '비자',           'Visa',               'US'),
    ('COST',    '코스트코',        'Costco',             'US'),
    -- 🇰🇷 대형
    ('005930',  '삼성전자',        'Samsung Electronics', 'KR'),
    ('000660',  'SK하이닉스',      'SK Hynix',           'KR'),
    ('005380',  '현대차',         'Hyundai Motor',      'KR'),
    -- 🇰🇷 플랫폼
    ('035420',  'NAVER',         'NAVER',              'KR'),
    ('035720',  '카카오',         'Kakao',              'KR'),
    -- 🇰🇷 2차전지
    ('373220',  'LG에너지솔루션',   'LG Energy Solution', 'KR'),
    ('006400',  '삼성SDI',        'Samsung SDI',        'KR'),
    ('247540',  '에코프로비엠',     'Ecopro BM',          'KR'),
    -- 🇰🇷 바이오
    ('207940',  '삼성바이오로직스',  'Samsung Biologics',   'KR'),
    ('068270',  '셀트리온',        'Celltrion',          'KR'),
    -- 🇰🇷 금융/기타
    ('105560',  'KB금융',         'KB Financial',       'KR'),
    ('012330',  '현대모비스',       'Hyundai Mobis',      'KR'),
    -- 🇰🇷 ETF
    ('069500',  'KODEX 200',     'KODEX 200',          'KR'),
    ('122630',  'KODEX 레버리지',  'KODEX Leverage',     'KR'),
    ('360750',  'TIGER 미국S&P500','TIGER US S&P500',   'KR');
"""

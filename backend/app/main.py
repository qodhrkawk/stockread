from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 서버 시작 시 DB 초기화
    await init_db()
    print("✅ DB initialized")
    yield


app = FastAPI(
    title="StockRead API",
    description="주읽이 — AI 기반 투자 해석 서비스",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return {"service": "StockRead", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "ok"}

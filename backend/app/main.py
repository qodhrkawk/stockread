from fastapi import FastAPI

app = FastAPI(
    title="StockRead API",
    description="주읽이 — AI 기반 투자 해석 서비스",
    version="0.1.0",
)


@app.get("/")
async def root():
    return {"service": "StockRead", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "ok"}

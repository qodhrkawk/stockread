# CLAUDE.md

## 프로젝트 개요
주읽이 (StockRead) — 주린이를 위한 AI 기반 투자 해석 서비스.
매일 아침 AI가 종목을 성향별로 해석해 텔레그램으로 보내주고, 유튜브 쇼츠도 자동 생성.

## 기술 스택
- **Frontend:** Next.js + TypeScript (pnpm) → Vercel 배포
- **Backend:** Python + FastAPI
- **DB:** Supabase (PostgreSQL)
- **AI:** Claude API (리포트 + 스크립트 생성)
- **TTS:** OpenAI TTS (남성, 차분한 뉴스 톤)
- **영상:** Remotion (React 기반 MP4 렌더링)
- **봇:** python-telegram-bot
- **스케줄링:** OpenClaw 크론
- **데이터:** FMP (미국) + KRX/DART (한국)

## 기획 문서
- `docs/PRD.md` — 전체 기능 명세
- `docs/screens/` — 화면별 상세 스펙 (랜딩, 텔레그램 봇)

## 디자인
- `docs/design/html/landing.html` — 확정된 랜딩 디자인 HTML (v4)
- `docs/design/README.md` — 디자인 시스템 요약
- `docs/design/landing.md` — 랜딩 디자인 결정사항
- 디자인 프리뷰: https://qodhrkawk.github.io/design-preview/stockread/landing.html
- 디자인 키워드: 다크모드(#09090b) + 그린(#22c55e), 모바일 퍼스트, shadcn/ui

## 프로젝트 구조
```
stockread/
├── docs/           # 기획 + 디자인 스펙
├── web/            # Next.js 랜딩 페이지
├── backend/        # Python FastAPI
│   └── app/
│       ├── bot/        # 텔레그램 봇
│       ├── pipeline/   # 데이터 수집
│       ├── report/     # AI 리포트 생성
│       ├── shorts/     # 쇼츠 생성
│       └── db/         # Supabase 연동
└── remotion/       # 쇼츠 영상 렌더링
```

## 환경변수
- `StockRead_BOT_TOKEN` — 텔레그램 봇 토큰
- `FINANCIALMODEL_API_KEY` — FMP API 키
- `SUPABASE_URL` — Supabase 프로젝트 URL
- `SUPABASE_KEY` — Supabase anon key
- `ANTHROPIC_API_KEY` — Claude API 키
- `OPENAI_API_KEY` — OpenAI TTS용

## 개발 가이드

### Backend (Python)
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Web (Next.js)
```bash
cd web
pnpm install
pnpm dev
```

### Remotion
```bash
cd remotion
pnpm install
pnpm start  # 프리뷰
pnpm build  # MP4 렌더
```

## 핵심 규칙
- 매수/매도 추천 금지 — "리스크 높음", "변동성 가능성" 등 표현 사용
- 모든 리포트에 면책 문구 포함
- 톤: 해요체, 친근하고 쉬운 말
- 성향: 안정형(보수적) / 중립형(균형) / 공격형(적극적)

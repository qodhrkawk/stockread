"""봇 상수 & 텍스트"""

# 콜백 데이터 접두사
RISK_PREFIX = "risk:"
STOCK_PREFIX = "stock:"
DONE_PREFIX = "done:"
EDIT_PREFIX = "edit:"

# 성향
RISK_TYPES = {
    "안정": {"emoji": "🛡", "label": "안정형", "desc": "리스크 최소화, 안정적 투자"},
    "중립": {"emoji": "⚖️", "label": "중립형", "desc": "균형 잡힌 분석"},
    "공격": {"emoji": "🔥", "label": "공격형", "desc": "기회 포착, 적극적 투자"},
}

# 메시지
MSG_WELCOME = (
    "안녕하세요! 📊 <b>주읽이</b>입니다.\n"
    "매일 아침 7시, AI가 해석한 종목 리포트를 보내드려요.\n\n"
    "먼저 <b>투자 성향</b>을 선택해주세요:"
)

MSG_RISK_SELECTED = (
    "{emoji} <b>{label}</b>으로 설정했어요!\n\n"
    "이제 <b>관심 종목</b>을 선택해주세요 (최대 3개):\n"
    "선택이 끝나면 아래 <b>완료</b> 버튼을 눌러주세요."
)

MSG_ONBOARDING_DONE = (
    "✅ <b>설정 완료!</b>\n\n"
    "📊 구독 종목: {stocks}\n"
    "{risk_emoji} 투자 성향: {risk_label}\n"
    "⏰ 리포트: 매일 오전 7시\n\n"
    "내일 아침부터 리포트를 보내드릴게요!"
)

MSG_MY = (
    "📋 <b>내 설정</b>\n\n"
    "{risk_emoji} 투자 성향: {risk_label}\n"
    "📊 구독 종목: {stocks}\n\n"
    "변경하려면 /edit 을 눌러주세요."
)

MSG_NO_ONBOARDING = (
    "아직 설정이 안 되어 있어요!\n"
    "/start 로 시작해주세요 😊"
)

MSG_STOCK_LIMIT = "⚠️ 최대 3개까지 가능해요. 먼저 다른 종목을 해제해주세요."

MSG_HELP = (
    "📖 <b>주읽이 명령어</b>\n\n"
    "/start — 시작하기 (온보딩)\n"
    "/my — 내 설정 확인\n"
    "/edit — 성향 + 종목 수정\n"
    "/help — 명령어 안내\n\n"
    "💡 문의: @qodhrkawk"
)

MSG_EDIT_CHOOSE = (
    "✏️ <b>설정 변경</b>\n\n"
    "무엇을 변경할까요?"
)

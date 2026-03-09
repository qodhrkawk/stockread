const features = [
  {
    emoji: "🧠",
    bg: "bg-blue-500/15",
    title: "데이터가 아닌 해석",
    desc: "숫자 나열이 아니라, 지금 이 종목이 어떤 상황인지 쉬운 말로 알려드려요.",
  },
  {
    emoji: "🎯",
    bg: "bg-purple-500/15",
    title: "투자 성향 맞춤",
    desc: "안정형·중립형·공격형 — 내 성향에 맞는 톤으로 해석해 드려요.",
  },
  {
    emoji: "⏰",
    bg: "bg-green/15",
    title: "매일 아침 자동 배달",
    desc: "매일 아침 7시, 텔레그램으로 자동 전송. 출근길에 1분이면 충분해요.",
  },
];

export default function Features() {
  return (
    <section className="px-6 py-10">
      <p className="text-xs font-semibold text-green uppercase tracking-wide mb-[6px]">
        WHY 주읽이
      </p>
      <h2 className="text-[22px] font-bold tracking-tight mb-6">
        이런 게 다릅니다
      </h2>

      <div className="flex flex-col gap-3">
        {features.map((f, i) => (
          <div
            key={i}
            className="bg-bg-card border border-border rounded-2xl p-6"
          >
            <div className="flex items-start gap-4">
              <div
                className={`w-11 h-11 min-w-[44px] rounded-xl ${f.bg} flex items-center justify-center text-xl`}
              >
                {f.emoji}
              </div>
              <div>
                <h3 className="text-base font-bold mb-[6px]">{f.title}</h3>
                <p className="text-sm text-text-secondary leading-[22px]">
                  {f.desc}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

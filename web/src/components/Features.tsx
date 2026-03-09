const features = [
  {
    emoji: "🧠",
    bg: "bg-blue-500/15",
    title: "데이터가 아닌 해석",
    desc: "숫자만 나열하지 않아요. AI가 데이터를 읽고, 지금 무슨 상황인지 쉬운 말로 설명해 드려요.",
  },
  {
    emoji: "🎯",
    bg: "bg-purple-500/15",
    title: "투자 성향 맞춤",
    desc: "안정형, 중립형, 공격형 — 내 성향에 맞는 해석을 받아보세요. 같은 종목도 해석이 달라요.",
  },
  {
    emoji: "⏰",
    bg: "bg-green/15",
    title: "매일 아침 자동 배달",
    desc: "매일 아침 7시, 텔레그램으로 리포트가 와요. 따로 검색할 필요 없어요.",
  },
];

export default function Features() {
  return (
    <section className="px-6 py-10">
      <h2 className="text-xl font-bold mb-2">왜 주읽이인가요?</h2>
      <p className="text-sm text-text-secondary mb-6">
        주린이를 위해 만들었어요
      </p>

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
                <h3 className="text-[15px] font-bold mb-1">{f.title}</h3>
                <p className="text-[13px] text-text-secondary leading-[20px]">
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

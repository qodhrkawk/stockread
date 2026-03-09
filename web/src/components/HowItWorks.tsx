const steps = [
  {
    num: 1,
    title: "텔레그램 봇 시작",
    desc: "가입 없이 텔레그램에서 /start",
  },
  {
    num: 2,
    title: "성향 & 종목 선택",
    desc: "투자 성향 + 관심 종목 3개 선택",
  },
  {
    num: 3,
    title: "매일 아침 리포트 수신",
    desc: "매일 7시, AI 해석 리포트 도착!",
  },
];

export default function HowItWorks() {
  return (
    <section className="px-6 py-10">
      <h2 className="text-xl font-bold mb-2">어떻게 시작하나요?</h2>
      <p className="text-sm text-text-secondary mb-6">3단계면 끝이에요</p>

      <div className="flex flex-col">
        {steps.map((step, i) => (
          <div key={i} className="flex gap-4 mb-6">
            {/* 넘버 + 연결선 */}
            <div className="flex flex-col items-center">
              <div className="w-8 h-8 rounded-full bg-green text-bg flex items-center justify-center text-sm font-bold">
                {step.num}
              </div>
              {i < steps.length - 1 && (
                <div
                  className="w-[2px] flex-1 mt-2"
                  style={{
                    background:
                      "linear-gradient(to bottom, #22c55e, transparent)",
                  }}
                />
              )}
            </div>

            {/* 텍스트 */}
            <div className="pb-2">
              <h3 className="text-[15px] font-bold mb-1">{step.title}</h3>
              <p className="text-[13px] text-text-secondary">{step.desc}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

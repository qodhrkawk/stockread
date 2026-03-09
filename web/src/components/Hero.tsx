const BOT_URL = "https://t.me/StockRead_bot";

export default function Hero() {
  return (
    <section className="px-6 pt-12 pb-10">
      {/* 라이브 뱃지 */}
      <div className="inline-flex items-center gap-[6px] bg-green/10 border border-green/20 rounded-full px-3 py-[5px] mb-5">
        <div className="w-[6px] h-[6px] rounded-full bg-green animate-pulse" />
        <span className="text-xs text-green font-medium">
          매일 아침 7시 리포트 발송 중
        </span>
      </div>

      {/* 헤드라인 */}
      <h1 className="text-[32px] font-extrabold leading-[1.25] mb-3">
        주식 뉴스,
        <br />
        <span className="text-green" style={{ textShadow: "0 0 20px rgba(34,197,94,0.3)" }}>
          읽어드립니다
        </span>
      </h1>

      {/* 서브카피 */}
      <p className="text-[15px] text-text-secondary leading-relaxed mb-8">
        AI가 매일 아침 당신의 종목을
        <br />
        초보 눈높이로 해석해 드려요.
      </p>

      {/* CTA */}
      <a
        href={BOT_URL}
        target="_blank"
        rel="noopener noreferrer"
        className="flex items-center justify-center gap-2 w-full h-[52px] bg-green text-bg text-base font-bold rounded-xl hover:brightness-110 transition"
      >
        <span>텔레그램에서 무료로 시작</span>
        <span className="text-lg">→</span>
      </a>

      {/* 하단 텍스트 */}
      <p className="text-center text-xs text-text-muted mt-3">
        가입 없이 바로 시작 · 완전 무료
      </p>
    </section>
  );
}

const BOT_URL = "https://t.me/StockRead_bot";

export default function BottomCTA() {
  return (
    <section className="px-6 py-10 text-center">
      <h2 className="text-xl font-bold mb-2">
        내일 아침,
        <br />
        <span className="text-green" style={{ textShadow: "0 0 20px rgba(34,197,94,0.3)" }}>
          첫 리포트를 받아보세요
        </span>
      </h2>
      <p className="text-sm text-text-secondary mb-7">
        가입 없이 텔레그램에서 바로 시작
      </p>
      <a
        href={BOT_URL}
        target="_blank"
        rel="noopener noreferrer"
        className="flex items-center justify-center gap-2 w-full h-[52px] bg-green text-bg text-base font-bold rounded-xl hover:brightness-110 transition"
      >
        <span>무료로 시작하기</span>
        <span className="text-lg">→</span>
      </a>
    </section>
  );
}

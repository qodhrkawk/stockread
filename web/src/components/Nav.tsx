import Link from "next/link";

const BOT_URL = "https://t.me/StockRead_bot";

export default function Nav() {
  return (
    <nav className="px-6 flex items-center justify-between h-12">
      <div className="flex items-center gap-2">
        <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-green to-green-dark flex items-center justify-center text-sm">
          📊
        </div>
        <span className="text-[15px] font-bold">주읽이</span>
      </div>
      <Link
        href={BOT_URL}
        target="_blank"
        className="bg-green text-bg text-[13px] font-semibold px-4 py-[6px] rounded-lg hover:brightness-110 transition"
      >
        시작하기
      </Link>
    </nav>
  );
}

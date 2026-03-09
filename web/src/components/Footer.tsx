export default function Footer() {
  return (
    <footer className="px-6 py-6 border-t border-border-inner">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-[6px]">
          <span className="text-xs">📊</span>
          <span className="text-xs font-semibold text-text-muted">주읽이</span>
        </div>
        <span className="text-[11px] text-text-dim">© 2026 StockRead</span>
      </div>
      <p className="text-[11px] text-text-dim mt-3 leading-[18px]">
        ⚠️ 이 서비스는 참고용이에요. 투자 판단은 본인이 직접 해주세요!
      </p>
    </footer>
  );
}

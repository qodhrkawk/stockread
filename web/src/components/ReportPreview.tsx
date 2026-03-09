"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import {
  tabLabels,
  riskMeta,
  tabKeys,
  riskKeys,
  type TabKey,
  type RiskKey,
  type LandingData,
} from "@/lib/report-data";

function useDragScroll() {
  const ref = useRef<HTMLDivElement>(null);
  const isDragging = useRef(false);
  const startX = useRef(0);
  const scrollLeft = useRef(0);
  const onMouseDown = useCallback((e: React.MouseEvent) => {
    isDragging.current = true;
    startX.current = e.pageX - (ref.current?.offsetLeft || 0);
    scrollLeft.current = ref.current?.scrollLeft || 0;
    if (ref.current) ref.current.style.cursor = "grabbing";
  }, []);
  const onMouseMove = useCallback((e: React.MouseEvent) => {
    if (!isDragging.current || !ref.current) return;
    e.preventDefault();
    const x = e.pageX - ref.current.offsetLeft;
    ref.current.scrollLeft = scrollLeft.current - (x - startX.current) * 1.5;
  }, []);
  const onMouseUp = useCallback(() => {
    isDragging.current = false;
    if (ref.current) ref.current.style.cursor = "grab";
  }, []);
  return { ref, onMouseDown, onMouseMove, onMouseUp, onMouseLeave: onMouseUp };
}

const sectionMeta = [
  { key: "section1", emoji: "📍", title: "지금 어디쯤이에요?" },
  { key: "section2", emoji: "📐", title: "차트가 말해주는 것" },
  { key: "section3", emoji: "📰", title: "무슨 일이 있었나요?" },
];

export default function ReportPreview() {
  const [tab, setTab] = useState<TabKey>("nvda");
  const [risk, setRisk] = useState<RiskKey>("mid");
  const [data, setData] = useState<LandingData | null>(null);
  const drag = useDragScroll();

  useEffect(() => {
    fetch("/landing-data.json")
      .then((r) => r.json())
      .then(setData)
      .catch(() => {});
  }, []);

  // 로딩 or 데이터 없음
  if (!data || !data.stocks[tab]) {
    return (
      <section className="px-6 py-10">
        <p className="text-xs font-semibold text-green uppercase tracking-wide mb-[6px]">LIVE PREVIEW</p>
        <h2 className="text-[22px] font-bold tracking-tight mb-4">오늘의 리포트 미리보기</h2>
        <div className="bg-bg-card border border-border rounded-2xl p-8 text-center text-text-secondary text-sm">
          리포트를 준비 중이에요 ☕
        </div>
      </section>
    );
  }

  const stock = data.stocks[tab];
  const rm = riskMeta[risk];
  const sec = stock.sections[risk];

  return (
    <section className="px-6 py-10">
      <div className="mb-5">
        <p className="text-xs font-semibold text-green uppercase tracking-wide mb-[6px]">LIVE PREVIEW</p>
        <h2 className="text-[22px] font-bold tracking-tight">오늘의 리포트 미리보기</h2>
        <p className="text-xs text-text-muted mt-1">{data.date} 기준</p>
      </div>

      {/* 종목 탭 */}
      <div ref={drag.ref} onMouseDown={drag.onMouseDown} onMouseMove={drag.onMouseMove} onMouseUp={drag.onMouseUp} onMouseLeave={drag.onMouseLeave}
        className="flex gap-[6px] overflow-x-auto pb-3 scrollbar-hide select-none" style={{ cursor: "grab" }}>
        {tabKeys.map((key) => (
          <button key={key} onClick={() => setTab(key)}
            className={`shrink-0 px-[14px] py-[7px] rounded-full text-[13px] font-medium border transition-all ${
              key === tab ? "bg-text text-bg font-semibold border-text" : "border-border text-text-secondary hover:bg-border hover:text-text"
            }`}>
            {tabLabels[key]}
          </button>
        ))}
      </div>

      {/* 성향 */}
      <div className="flex gap-2 pb-4">
        {riskKeys.map((key) => {
          const m = riskMeta[key];
          return (
            <button key={key} onClick={() => setRisk(key)}
              className={`shrink-0 px-3 py-[6px] rounded-lg text-xs font-medium border transition-all ${
                key === risk ? `${m.bg} ${m.border} ${m.color}` : "border-border text-text-secondary hover:bg-border-inner hover:border-text-dim hover:text-text"
              }`}>
              {m.label}
            </button>
          );
        })}
      </div>

      {/* 리포트 카드 */}
      <div key={`${tab}-${risk}`} className="bg-bg-card border border-border rounded-2xl overflow-hidden animate-in fade-in slide-in-from-bottom-3 duration-300">
        {/* 헤더 */}
        <div className="px-5 pt-5 pb-4 border-b border-border-inner">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-[10px]">
              <span className="text-base">{stock.flag}</span>
              <div>
                <span className="text-base font-bold">{stock.ticker}</span>
                <span className="text-[13px] text-text-dim ml-[6px]">{stock.name}</span>
              </div>
            </div>
            <div className="text-right">
              <div className="text-base font-bold">{stock.price}</div>
              <div className={`text-[13px] font-semibold ${stock.positive ? "text-green" : "text-red"}`}>
                {stock.positive ? "▲" : "▼"} {stock.change}
              </div>
              <div className="text-[10px] text-text-muted mt-[2px]">
                {data.date.slice(5).replace("-", "/")} 종가
              </div>
            </div>
          </div>
          <div className="flex gap-2">
            <span className="bg-border-inner rounded-md px-[10px] py-1 text-[11px] text-text-secondary">
              52주 고점 대비 <span className="text-text font-semibold">{stock.high52}</span>
            </span>
            <span className="bg-border-inner rounded-md px-[10px] py-1 text-[11px] text-text-secondary">
              {rm.emoji} {rm.name}
            </span>
          </div>
        </div>

        {/* 본문 */}
        <div className="px-5 py-5">
          {sectionMeta.map(({ key, emoji, title }) => {
            const text = sec[key as keyof typeof sec];
            if (!text) return null;
            return (
              <div key={key} className="mb-4">
                <div className="flex items-center gap-[6px] mb-[6px]">
                  <span className="text-sm">{emoji}</span>
                  <span className="text-[13px] font-semibold text-text-secondary">{title}</span>
                </div>
                <p className="text-sm leading-[22px] text-neutral-300 pl-[22px] whitespace-pre-line">{text}</p>
              </div>
            );
          })}

          {/* 해석 */}
          {sec.interpret && (
            <div className="p-4 bg-green/5 rounded-xl border border-green/10">
              <div className="flex items-center gap-[6px] mb-[6px]">
                <span className="text-sm">💡</span>
                <span className="text-[13px] font-semibold text-green">이렇게 보시면 돼요 ({rm.emoji} {rm.name})</span>
              </div>
              <p className="text-sm leading-[22px] text-neutral-300 pl-[22px] whitespace-pre-line">{sec.interpret}</p>
            </div>
          )}
        </div>

        {/* 면책 */}
        <div className="px-5 py-3 bg-bg-footer border-t border-border-inner">
          <p className="text-[11px] text-text-muted">⚠️ 이 리포트는 참고용이에요. 투자 판단은 본인이 직접 해주세요!</p>
        </div>
      </div>
    </section>
  );
}

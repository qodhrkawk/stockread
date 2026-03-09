"use client";

import { useState } from "react";
import {
  reports,
  tabLabels,
  riskMeta,
  tabKeys,
  riskKeys,
  type TabKey,
  type RiskKey,
} from "@/lib/report-data";

export default function ReportPreview() {
  const [tab, setTab] = useState<TabKey>("nvda");
  const [risk, setRisk] = useState<RiskKey>("mid");

  const r = reports[tab];
  const rm = riskMeta[risk];

  return (
    <section className="px-6 py-10">
      {/* 섹션 제목 */}
      <div className="mb-5">
        <h2 className="text-xl font-bold mb-1">이런 리포트를 받아요</h2>
        <p className="text-sm text-text-secondary">
          종목과 성향을 바꿔보세요
        </p>
      </div>

      {/* 종목 탭 */}
      <div className="flex gap-[6px] overflow-x-auto pb-3 scrollbar-hide">
        {tabKeys.map((key) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={`shrink-0 px-[14px] py-[7px] rounded-full text-[13px] font-medium transition-all ${
              key === tab
                ? "bg-text text-bg font-semibold"
                : "text-text-secondary hover:bg-border hover:text-text"
            }`}
          >
            {tabLabels[key]}
          </button>
        ))}
      </div>

      {/* 성향 버튼 */}
      <div className="flex gap-2 pb-4">
        {riskKeys.map((key) => {
          const meta = riskMeta[key];
          const active = key === risk;
          return (
            <button
              key={key}
              onClick={() => setRisk(key)}
              className={`shrink-0 px-3 py-[6px] rounded-lg text-xs font-medium border transition-all ${
                active
                  ? `${meta.bg} ${meta.border} ${meta.color}`
                  : "border-border text-text-secondary hover:bg-border-inner hover:border-text-dim hover:text-text"
              }`}
            >
              {meta.label}
            </button>
          );
        })}
      </div>

      {/* 리포트 카드 */}
      <div
        key={`${tab}-${risk}`}
        className="bg-bg-card border border-border rounded-2xl overflow-hidden animate-in fade-in slide-in-from-bottom-3 duration-300"
      >
        {/* 헤더 */}
        <div className="px-5 pt-5 pb-4 border-b border-border-inner">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-[10px]">
              <span className="text-base">{r.flag}</span>
              <div>
                <span className="text-base font-bold">{r.ticker}</span>
                <span className="text-[13px] text-text-dim ml-[6px]">
                  {r.name}
                </span>
              </div>
            </div>
            <div className="text-right">
              <div className="text-base font-bold">{r.price}</div>
              <div
                className={`text-[13px] font-semibold ${
                  r.positive ? "text-green" : "text-red"
                }`}
              >
                {r.positive ? "▲" : "▼"} {r.change}
              </div>
            </div>
          </div>
          <div className="flex gap-2">
            <span className="bg-border-inner rounded-md px-[10px] py-1 text-[11px] text-text-secondary">
              52주 고점 대비{" "}
              <span className="text-text font-semibold">{r.high52}</span>
            </span>
            <span className="bg-border-inner rounded-md px-[10px] py-1 text-[11px] text-text-secondary">
              {rm.emoji} {rm.name}
            </span>
          </div>
        </div>

        {/* 본문 */}
        <div className="px-5 py-5">
          {r.base.map((section, i) => (
            <div key={i} className="mb-4">
              <div className="flex items-center gap-[6px] mb-[6px]">
                <span className="text-sm">{section.emoji}</span>
                <span className="text-[13px] font-semibold text-text-secondary">
                  {section.title}
                </span>
              </div>
              <p className="text-sm leading-[22px] text-neutral-300 pl-[22px]">
                {section.text}
              </p>
            </div>
          ))}

          {/* 해석 섹션 */}
          <div className="p-4 bg-green/5 rounded-xl border border-green/10">
            <div className="flex items-center gap-[6px] mb-[6px]">
              <span className="text-sm">💡</span>
              <span className="text-[13px] font-semibold text-green">
                이렇게 보시면 돼요 ({rm.emoji} {rm.name})
              </span>
            </div>
            <p className="text-sm leading-[22px] text-neutral-300 pl-[22px]">
              {r.interpret[risk]}
            </p>
          </div>
        </div>

        {/* 면책 */}
        <div className="px-5 py-3 bg-bg-footer border-t border-border-inner">
          <p className="text-[11px] text-text-muted">
            ⚠️ 이 리포트는 참고용이에요. 투자 판단은 본인이 직접 해주세요!
          </p>
        </div>
      </div>
    </section>
  );
}

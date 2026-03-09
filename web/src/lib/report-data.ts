export type RiskKey = "safe" | "mid" | "aggr";
export type TabKey = "nvda" | "tsla" | "samsung" | "aapl" | "hynix";

export interface SectionData {
  section1: string;
  section2: string;
  section3: string;
  interpret: string;
}

export interface StockData {
  ticker: string;
  name: string;
  flag: string;
  price: string;
  change: string;
  positive: boolean;
  high52: string;
  tradeDate: string;
  sections: Record<RiskKey, SectionData>;
}

export interface LandingData {
  date: string;
  stocks: Record<TabKey, StockData>;
}

export const tabLabels: Record<TabKey, string> = {
  nvda: "NVDA", tsla: "TSLA", samsung: "삼성전자", aapl: "AAPL", hynix: "SK하이닉스",
};

export const riskMeta: Record<RiskKey, { label: string; emoji: string; name: string; color: string; bg: string; border: string }> = {
  safe: { label: "🛡 안정형", emoji: "🛡", name: "안정형", color: "text-blue-400", bg: "bg-blue-500/15", border: "border-blue-500/40" },
  mid: { label: "⚖️ 중립형", emoji: "⚖️", name: "중립형", color: "text-purple-400", bg: "bg-purple-500/15", border: "border-purple-500/40" },
  aggr: { label: "🔥 공격형", emoji: "🔥", name: "공격형", color: "text-red-400", bg: "bg-red-500/15", border: "border-red-500/40" },
};

export const tabKeys: TabKey[] = ["nvda", "tsla", "samsung", "aapl", "hynix"];
export const riskKeys: RiskKey[] = ["safe", "mid", "aggr"];

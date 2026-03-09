export type RiskKey = "safe" | "mid" | "aggr";
export type TabKey = "nvda" | "tsla" | "samsung" | "aapl" | "hynix";

export interface ReportSection {
  emoji: string;
  title: string;
  text: string;
}

export interface ReportData {
  ticker: string;
  name: string;
  flag: string;
  price: string;
  change: string;
  positive: boolean;
  high52: string;
  base: ReportSection[];
  interpret: Record<RiskKey, string>;
}

export const reports: Record<TabKey, ReportData> = {
  nvda: {
    ticker: "NVDA", name: "엔비디아", flag: "🇺🇸",
    price: "$875.40", change: "+2.3%", positive: true, high52: "91%",
    base: [
      { emoji: "📍", title: "지금 어디쯤이에요?", text: "어제 $875.40에 마감했어요 (+2.3%). 1년 중 가장 높았던 가격의 91% 위치에 있어요. 거의 최고점 근처예요!" },
      { emoji: "📐", title: "차트가 말해주는 것", text: "RSI가 72예요. 보통 70 넘으면 과열 신호로 봐요. 20일 이평선 위에 있어서 단기적으로는 오르는 흐름이에요. 거래량도 평소보다 15% 많았어요." },
      { emoji: "📰", title: "무슨 일이 있었나요?", text: "AI 서버 수요가 급증하고 있다는 뉴스가 나왔어요 (호재 📈). GTC 컨퍼런스 기대감도 커지고 있고요. 실적 발표가 2주 뒤에 있어요." },
    ],
    interpret: {
      safe: "최근 많이 올랐기 때문에 지금 새로 사는 건 조심할 필요가 있어요. 이미 갖고 계시다면 일부 이익 실현을 고려해 보세요. 실적 발표 전까지는 지켜보는 게 안전해요.",
      mid: "최근 많이 올랐기 때문에 조정이 올 수도 있어요. 한 번에 사기보다 나눠서 접근하는 게 좋아 보여요. 실적 발표 전에는 가격이 흔들릴 수 있으니 참고하세요!",
      aggr: "AI 관련 흐름이 여전히 강해요! RSI가 좀 높긴 하지만 추세 자체는 아직 살아있어요. GTC + 실적 이벤트 앞두고 단기 트레이딩 기회가 있어 보여요.",
    },
  },
  tsla: {
    ticker: "TSLA", name: "테슬라", flag: "🇺🇸",
    price: "$248.50", change: "-1.2%", positive: false, high52: "68%",
    base: [
      { emoji: "📍", title: "지금 어디쯤이에요?", text: "어제 $248.50에 마감했어요 (-1.2%). 1년 최고가의 68% 위치라, 고점에서 꽤 많이 내려와 있어요." },
      { emoji: "📐", title: "차트가 말해주는 것", text: "RSI가 45예요. 딱 중간 정도 구간이에요. 20일 이평선 아래로 내려왔고, 거래량도 줄어드는 추세예요." },
      { emoji: "📰", title: "무슨 일이 있었나요?", text: "자율주행 FSD 업데이트 기대감이 있어요. 다만 중국 판매량은 저번 달보다 조금 줄었어요." },
    ],
    interpret: {
      safe: "아직 내려가는 흐름이 이어지고 있어요. 확실히 반등하는 게 보이기 전까지는 지켜보는 게 좋을 것 같아요.",
      mid: "기술적으로 반등을 시도하는 구간이에요. 하지만 추세가 바뀌었는지 확인이 필요해요. 단기보다는 중장기 관점으로 접근하는 게 좋아 보여요.",
      aggr: "고점 대비 32%나 내려온 구간이에요. 반등하면 수익폭이 클 수 있어요! 다만 변동성이 크니까 소량씩 나눠서 접근해 보세요.",
    },
  },
  samsung: {
    ticker: "005930", name: "삼성전자", flag: "🇰🇷",
    price: "72,400원", change: "-0.5%", positive: false, high52: "78%",
    base: [
      { emoji: "📍", title: "지금 어디쯤이에요?", text: "어제 72,400원에 마감했어요 (-0.5%). 1년 최고가의 78% 위치예요. 7만원대에서 오르내리는 중이에요." },
      { emoji: "📐", title: "차트가 말해주는 것", text: "RSI가 48이에요. 딱 중간이에요. 60일 이평선 근처에서 왔다 갔다 하고 있고, 외국인이 3일 연속 팔고 있어요." },
      { emoji: "📰", title: "무슨 일이 있었나요?", text: "HBM3E 양산이 본격적으로 시작된다는 소식이에요. 파운드리 수율도 좋아지고 있다고 해요. 반도체 업황 바닥 논쟁은 계속되고 있어요." },
    ],
    interpret: {
      safe: "외국인이 계속 팔고 있어서 부담이에요. 배당 매력은 있지만, 단기 반등 근거가 부족해요. 추가 하락에 대비하는 게 좋겠어요.",
      mid: "외국인 매도세가 부담이지만, HBM 관련 기대감은 긍정적이에요. 7만원 초반이면 나눠서 사 볼 만한 구간이에요.",
      aggr: "HBM 테마 + 저평가 구간이에요! 박스권 하단에서 적극적으로 나눠 사는 전략이 유효해 보여요. 반도체 턴어라운드에 베팅해볼 만해요!",
    },
  },
  aapl: {
    ticker: "AAPL", name: "애플", flag: "🇺🇸",
    price: "$178.20", change: "+0.8%", positive: true, high52: "85%",
    base: [
      { emoji: "📍", title: "지금 어디쯤이에요?", text: "어제 $178.20에 마감했어요 (+0.8%). 1년 최고가의 85% 위치에서 안정적으로 흐르고 있어요." },
      { emoji: "📐", title: "차트가 말해주는 것", text: "RSI가 55예요. 부담 없는 구간이에요. 20일, 60일 이평선 모두 위에 있어서 흐름이 좋아요." },
      { emoji: "📰", title: "무슨 일이 있었나요?", text: "WWDC에서 AI 기능을 발표할 거라는 기대가 커요. 서비스 매출은 역대 최고를 기록했어요!" },
    ],
    interpret: {
      safe: "안정적인 우량주예요. 급등보다는 꾸준한 흐름이에요. 배당 + 자사주 매입을 고려하면 장기 보유에 적합해요.",
      mid: "안정적인 우량주 역할을 잘 하고 있어요. AI 전략이 구체화되면 추가 상승 여력도 있어요. 꾸준한 흐름을 기대해 봐도 좋아요.",
      aggr: "AI 전략 발표가 기폭제가 될 수 있어요! WWDC 이벤트 전에 미리 포지션을 잡아볼 수 있어요. 서비스 매출 성장세도 주목해 보세요!",
    },
  },
  hynix: {
    ticker: "000660", name: "SK하이닉스", flag: "🇰🇷",
    price: "185,500원", change: "+1.8%", positive: true, high52: "88%",
    base: [
      { emoji: "📍", title: "지금 어디쯤이에요?", text: "어제 185,500원에 마감했어요 (+1.8%). 1년 최고가의 88% 위치예요. AI 반도체 수혜주로 강하게 가고 있어요!" },
      { emoji: "📐", title: "차트가 말해주는 것", text: "RSI가 65예요. 강세 구간이에요. 모든 이평선 위에 있고, 외국인도 2일째 사고 있어요." },
      { emoji: "📰", title: "무슨 일이 있었나요?", text: "HBM 글로벌 1위 자리가 더 확고해졌어요. 엔비디아에 납품하는 HBM3E 물량도 늘어나고 있어요." },
    ],
    interpret: {
      safe: "AI 수혜 흐름은 인정하지만, RSI가 강세 구간이라 지금 쫓아서 사기엔 부담이에요. 조정이 올 때 나눠서 접근하는 게 좋겠어요.",
      mid: "AI 수혜 흐름이 아주 강해요! 다만 단기 과열 가능성도 있으니 나눠서 접근하는 게 좋아 보여요. 실적 시즌에 변동성이 커질 수 있어요.",
      aggr: "HBM 글로벌 1위 + AI 슈퍼사이클 수혜주! 추세가 꺾이기 전까지는 적극 보유하는 전략이 유효해요. 실적 서프라이즈도 기대돼요!",
    },
  },
};

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

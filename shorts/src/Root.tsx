import { Composition } from "remotion";
import { ShortVideo } from "./ShortVideo";
import { ShortVideoSchema, type ShortScript } from "./types";

const DEFAULT_SCRIPT: ShortScript = {
  date: "2026-03-10",
  title: "한국증시 대폭락",
  tts_script: "test",
  scenes: [
    {
      label: "hook",
      tts_text: "삼성전자가 9.5% 폭락했어요.",
      headline: "삼성전자 17만원대 추락",
      number: "-9.5%",
      duration: 5,
    },
    {
      label: "summary",
      tts_text: "반도체 급락, 방산 급등.",
      sectors: [
        { name: "반도체", direction: "down" },
        { name: "방산", direction: "up" },
      ],
      duration: 10,
    },
    {
      label: "detail",
      tts_text: "삼성전자 170,200원.",
      cards: [
        { name: "삼성전자", price: "170,200원", change: "-9.56%", indicators: ["RSI 46.8"] },
        { name: "SK하이닉스", price: "827,000원", change: "-10.5%", indicators: ["RSI 44.8"] },
      ],
      duration: 25,
    },
    {
      label: "context",
      tts_text: "이란 사태 때문이에요.",
      flow: ["이란 사태", "헬륨 공급 차질", "반도체 제조 리스크"],
      duration: 15,
    },
    {
      label: "closing",
      tts_text: "지켜보는 게 좋겠어요.",
      message: "당분간 변동성 주의\n관망하며 지켜보세요",
      duration: 5,
    },
  ],
  audioDurationSec: 60,
};

export const RemotionRoot: React.FC = () => {
  const fps = 30;
  return (
    <Composition
      id="ShortVideo"
      component={ShortVideo}
      durationInFrames={60 * fps}
      fps={fps}
      width={1080}
      height={1920}
      schema={ShortVideoSchema}
      defaultProps={DEFAULT_SCRIPT}
      calculateMetadata={async ({ props }) => {
        const totalSec = props.scenes.reduce((sum, s) => sum + s.duration, 0);
        const clamped = Math.max(30, Math.min(70, totalSec));
        return { durationInFrames: clamped * fps };
      }}
    />
  );
};

import { Composition } from "remotion";
import { ShortVideo } from "./ShortVideo";
import { ShortVideoSchema, type ShortScript } from "./types";

const DEFAULT_SCRIPT: ShortScript = {
  date: "2026-03-10",
  title: "서킷브레이커 발동",
  tts_script: "test",
  scenes: [
    {
      label: "hook",
      tts_text: "서킷브레이커가 발동됐어요.",
      event: "서킷브레이커 발동",
      number: "-8.5%",
      duration: 5,
    },
    {
      label: "summary",
      tts_text: "반도체 급락.",
      visual_segments: [
        { start_sentence: 0, sector: { name: "반도체", direction: "down", change: "-10%" } },
      ],
      duration: 10,
    },
    {
      label: "detail",
      tts_text: "삼성전자 170,200원.",
      visual_segments: [
        { start_sentence: 0, card: { name: "삼성전자", price: "170,200원", change: "-9.56%", reason: "헬륨 공급 차질", indicators: ["RSI 46.8"] } },
      ],
      duration: 25,
    },
    {
      label: "context",
      tts_text: "이란 사태 때문이에요.",
      flow: ["이란 사태", "헬륨 공급 차질", "반도체 타격"],
      duration: 15,
    },
    {
      label: "closing",
      tts_text: "지켜보는 게 좋겠어요.",
      message: "지켜보는 게 좋겠어요.",
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

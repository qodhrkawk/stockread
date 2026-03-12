import { Composition } from "remotion";
import { ShortVideo } from "./ShortVideo";
import { ShortVideoSchema, type ShortScript } from "./types";
import { TriviaVideo, TriviaScriptSchema, type TriviaScript } from "./trivia";

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

const DEFAULT_TRIVIA: TriviaScript = {
  date: "2026-03-12",
  title: "물의 진짜 색깔은?",
  tts_script: "test",
  scenes: [
    {
      label: "hook",
      tts_text: "물은 정말 무색무취일까요?",
      question: "물은 정말 무색무취일까요?",
      fact: "순수한 물은 사실 파란색이에요!",
      duration: 8,
    },
    {
      label: "explain",
      tts_text: "우리가 매일 마시는 물은 투명해 보여요.",
      steps: [
        { icon: "💧", text: "물은 투명해 보여요" },
        { icon: "🔬", text: "분자가 빛을 흡수해요" },
        { icon: "🌊", text: "많이 모이면 파란색이에요" },
      ],
      duration: 18,
    },
    {
      label: "twist",
      tts_text: "그런데 사실 순수한 물은 파란색이에요.",
      highlight: "순수한 H2O는 파란색!",
      detail: "빨간 빛을 아주 조금 흡수하기 때문이에요",
      duration: 12,
    },
    {
      label: "closing",
      tts_text: "알고 보면 신기하죠.",
      message: "물의 진짜 색깔\n아주 옅은 파란색",
      duration: 7,
    },
  ],
  audioDurationSec: 45,
};

export const RemotionRoot: React.FC = () => {
  const fps = 30;
  return (
    <>
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
      <Composition
        id="TriviaVideo"
        component={TriviaVideo}
        durationInFrames={45 * fps}
        fps={fps}
        width={1080}
        height={1920}
        schema={TriviaScriptSchema}
        defaultProps={DEFAULT_TRIVIA}
        calculateMetadata={async ({ props }) => {
          const totalSec = props.scenes.reduce((sum, s) => sum + s.duration, 0);
          const clamped = Math.max(30, Math.min(60, totalSec));
          return { durationInFrames: clamped * fps };
        }}
      />
    </>
  );
};

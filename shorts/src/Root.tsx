import { Composition } from "remotion";
import { ShortVideo } from "./ShortVideo";
import { ShortVideoSchema, type ShortScript } from "./types";

const DEFAULT_SCRIPT: ShortScript = {
  date: "2026-03-10",
  title: "삼성전자 8% 폭락!",
  tts_script: "삼성전자가 하루 만에 8% 폭락했어요...",
  scenes: [
    { label: "hook", text: "삼성전자 8% 폭락!\n무슨 일이 있었던 걸까요?", duration: 5 },
    { label: "summary", text: "반도체 급락 📉\n방산주 급등 📈", duration: 10 },
    { label: "detail", text: "삼성전자 -8% · 170,200원\nSK하이닉스 -8% · 827,000원\n한화에어로 +12%", duration: 20 },
    { label: "context", text: "이란 분쟁 → 헬륨 공급 차질\n→ 반도체 제조 리스크", duration: 15 },
    { label: "closing", text: "분산 투자로\n지켜보는 게 좋아 보여요", duration: 10 },
  ],
  audioDurationSec: 60,
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
          // scenes duration 합계로 영상 길이 결정
          const totalSec = props.scenes.reduce((sum, s) => sum + s.duration, 0);
          const clamped = Math.max(30, Math.min(70, totalSec));
          return { durationInFrames: clamped * fps };
        }}
      />
    </>
  );
};

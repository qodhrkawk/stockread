import { Composition } from "remotion";
import { ShortVideo } from "./ShortVideo";
import { ShortVideoSchema, type ShortScript } from "./types";

const DEFAULT_SCRIPT: ShortScript = {
  date: "2026-03-10",
  title: "3월 10일 미국·한국 증시 핵심 요약",
  market_summary: "미국 반도체 강세, 한국 2차전지 약세",
  highlights: [
    "엔비디아 AI 수요 호재로 +2.3%",
    "테슬라 기술적 반등 시도",
    "삼성전자 외국인 순매도 지속",
  ],
  interpretation: "단기 과열 구간 접근, 신규 진입은 신중하게 판단하세요",
  tts_script:
    "오늘 미국 증시는 반도체 강세로 상승 마감했어요.",
  audioDurationSec: 30,
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
          const sec = props.audioDurationSec ?? 30;
          const clamped = Math.max(30, Math.min(60, sec));
          return {
            durationInFrames: clamped * fps,
          };
        }}
      />
    </>
  );
};

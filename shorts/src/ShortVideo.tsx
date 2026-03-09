import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Sequence,
  Audio,
  staticFile,
} from "remotion";
import { theme, fonts } from "./styles/theme";
import { HookTitle } from "./components/HookTitle";
import { MarketSummary } from "./components/MarketSummary";
import { Highlights } from "./components/Highlights";
import { Interpretation } from "./components/Interpretation";
import { Watermark } from "./components/Watermark";
import type { ShortScript } from "./types";

export const ShortVideo: React.FC<ShortScript> = (props) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // 섹션별 타이밍 (프레임 단위, 30fps 기준)
  const hookStart = 0;
  const hookDuration = Math.round(3 * fps); // 0~3초

  const summaryStart = hookDuration;
  const summaryDuration = Math.round(7 * fps); // 3~10초

  const highlightsStart = summaryStart + summaryDuration;
  const highlightsDuration = Math.round(10 * fps); // 10~20초

  const interpStart = highlightsStart + highlightsDuration;
  const interpDuration = durationInFrames - interpStart; // 나머지

  // 배경 그라데이션 애니메이션
  const bgShift = interpolate(frame, [0, durationInFrames], [0, 30]);

  return (
    <AbsoluteFill
      style={{
        background: theme.bgGradient,
        fontFamily: fonts.body,
        overflow: "hidden",
      }}
    >
      {/* 배경 글로우 오브 */}
      <div
        style={{
          position: "absolute",
          top: `${20 + Math.sin(frame / 60) * 5}%`,
          left: `${-10 + Math.sin(frame / 80) * 5}%`,
          width: 600,
          height: 600,
          borderRadius: "50%",
          background:
            "radial-gradient(circle, rgba(0,255,136,0.08) 0%, transparent 70%)",
          filter: "blur(80px)",
        }}
      />
      <div
        style={{
          position: "absolute",
          bottom: `${10 + Math.cos(frame / 70) * 5}%`,
          right: `${-10 + Math.cos(frame / 90) * 5}%`,
          width: 500,
          height: 500,
          borderRadius: "50%",
          background:
            "radial-gradient(circle, rgba(0,212,255,0.06) 0%, transparent 70%)",
          filter: "blur(80px)",
        }}
      />

      {/* 섹션들 */}
      <Sequence from={hookStart} durationInFrames={hookDuration + 15}>
        <HookTitle title={props.title} date={props.date} />
      </Sequence>

      <Sequence from={summaryStart} durationInFrames={summaryDuration + 15}>
        <MarketSummary summary={props.market_summary} />
      </Sequence>

      <Sequence from={highlightsStart} durationInFrames={highlightsDuration + 15}>
        <Highlights highlights={props.highlights} />
      </Sequence>

      <Sequence from={interpStart} durationInFrames={interpDuration}>
        <Interpretation text={props.interpretation} />
      </Sequence>

      {/* 워터마크 — 항상 표시 */}
      <Watermark />

      {/* TTS 오디오 (파일이 있을 때만) */}
      {/* <Audio src={staticFile("tts.mp3")} /> */}
    </AbsoluteFill>
  );
};

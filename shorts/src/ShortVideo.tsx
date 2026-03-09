import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  Sequence,
} from "remotion";
import { theme, fonts } from "./styles/theme";
import { SceneRenderer } from "./components/SceneRenderer";
import { Watermark } from "./components/Watermark";
import type { ShortScript } from "./types";

export const ShortVideo: React.FC<ShortScript> = (props) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // 씬별 시작 프레임 계산
  let currentFrame = 0;
  const sceneTimings = props.scenes.map((scene) => {
    const start = currentFrame;
    const duration = scene.duration * fps;
    currentFrame += duration;
    return { start, duration };
  });

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

      {/* 씬 시퀀스 */}
      {props.scenes.map((scene, i) => {
        const { start, duration } = sceneTimings[i];
        const isLast = i === props.scenes.length - 1;
        // 다음 씬과 겹치기 위해 duration에 여유 추가
        const overlap = isLast ? 0 : 15;

        return (
          <Sequence
            key={i}
            from={start}
            durationInFrames={duration + overlap}
          >
            <SceneRenderer scene={scene} isLast={isLast} />
          </Sequence>
        );
      })}

      {/* 워터마크 — 항상 표시 */}
      <Watermark />
    </AbsoluteFill>
  );
};

import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  Sequence,
  Audio,
  staticFile,
} from "remotion";
import { theme, fonts } from "./styles/theme";
import { HookScene } from "./components/HookScene";
import { SummaryScene } from "./components/SummaryScene";
import { DetailScene } from "./components/DetailScene";
import { ContextScene } from "./components/ContextScene";
import { ClosingScene } from "./components/ClosingScene";
import { Subtitle } from "./components/Subtitle";
import { Watermark } from "./components/Watermark";
import type { ShortScript, Scene } from "./types";

const SceneComponent: React.FC<{ scene: Scene }> = ({ scene }) => {
  switch (scene.label) {
    case "hook": return <HookScene scene={scene} />;
    case "summary": return <SummaryScene scene={scene} />;
    case "detail": return <DetailScene scene={scene} />;
    case "context": return <ContextScene scene={scene} />;
    case "closing": return <ClosingScene scene={scene} />;
    default: return null;
  }
};

export const ShortVideo: React.FC<ShortScript> = (props) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  let currentFrame = 0;
  const sceneTimings = props.scenes.map((scene) => {
    const start = currentFrame;
    const duration = scene.duration * fps;
    currentFrame += duration;
    return { start, duration };
  });

  return (
    <AbsoluteFill style={{ background: theme.bgGradient, fontFamily: fonts.body, overflow: "hidden" }}>
      {/* TTS 오디오 */}
      <Audio src={staticFile("tts.mp3")} />

      {/* 배경 글로우 */}
      <div style={{
        position: "absolute",
        top: `${20 + Math.sin(frame / 60) * 5}%`,
        left: `${-10 + Math.sin(frame / 80) * 5}%`,
        width: 600, height: 600, borderRadius: "50%",
        background: "radial-gradient(circle, rgba(0,255,136,0.08) 0%, transparent 70%)",
        filter: "blur(80px)",
      }} />
      <div style={{
        position: "absolute",
        bottom: `${10 + Math.cos(frame / 70) * 5}%`,
        right: `${-10 + Math.cos(frame / 90) * 5}%`,
        width: 500, height: 500, borderRadius: "50%",
        background: "radial-gradient(circle, rgba(0,212,255,0.06) 0%, transparent 70%)",
        filter: "blur(80px)",
      }} />

      {/* 씬별 인포그래픽 (상단~중단) */}
      {props.scenes.map((scene, i) => {
        const { start, duration } = sceneTimings[i];
        const isLast = i === props.scenes.length - 1;
        const overlap = 0;
        return (
          <Sequence key={i} from={start} durationInFrames={duration}>
            <SceneComponent scene={scene} />
          </Sequence>
        );
      })}

      {/* 하단 자막 레이어 */}
      <Subtitle scenes={props.scenes} sceneTimings={sceneTimings} />

      {/* 워터마크 */}
      <Watermark />
    </AbsoluteFill>
  );
};

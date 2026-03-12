import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  Sequence,
  Audio,
  staticFile,
  Img,
  interpolate,
} from "remotion";
import { theme, fonts } from "../styles/theme";
import { Subtitle } from "../components/Subtitle";
import { HookScene } from "./HookScene";
import { ExplainScene } from "./ExplainScene";
import { TwistScene } from "./TwistScene";
import { ClosingScene } from "./ClosingScene";
import type { TriviaScript, TriviaScene } from "./types";

const SCENE_IMAGES: Record<string, string> = {
  hook: "trivia/hook.png",
  explain: "trivia/explain.png",
  twist: "trivia/twist.png",
  closing: "trivia/closing.png",
};

const SceneComponent: React.FC<{ scene: TriviaScene }> = ({ scene }) => {
  switch (scene.label) {
    case "hook": return <HookScene scene={scene} />;
    case "explain": return <ExplainScene scene={scene} />;
    case "twist": return <TwistScene scene={scene} />;
    case "closing": return <ClosingScene scene={scene} />;
    default: return null;
  }
};

const KenBurnsBackground: React.FC<{ label: string; durationInFrames: number }> = ({ label, durationInFrames }) => {
  const frame = useCurrentFrame();
  const scale = interpolate(frame, [0, durationInFrames], [1, 1.1], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill>
      <Img
        src={staticFile(SCENE_IMAGES[label])}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transform: `scale(${scale})`,
        }}
      />
      {/* 다크 오버레이 */}
      <div style={{
        position: "absolute",
        top: 0, left: 0, right: 0, bottom: 0,
        background: "rgba(0,0,0,0.5)",
      }} />
    </AbsoluteFill>
  );
};

const TriviaWatermark: React.FC = () => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 30], [0, 0.5], {
    extrapolateRight: "clamp",
  });

  return (
    <div style={{
      position: "absolute",
      bottom: 60,
      left: 0,
      right: 0,
      display: "flex",
      justifyContent: "center",
      opacity,
    }}>
      <div style={{
        color: theme.textMuted,
        fontSize: 26,
        fontFamily: fonts.mono,
        fontWeight: 600,
        letterSpacing: 2,
      }}>
        60초 상식
      </div>
    </div>
  );
};

export const TriviaVideo: React.FC<TriviaScript> = (props) => {
  const { fps } = useVideoConfig();

  let currentFrame = 0;
  const sceneTimings = props.scenes.map((scene) => {
    const start = currentFrame;
    const duration = scene.duration * fps;
    currentFrame += duration;
    return { start, duration };
  });

  return (
    <AbsoluteFill style={{ background: theme.bg, fontFamily: fonts.body, overflow: "hidden" }}>
      {/* TTS 오디오 */}
      <Audio src={staticFile("trivia/tts.mp3")} />

      {/* 씬별 배경 이미지 + 인포그래픽 */}
      {props.scenes.map((scene, i) => {
        const { start, duration } = sceneTimings[i];
        return (
          <Sequence key={i} from={start} durationInFrames={duration}>
            <KenBurnsBackground label={scene.label} durationInFrames={duration} />
            <SceneComponent scene={scene} />
          </Sequence>
        );
      })}

      {/* 하단 자막 레이어 */}
      <Subtitle scenes={props.scenes as any} sceneTimings={sceneTimings} />

      {/* 워터마크 */}
      <TriviaWatermark />
    </AbsoluteFill>
  );
};

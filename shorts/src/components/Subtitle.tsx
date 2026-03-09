import React from "react";
import { useCurrentFrame, useVideoConfig, interpolate, spring } from "remotion";
import { theme, fonts } from "../styles/theme";
import type { Scene } from "../types";

interface Props {
  scenes: Scene[];
  sceneTimings: { start: number; duration: number }[];
}

export const Subtitle: React.FC<Props> = ({ scenes, sceneTimings }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // 현재 프레임이 어느 씬에 속하는지 찾기
  let currentScene: Scene | null = null;
  for (let i = 0; i < scenes.length; i++) {
    const { start, duration } = sceneTimings[i];
    if (frame >= start && frame < start + duration) {
      currentScene = scenes[i];
      break;
    }
  }

  if (!currentScene) return null;

  const ttsText = currentScene.tts_text || "";
  if (!ttsText) return null;

  // 문장 단위로 분리
  const sentences = ttsText.split(/(?<=[.?!요죠])\s*/g).filter(s => s.trim());
  if (sentences.length === 0) return null;

  // 씬 시작 기준 현재 프레임
  const sceneIdx = scenes.indexOf(currentScene);
  const sceneStart = sceneTimings[sceneIdx].start;
  const sceneDuration = sceneTimings[sceneIdx].duration;
  const localFrame = frame - sceneStart;

  // 문장별 표시 타이밍 (균등 분배)
  const framesPerSentence = Math.floor(sceneDuration / sentences.length);
  const currentSentenceIdx = Math.min(
    Math.floor(localFrame / framesPerSentence),
    sentences.length - 1
  );
  const currentSentence = sentences[currentSentenceIdx];

  // 문장 전환 애니메이션
  const sentenceStart = currentSentenceIdx * framesPerSentence;
  const sentenceFrame = localFrame - sentenceStart;
  const fadeIn = interpolate(sentenceFrame, [0, 8], [0, 1], { extrapolateRight: "clamp" });

  return (
    <div style={{
      position: "absolute",
      bottom: 120,
      left: 40,
      right: 40,
      display: "flex",
      justifyContent: "center",
    }}>
      <div style={{
        opacity: fadeIn,
        background: "rgba(0,0,0,0.7)",
        borderRadius: 16,
        padding: "20px 32px",
        maxWidth: 960,
      }}>
        <div style={{
          color: "#ffffff",
          fontSize: 32,
          fontWeight: 600,
          fontFamily: fonts.body,
          textAlign: "center",
          lineHeight: 1.5,
          wordBreak: "keep-all" as const,
        }}>
          {currentSentence}
        </div>
      </div>
    </div>
  );
};

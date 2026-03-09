import React from "react";
import { useCurrentFrame, useVideoConfig, interpolate } from "remotion";
import { theme, fonts } from "../styles/theme";
import type { Scene } from "../types";

interface Props {
  scenes: Scene[];
  sceneTimings: { start: number; duration: number }[];
}

function splitSentences(text: string): string[] {
  // 문장 끝 패턴으로 split하되, 마침표/물음표/느낌표를 포함한 채로
  const raw = text.match(/[^.?!요죠]+[.?!요죠]+/g);
  if (!raw) return [text];
  // 빈 문장, 공백만 있는 것, 구두점만 있는 것 제거
  return raw
    .map(s => s.trim())
    .filter(s => s.length > 1); // 1글자 이하(마침표 등) 제거
}

export const Subtitle: React.FC<Props> = ({ scenes, sceneTimings }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // 현재 프레임이 어느 씬에 속하는지
  let currentIdx = -1;
  for (let i = 0; i < scenes.length; i++) {
    const { start, duration } = sceneTimings[i];
    if (frame >= start && frame < start + duration) {
      currentIdx = i;
      break;
    }
  }
  if (currentIdx < 0) return null;

  const currentScene = scenes[currentIdx];
  const ttsText = currentScene.tts_text || "";
  if (!ttsText) return null;

  const sentences = splitSentences(ttsText);
  if (sentences.length === 0) return null;

  const sceneStart = sceneTimings[currentIdx].start;
  const sceneDuration = sceneTimings[currentIdx].duration;
  const localFrame = frame - sceneStart;

  const framesPerSentence = Math.floor(sceneDuration / sentences.length);
  const currentSentenceIdx = Math.min(
    Math.floor(localFrame / framesPerSentence),
    sentences.length - 1
  );
  const currentSentence = sentences[currentSentenceIdx];

  const sentenceStart = currentSentenceIdx * framesPerSentence;
  const sentenceFrame = localFrame - sentenceStart;
  const fadeIn = interpolate(sentenceFrame, [0, 6], [0, 1], { extrapolateRight: "clamp" });

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

import React from "react";
import { useCurrentFrame, useVideoConfig, interpolate } from "remotion";
import { fonts } from "../styles/theme";
import type { Scene } from "../types";

interface Props {
  scenes: Scene[];
  sceneTimings: { start: number; duration: number }[];
}

function splitSentences(text: string): string[] {
  // 한국어 어미 뒤에서 분리 (요, 죠, 고요, 거든요 등)
  // 숫자 속 마침표(17.5%)를 분리하지 않도록 주의
  const result: string[] = [];
  // 문장 종결 패턴: 한국어 어미 + 마침표/물음표/느낌표
  // 숫자.숫자는 분리하지 않음
  const pattern = /(?<!\d)([.!?])(?!\d)/g;
  
  let lastIdx = 0;
  let match;
  while ((match = pattern.exec(text)) !== null) {
    const end = match.index + 1;
    const chunk = text.slice(lastIdx, end).trim();
    if (chunk.length > 1) {
      result.push(chunk);
    }
    lastIdx = end;
  }
  // 남은 부분
  const rest = text.slice(lastIdx).trim();
  if (rest.length > 1) {
    result.push(rest);
  }
  
  return result.length > 0 ? result : [text];
}

export const Subtitle: React.FC<Props> = ({ scenes, sceneTimings }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

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

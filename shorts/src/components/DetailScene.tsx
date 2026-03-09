import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, spring } from "remotion";
import { theme, fonts } from "../styles/theme";
import type { Scene, Card } from "../types";

function splitSentences(text: string): string[] {
  const result: string[] = [];
  const pattern = /(?<!\d)([.!?])(?!\d)/g;
  let lastIdx = 0;
  let match;
  while ((match = pattern.exec(text)) !== null) {
    const end = match.index + 1;
    const chunk = text.slice(lastIdx, end).trim();
    if (chunk.length > 1) result.push(chunk);
    lastIdx = end;
  }
  const rest = text.slice(lastIdx).trim();
  if (rest.length > 1) result.push(rest);
  return result.length > 0 ? result : [text];
}

const StockCard: React.FC<{ card: Card; frame: number; fps: number; delay: number }> = ({ card, frame, fps, delay }) => {
  const progress = spring({ frame: frame - delay, fps, config: { damping: 14 } });
  const isNeg = (card.change || "").includes("-");
  const changeColor = isNeg ? theme.neonRed : theme.neonGreen;

  return (
    <div style={{
      opacity: progress,
      transform: `scale(${interpolate(progress, [0, 1], [0.95, 1])})`,
      background: theme.cardBg,
      border: `1px solid ${theme.cardBorder}`,
      borderRadius: 20,
      padding: "28px 32px",
      marginBottom: 16,
      borderLeft: `4px solid ${changeColor}`,
      width: "100%",
    }}>
      {/* 종목명 + 등락% */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
        <span style={{ color: theme.textPrimary, fontSize: 36, fontWeight: 800, fontFamily: fonts.title }}>
          {card.name}
        </span>
        <span style={{
          color: changeColor, fontSize: 40, fontWeight: 900, fontFamily: fonts.mono,
          textShadow: isNeg ? "0 0 15px rgba(255,68,102,0.3)" : "0 0 15px rgba(0,255,136,0.3)",
        }}>
          {card.change}
        </span>
      </div>
      {/* 가격 */}
      {card.price && (
        <div style={{ color: theme.textSecondary, fontSize: 28, fontFamily: fonts.mono, marginBottom: 6 }}>
          {card.price}
        </div>
      )}
      {/* 이유 */}
      {card.reason && (
        <div style={{ color: theme.neonBlue, fontSize: 26, fontFamily: fonts.body, marginBottom: 8, wordBreak: "keep-all" as const }}>
          💡 {card.reason}
        </div>
      )}
      {/* 지표 태그 */}
      {card.indicators && card.indicators.length > 0 && (
        <div style={{ display: "flex", flexWrap: "wrap" as const, gap: 8 }}>
          {card.indicators.map((ind, j) => (
            <span key={j} style={{
              color: theme.neonBlue, fontSize: 22, fontFamily: fonts.mono,
              background: "rgba(0,212,255,0.08)", borderRadius: 8, padding: "4px 10px",
            }}>
              {ind}
            </span>
          ))}
        </div>
      )}
    </div>
  );
};

export const DetailScene: React.FC<{ scene: Scene }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const segments = scene.visual_segments || [];
  const totalFrames = scene.duration * fps;

  const labelOpacity = interpolate(frame, [0, 10], [0, 1], { extrapolateRight: "clamp" });

  // TTS 문장 분리 → 현재 문장 번호 계산
  const sentences = splitSentences(scene.tts_text || "");
  const framesPerSentence = sentences.length > 0 ? Math.floor(totalFrames / sentences.length) : totalFrames;
  const currentSentence = Math.min(Math.floor(frame / framesPerSentence), sentences.length - 1);

  // 현재 문장에 해당하는 카드 찾기
  let activeSegmentIdx = 0;
  for (let i = segments.length - 1; i >= 0; i--) {
    if (currentSentence >= (segments[i].start_sentence || 0)) {
      activeSegmentIdx = i;
      break;
    }
  }

  const activeCard = segments[activeSegmentIdx]?.card;

  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", padding: "0 50px" }}>
      <div style={{
        opacity: labelOpacity,
        color: theme.neonPurple, fontSize: 28, fontWeight: 700,
        fontFamily: fonts.mono, letterSpacing: 3, marginBottom: 36,
        textShadow: "0 0 20px rgba(179,102,255,0.3)",
      }}>
        🔍 핵심 종목
      </div>

      <div style={{ width: "100%", maxWidth: 920 }}>
        {activeCard && <StockCard card={activeCard} frame={frame} fps={fps} delay={5} />}
      </div>
    </AbsoluteFill>
  );
};

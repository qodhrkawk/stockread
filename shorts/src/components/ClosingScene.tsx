import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, spring } from "remotion";
import { theme, fonts } from "../styles/theme";
import type { Scene } from "../types";

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

export const ClosingScene: React.FC<{ scene: Scene }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = spring({ frame: frame - 5, fps, config: { damping: 16 } });

  const tts = scene.tts_text || scene.message || "";
  const sentences = splitSentences(tts);

  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", padding: "0 60px" }}>
      <div style={{
        opacity: progress,
        transform: `translateY(${interpolate(progress, [0, 1], [30, 0])}px)`,
        background: `linear-gradient(135deg, rgba(0,255,136,0.06), rgba(0,212,255,0.04))`,
        border: `1px solid rgba(0,255,136,0.15)`,
        borderRadius: 24,
        padding: "50px 44px",
        maxWidth: 900,
        width: "100%",
      }}>
        {sentences.map((sentence, i) => {
          const lineProgress = spring({ frame: frame - 8 - i * 12, fps, config: { damping: 14 } });
          return (
            <div key={i} style={{
              opacity: lineProgress,
              color: theme.textPrimary,
              fontSize: 42,
              fontWeight: 700,
              fontFamily: fonts.body,
              textAlign: "center",
              lineHeight: 1.6,
              wordBreak: "keep-all" as const,
              marginBottom: i < sentences.length - 1 ? 20 : 0,
            }}>
              {sentence}
            </div>
          );
        })}
      </div>

      <div style={{
        opacity: interpolate(frame, [15, 30], [0, 0.5], { extrapolateRight: "clamp" }),
        marginTop: 40,
        color: theme.neonGreen,
        fontSize: 26,
        fontFamily: fonts.mono,
        fontWeight: 600,
        textShadow: theme.glowGreen,
      }}>
        📊 주읽이 StockRead
      </div>
    </AbsoluteFill>
  );
};

import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, spring } from "remotion";
import { theme, fonts } from "../styles/theme";
import type { Scene } from "../types";

export const ClosingScene: React.FC<{ scene: Scene }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = spring({ frame: frame - 5, fps, config: { damping: 16 } });

  // TTS 텍스트를 문장 단위로 분리해서 표시
  const tts = scene.tts_text || scene.message || "";
  const sentences = tts.split(/(?<=[.?!요죠])\s*/g).filter(s => s.trim());

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

      {/* 브랜딩 */}
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

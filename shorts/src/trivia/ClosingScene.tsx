import React from "react";
import { AbsoluteFill, useCurrentFrame, interpolate, useVideoConfig } from "remotion";
import { theme, fonts } from "../styles/theme";
import type { TriviaScene } from "./types";

export const ClosingScene: React.FC<{ scene: TriviaScene }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  // 글로우 배경 펄스
  const glowScale = interpolate(
    Math.sin(frame / 20),
    [-1, 1],
    [0.9, 1.1],
  );
  const glowOpacity = interpolate(
    Math.sin(frame / 20),
    [-1, 1],
    [0.08, 0.2],
  );

  const textOpacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateRight: "clamp",
  });
  const textY = interpolate(frame, [0, 20], [30, 0], {
    extrapolateRight: "clamp",
  });

  const message = scene.message || "";
  const lines = message.split("\n").filter(Boolean);

  return (
    <AbsoluteFill style={{
      display: "flex",
      flexDirection: "column",
      justifyContent: "center",
      alignItems: "center",
      padding: "60px 50px",
    }}>
      {/* 글로우 배경 */}
      <div style={{
        position: "absolute",
        width: 500,
        height: 500,
        borderRadius: "50%",
        background: `radial-gradient(circle, rgba(0,255,136,${glowOpacity}) 0%, transparent 70%)`,
        transform: `scale(${glowScale})`,
        filter: "blur(60px)",
      }} />

      {/* 메시지 */}
      <div style={{
        opacity: textOpacity,
        transform: `translateY(${textY}px)`,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 16,
        zIndex: 1,
      }}>
        {lines.map((line, i) => (
          <div key={i} style={{
            fontSize: i === 0 ? 52 : 40,
            fontWeight: i === 0 ? 800 : 600,
            fontFamily: fonts.title,
            color: i === 0 ? theme.neonGreen : theme.textPrimary,
            textAlign: "center",
            lineHeight: 1.4,
            wordBreak: "keep-all" as const,
            textShadow: i === 0
              ? theme.glowGreen
              : "0 2px 10px rgba(0,0,0,0.6)",
          }}>
            {line}
          </div>
        ))}
      </div>

      {/* 하단 구분선 + 브랜딩 */}
      <div style={{
        position: "absolute",
        bottom: 200,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 12,
        opacity: textOpacity,
      }}>
        <div style={{
          width: 60,
          height: 2,
          background: theme.textMuted,
          borderRadius: 1,
        }} />
        <div style={{
          fontSize: 22,
          fontFamily: fonts.mono,
          color: theme.textMuted,
          letterSpacing: 3,
        }}>
          60초 상식
        </div>
      </div>
    </AbsoluteFill>
  );
};

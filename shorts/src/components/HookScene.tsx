import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, spring } from "remotion";
import { theme, fonts } from "../styles/theme";
import type { Scene } from "../types";

export const HookScene: React.FC<{ scene: Scene }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const eventProgress = spring({ frame: frame - 3, fps, config: { damping: 12 } });
  const numberProgress = spring({ frame: frame - 15, fps, config: { damping: 14 } });

  const event = scene.event || "";
  const number = scene.number || "";
  const isNegative = number.includes("-");

  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", padding: "0 60px" }}>
      {/* 이벤트명 (크게) */}
      <div style={{
        opacity: eventProgress,
        transform: `scale(${interpolate(eventProgress, [0, 1], [0.6, 1])})`,
        color: isNegative ? theme.neonRed : theme.neonGreen,
        fontSize: 80,
        fontWeight: 900,
        fontFamily: fonts.title,
        textAlign: "center",
        lineHeight: 1.3,
        textShadow: isNegative
          ? "0 0 40px rgba(255,68,102,0.4)"
          : "0 0 40px rgba(0,255,136,0.4)",
        marginBottom: 24,
        wordBreak: "keep-all" as const,
      }}>
        {event}
      </div>

      {/* 보조 숫자 (작게) */}
      {number && (
        <div style={{
          opacity: numberProgress,
          color: isNegative ? theme.neonRed : theme.neonGreen,
          fontSize: 48,
          fontWeight: 700,
          fontFamily: fonts.mono,
          textShadow: isNegative
            ? "0 0 20px rgba(255,68,102,0.3)"
            : "0 0 20px rgba(0,255,136,0.3)",
        }}>
          코스피 {number}
        </div>
      )}

      {/* 브랜딩 */}
      <div style={{
        opacity: interpolate(frame, [20, 35], [0, 0.6], { extrapolateRight: "clamp" }),
        marginTop: 50,
        color: theme.neonGreen,
        fontSize: 28,
        fontFamily: fonts.mono,
        fontWeight: 600,
        textShadow: theme.glowGreen,
      }}>
        📊 주읽이
      </div>
    </AbsoluteFill>
  );
};

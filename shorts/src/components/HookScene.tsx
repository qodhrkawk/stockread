import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, spring } from "remotion";
import { theme, fonts } from "../styles/theme";
import type { Scene } from "../types";

export const HookScene: React.FC<{ scene: Scene }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const numberProgress = spring({ frame: frame - 5, fps, config: { damping: 12 } });
  const numberScale = interpolate(numberProgress, [0, 1], [0.5, 1]);
  const headlineProgress = spring({ frame: frame - 15, fps, config: { damping: 14 } });
  const headlineY = interpolate(headlineProgress, [0, 1], [40, 0]);

  const number = scene.number || "";
  const headline = scene.headline || "";
  const isNegative = number.includes("-");

  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", padding: "0 60px" }}>
      {/* 큰 숫자 */}
      <div style={{
        opacity: numberProgress,
        transform: `scale(${numberScale})`,
        color: isNegative ? theme.neonRed : theme.neonGreen,
        fontSize: 120,
        fontWeight: 900,
        fontFamily: fonts.mono,
        textShadow: isNegative
          ? "0 0 40px rgba(255,68,102,0.4)"
          : "0 0 40px rgba(0,255,136,0.4)",
        marginBottom: 20,
      }}>
        {number}
      </div>

      {/* 헤드라인 */}
      <div style={{
        opacity: headlineProgress,
        transform: `translateY(${headlineY}px)`,
        color: theme.textPrimary,
        fontSize: 52,
        fontWeight: 700,
        fontFamily: fonts.title,
        textAlign: "center",
        lineHeight: 1.4,
        wordBreak: "keep-all" as const,
      }}>
        {headline}
      </div>

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

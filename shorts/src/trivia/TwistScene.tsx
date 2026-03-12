import React from "react";
import { AbsoluteFill, useCurrentFrame, spring, useVideoConfig, interpolate } from "remotion";
import { theme, fonts } from "../styles/theme";
import type { TriviaScene } from "./types";

export const TwistScene: React.FC<{ scene: TriviaScene }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const highlightSpring = spring({ frame, fps, config: { damping: 12, mass: 1.2 } });
  const detailOpacity = interpolate(frame, [20, 30], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const detailY = interpolate(frame, [20, 35], [20, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // 글로우 펄스
  const glowIntensity = interpolate(
    Math.sin(frame / 15),
    [-1, 1],
    [0.3, 0.6],
  );

  return (
    <AbsoluteFill style={{
      display: "flex",
      flexDirection: "column",
      justifyContent: "center",
      alignItems: "center",
      padding: "60px 50px",
    }}>
      {/* 반전 라벨 */}
      <div style={{
        fontSize: 28,
        fontWeight: 600,
        fontFamily: fonts.body,
        color: theme.neonPurple,
        letterSpacing: 4,
        marginBottom: 30,
        opacity: interpolate(frame, [0, 10], [0, 1], { extrapolateRight: "clamp" }),
      }}>
        TWIST
      </div>

      {/* 하이라이트 */}
      <div style={{
        fontSize: 60,
        fontWeight: 800,
        fontFamily: fonts.title,
        color: theme.textPrimary,
        textAlign: "center",
        lineHeight: 1.3,
        wordBreak: "keep-all" as const,
        transform: `scale(${highlightSpring})`,
        textShadow: `0 0 30px rgba(179,102,255,${glowIntensity}), 0 4px 20px rgba(0,0,0,0.8)`,
        maxWidth: 900,
        marginBottom: 40,
      }}>
        {scene.highlight || ""}
      </div>

      {/* 부연 설명 */}
      <div style={{
        fontSize: 34,
        fontWeight: 500,
        fontFamily: fonts.body,
        color: theme.textSecondary,
        textAlign: "center",
        lineHeight: 1.5,
        wordBreak: "keep-all" as const,
        opacity: detailOpacity,
        transform: `translateY(${detailY}px)`,
        maxWidth: 850,
        textShadow: "0 2px 10px rgba(0,0,0,0.6)",
      }}>
        {scene.detail || ""}
      </div>
    </AbsoluteFill>
  );
};

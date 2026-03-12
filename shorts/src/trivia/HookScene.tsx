import React from "react";
import { AbsoluteFill, useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";
import { theme, fonts } from "../styles/theme";
import type { TriviaScene } from "./types";

export const HookScene: React.FC<{ scene: TriviaScene }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const questionSpring = spring({ frame, fps, config: { damping: 15 } });
  const factSpring = spring({ frame: frame - 15, fps, config: { damping: 15 } });
  const factOpacity = interpolate(frame, [15, 25], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{
      display: "flex",
      flexDirection: "column",
      justifyContent: "center",
      alignItems: "center",
      padding: "60px 50px",
    }}>
      {/* 질문 */}
      <div style={{
        fontSize: 64,
        fontWeight: 800,
        fontFamily: fonts.title,
        color: theme.textPrimary,
        textAlign: "center",
        lineHeight: 1.3,
        wordBreak: "keep-all" as const,
        transform: `scale(${questionSpring})`,
        textShadow: "0 4px 20px rgba(0,0,0,0.8)",
        marginBottom: 60,
      }}>
        {scene.question || ""}
      </div>

      {/* 충격 팩트 */}
      <div style={{
        fontSize: 36,
        fontWeight: 600,
        fontFamily: fonts.body,
        color: theme.neonGreen,
        textAlign: "center",
        lineHeight: 1.5,
        wordBreak: "keep-all" as const,
        opacity: factOpacity,
        transform: `translateY(${(1 - factSpring) * 30}px)`,
        textShadow: theme.glowGreen,
        maxWidth: 900,
      }}>
        {scene.fact || ""}
      </div>
    </AbsoluteFill>
  );
};

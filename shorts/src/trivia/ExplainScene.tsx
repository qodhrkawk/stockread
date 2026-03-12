import React from "react";
import { AbsoluteFill, useCurrentFrame, spring, useVideoConfig, interpolate } from "remotion";
import { theme, fonts } from "../styles/theme";
import type { TriviaScene } from "./types";

export const ExplainScene: React.FC<{ scene: TriviaScene }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const steps = scene.steps || [];

  return (
    <AbsoluteFill style={{
      display: "flex",
      flexDirection: "column",
      justifyContent: "center",
      padding: "80px 50px",
    }}>
      {/* 헤더 */}
      <div style={{
        fontSize: 40,
        fontWeight: 700,
        fontFamily: fonts.title,
        color: theme.neonBlue,
        textShadow: theme.glowBlue,
        marginBottom: 50,
        textAlign: "center",
      }}>
        알고 보면 신기한 이야기
      </div>

      {/* Step 카드들 */}
      {steps.map((step, i) => {
        const delay = i * 20;
        const s = spring({ frame: frame - delay, fps, config: { damping: 15 } });
        const opacity = interpolate(frame - delay, [0, 10], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });

        return (
          <div key={i} style={{
            display: "flex",
            alignItems: "center",
            gap: 24,
            marginBottom: 24,
            opacity,
            transform: `translateX(${(1 - s) * 60}px)`,
          }}>
            {/* 아이콘 */}
            <div style={{
              width: 80,
              height: 80,
              borderRadius: 20,
              background: "rgba(0,212,255,0.1)",
              border: "1px solid rgba(0,212,255,0.2)",
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              fontSize: 40,
              flexShrink: 0,
            }}>
              {step.icon}
            </div>

            {/* 텍스트 */}
            <div style={{
              fontSize: 36,
              fontWeight: 600,
              fontFamily: fonts.body,
              color: theme.textPrimary,
              lineHeight: 1.4,
              wordBreak: "keep-all" as const,
              textShadow: "0 2px 10px rgba(0,0,0,0.6)",
            }}>
              {step.text}
            </div>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

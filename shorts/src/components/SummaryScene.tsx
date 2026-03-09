import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, spring } from "remotion";
import { theme, fonts } from "../styles/theme";
import type { Scene } from "../types";

export const SummaryScene: React.FC<{ scene: Scene }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const segments = scene.visual_segments || [];

  const labelOpacity = interpolate(frame, [0, 10], [0, 1], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", padding: "0 60px" }}>
      <div style={{
        opacity: labelOpacity,
        color: theme.neonBlue,
        fontSize: 28,
        fontWeight: 700,
        fontFamily: fonts.mono,
        letterSpacing: 3,
        marginBottom: 50,
        textShadow: theme.glowBlue,
      }}>
        📊 오늘의 시장
      </div>

      <div style={{ width: "100%", maxWidth: 900 }}>
        {segments.map((seg, i) => {
          const sector = seg.sector;
          if (!sector) return null;
          const progress = spring({ frame: frame - 10 - i * 12, fps, config: { damping: 14 } });
          const isUp = sector.direction === "up";
          return (
            <div key={i} style={{
              opacity: progress,
              transform: `translateX(${interpolate(progress, [0, 1], [50, 0])}px)`,
              display: "flex",
              alignItems: "center",
              marginBottom: 24,
              background: theme.cardBg,
              border: `1px solid ${theme.cardBorder}`,
              borderRadius: 20,
              padding: "28px 36px",
              borderLeft: `4px solid ${isUp ? theme.neonGreen : theme.neonRed}`,
            }}>
              <span style={{ fontSize: 40, marginRight: 16 }}>{isUp ? "📈" : "📉"}</span>
              <span style={{
                color: theme.textPrimary,
                fontSize: 38,
                fontWeight: 700,
                fontFamily: fonts.body,
                wordBreak: "keep-all" as const,
                flex: 1,
              }}>
                {sector.name}
              </span>
              {sector.change && (
                <span style={{
                  color: isUp ? theme.neonGreen : theme.neonRed,
                  fontSize: 36,
                  fontWeight: 800,
                  fontFamily: fonts.mono,
                }}>
                  {sector.change}
                </span>
              )}
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

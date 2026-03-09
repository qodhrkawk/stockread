import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, spring } from "remotion";
import { theme, fonts } from "../styles/theme";
import type { Scene } from "../types";

export const DetailScene: React.FC<{ scene: Scene }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const cards = scene.cards || [];

  const labelOpacity = interpolate(frame, [0, 10], [0, 1], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", padding: "0 50px" }}>
      <div style={{
        opacity: labelOpacity,
        color: theme.neonPurple,
        fontSize: 28,
        fontWeight: 700,
        fontFamily: fonts.mono,
        letterSpacing: 3,
        marginBottom: 40,
        textShadow: "0 0 20px rgba(179,102,255,0.3)",
      }}>
        🔍 핵심 종목
      </div>

      <div style={{ width: "100%", maxWidth: 920 }}>
        {cards.map((card, i) => {
          const delay = 8 + i * 20;
          const progress = spring({ frame: frame - delay, fps, config: { damping: 14 } });
          const isNeg = (card.change || "").includes("-");
          const changeColor = isNeg ? theme.neonRed : theme.neonGreen;

          return (
            <div key={i} style={{
              opacity: progress,
              transform: `scale(${interpolate(progress, [0, 1], [0.95, 1])})`,
              background: theme.cardBg,
              border: `1px solid ${theme.cardBorder}`,
              borderRadius: 20,
              padding: "32px 36px",
              marginBottom: 20,
              borderLeft: `4px solid ${changeColor}`,
            }}>
              {/* 종목명 + 등락률 */}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                <span style={{
                  color: theme.textPrimary,
                  fontSize: 38,
                  fontWeight: 800,
                  fontFamily: fonts.title,
                }}>
                  {card.name}
                </span>
                <span style={{
                  color: changeColor,
                  fontSize: 42,
                  fontWeight: 900,
                  fontFamily: fonts.mono,
                  textShadow: isNeg
                    ? "0 0 15px rgba(255,68,102,0.3)"
                    : "0 0 15px rgba(0,255,136,0.3)",
                }}>
                  {card.change}
                </span>
              </div>

              {/* 가격 */}
              {card.price && (
                <div style={{ color: theme.textSecondary, fontSize: 30, fontFamily: fonts.mono, marginBottom: 8 }}>
                  {card.price}
                </div>
              )}

              {/* 지표 */}
              {card.indicators && card.indicators.length > 0 && (
                <div style={{ display: "flex", flexWrap: "wrap" as const, gap: 8, marginTop: 8 }}>
                  {card.indicators.map((ind, j) => (
                    <span key={j} style={{
                      color: theme.neonBlue,
                      fontSize: 24,
                      fontFamily: fonts.mono,
                      background: "rgba(0,212,255,0.08)",
                      borderRadius: 8,
                      padding: "6px 12px",
                    }}>
                      {ind}
                    </span>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

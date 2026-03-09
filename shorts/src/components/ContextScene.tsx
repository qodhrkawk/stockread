import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, spring } from "remotion";
import { theme, fonts } from "../styles/theme";
import type { Scene } from "../types";

export const ContextScene: React.FC<{ scene: Scene }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const flow = scene.flow || [];

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
        💡 왜 이렇게 됐을까?
      </div>

      {/* 원인 흐름 */}
      <div style={{ display: "flex", flexDirection: "column" as const, alignItems: "center", gap: 0 }}>
        {flow.map((item, i) => {
          const progress = spring({ frame: frame - 12 - i * 15, fps, config: { damping: 14 } });
          return (
            <React.Fragment key={i}>
              <div style={{
                opacity: progress,
                transform: `scale(${interpolate(progress, [0, 1], [0.8, 1])})`,
                background: `linear-gradient(135deg, rgba(0,212,255,0.08), rgba(179,102,255,0.06))`,
                border: `1px solid rgba(0,212,255,0.15)`,
                borderRadius: 20,
                padding: "28px 40px",
                minWidth: 300,
              }}>
                <div style={{
                  color: theme.textPrimary,
                  fontSize: 38,
                  fontWeight: 700,
                  fontFamily: fonts.body,
                  textAlign: "center",
                  wordBreak: "keep-all" as const,
                }}>
                  {item}
                </div>
              </div>
              {i < flow.length - 1 && (
                <div style={{
                  opacity: progress,
                  color: theme.neonBlue,
                  fontSize: 36,
                  margin: "8px 0",
                }}>
                  ↓
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

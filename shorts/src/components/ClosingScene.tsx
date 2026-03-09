import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, spring } from "remotion";
import { theme, fonts } from "../styles/theme";
import type { Scene } from "../types";

export const ClosingScene: React.FC<{ scene: Scene }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = spring({ frame: frame - 5, fps, config: { damping: 16 } });
  const message = scene.message || "";

  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", padding: "0 70px" }}>
      <div style={{
        opacity: progress,
        transform: `translateY(${interpolate(progress, [0, 1], [30, 0])}px)`,
        background: `linear-gradient(135deg, rgba(0,255,136,0.06), rgba(0,212,255,0.04))`,
        border: `1px solid rgba(0,255,136,0.15)`,
        borderRadius: 24,
        padding: "60px 50px",
        maxWidth: 900,
        width: "100%",
      }}>
        <div style={{
          color: theme.textPrimary,
          fontSize: 46,
          fontWeight: 700,
          fontFamily: fonts.body,
          textAlign: "center",
          lineHeight: 1.6,
          wordBreak: "keep-all" as const,
        }}>
          {message}
        </div>
      </div>
    </AbsoluteFill>
  );
};

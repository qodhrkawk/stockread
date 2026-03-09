import React from "react";
import { AbsoluteFill, useCurrentFrame, interpolate } from "remotion";
import { theme, fonts } from "../styles/theme";

export const Watermark: React.FC = () => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 30], [0, 0.5], {
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        position: "absolute",
        bottom: 60,
        left: 0,
        right: 0,
        display: "flex",
        justifyContent: "center",
        opacity,
      }}
    >
      <div
        style={{
          color: theme.textMuted,
          fontSize: 26,
          fontFamily: fonts.mono,
          fontWeight: 600,
          letterSpacing: 2,
        }}
      >
        주읽이
      </div>
    </div>
  );
};

import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
} from "remotion";
import { theme, fonts } from "../styles/theme";

interface Props {
  highlights: string[];
}

export const Highlights: React.FC<Props> = ({ highlights }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // 라벨 fade in
  const labelOpacity = interpolate(frame, [0, 12], [0, 1], {
    extrapolateRight: "clamp",
  });

  // 페이드 아웃
  const fadeOut = interpolate(
    frame,
    [fps * 10 - 15, fps * 10],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // 각 하이라이트 순차 등장
  const staggerDelay = 25; // 프레임 간격

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        padding: "0 70px",
        opacity: fadeOut,
      }}
    >
      {/* 섹션 라벨 */}
      <div
        style={{
          opacity: labelOpacity,
          color: theme.neonPurple,
          fontSize: 30,
          fontWeight: 700,
          fontFamily: fonts.mono,
          letterSpacing: 3,
          marginBottom: 50,
          textShadow: `0 0 20px rgba(179,102,255,0.3)`,
          textTransform: "uppercase",
        }}
      >
        🔥 핵심 종목
      </div>

      {/* 하이라이트 리스트 */}
      <div style={{ width: "100%", maxWidth: 900 }}>
        {highlights.map((item, i) => {
          const itemFrame = frame - 15 - i * staggerDelay;
          const progress = spring({
            frame: Math.max(0, itemFrame),
            fps,
            config: { damping: 14 },
          });
          const slideX = interpolate(progress, [0, 1], [60, 0]);
          const opacity = progress;

          // 색상 순환
          const colors = [theme.neonGreen, theme.neonBlue, theme.neonPurple];
          const color = colors[i % colors.length];

          return (
            <div
              key={i}
              style={{
                opacity,
                transform: `translateX(${slideX}px)`,
                display: "flex",
                alignItems: "center",
                marginBottom: 30,
                background: theme.cardBg,
                border: `1px solid ${theme.cardBorder}`,
                borderRadius: 20,
                padding: "36px 40px",
                borderLeft: `4px solid ${color}`,
              }}
            >
              <div
                style={{
                  color,
                  fontSize: 36,
                  fontWeight: 800,
                  fontFamily: fonts.mono,
                  marginRight: 24,
                  minWidth: 36,
                }}
              >
                {i + 1}
              </div>
              <div
                style={{
                  color: theme.textPrimary,
                  fontSize: 40,
                  fontWeight: 600,
                  fontFamily: fonts.body,
                  lineHeight: 1.4,
                }}
              >
                {item}
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

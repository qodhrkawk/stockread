import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Easing,
} from "remotion";
import { theme, fonts } from "../styles/theme";

interface Props {
  title: string;
  date: string;
}

export const HookTitle: React.FC<Props> = ({ title, date }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // 날짜 fade in
  const dateOpacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateRight: "clamp",
  });

  // 제목 스프링 애니메이션
  const titleProgress = spring({ frame: frame - 8, fps, config: { damping: 14 } });
  const titleY = interpolate(titleProgress, [0, 1], [80, 0]);
  const titleOpacity = titleProgress;

  // 밑줄 네온 라인
  const lineWidth = interpolate(frame, [15, 40], [0, 100], {
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  // 페이드 아웃 (마지막 15프레임)
  const fadeOut = interpolate(
    frame,
    [fps * 3 - 15, fps * 3],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        padding: "0 80px",
        opacity: fadeOut,
      }}
    >
      {/* 날짜 */}
      <div
        style={{
          opacity: dateOpacity,
          color: theme.neonGreen,
          fontSize: 36,
          fontWeight: 600,
          fontFamily: fonts.mono,
          letterSpacing: 4,
          marginBottom: 30,
          textShadow: theme.glowGreen,
        }}
      >
        📊 {date}
      </div>

      {/* 제목 */}
      <div
        style={{
          opacity: titleOpacity,
          transform: `translateY(${titleY}px)`,
          color: theme.textPrimary,
          fontSize: 64,
          fontWeight: 800,
          fontFamily: fonts.title,
          textAlign: "center",
          lineHeight: 1.3,
          letterSpacing: -1,
        }}
      >
        {title}
      </div>

      {/* 네온 라인 */}
      <div
        style={{
          marginTop: 40,
          width: `${lineWidth}%`,
          maxWidth: 400,
          height: 3,
          background: `linear-gradient(90deg, transparent, ${theme.neonGreen}, transparent)`,
          boxShadow: theme.glowGreen,
          borderRadius: 2,
        }}
      />
    </AbsoluteFill>
  );
};

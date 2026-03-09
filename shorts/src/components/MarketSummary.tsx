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
  summary: string;
}

export const MarketSummary: React.FC<Props> = ({ summary }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // 라벨 fade in
  const labelOpacity = interpolate(frame, [0, 12], [0, 1], {
    extrapolateRight: "clamp",
  });

  // 카드 스프링
  const cardProgress = spring({ frame: frame - 6, fps, config: { damping: 16 } });
  const cardScale = interpolate(cardProgress, [0, 1], [0.9, 1]);
  const cardOpacity = cardProgress;

  // 페이드 아웃
  const fadeOut = interpolate(
    frame,
    [fps * 7 - 15, fps * 7],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

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
          color: theme.neonBlue,
          fontSize: 30,
          fontWeight: 700,
          fontFamily: fonts.mono,
          letterSpacing: 3,
          marginBottom: 40,
          textShadow: theme.glowBlue,
          textTransform: "uppercase",
        }}
      >
        📈 오늘의 시장
      </div>

      {/* 요약 카드 */}
      <div
        style={{
          opacity: cardOpacity,
          transform: `scale(${cardScale})`,
          background: theme.cardBg,
          border: `1px solid ${theme.cardBorder}`,
          borderRadius: 24,
          padding: "60px 50px",
          width: "100%",
          maxWidth: 900,
        }}
      >
        <div
          style={{
            color: theme.textPrimary,
            fontSize: 52,
            fontWeight: 700,
            fontFamily: fonts.title,
            textAlign: "center",
            lineHeight: 1.5,
            wordBreak: "keep-all" as const,
            overflowWrap: "break-word" as const,
          }}
        >
          {summary}
        </div>
      </div>
    </AbsoluteFill>
  );
};

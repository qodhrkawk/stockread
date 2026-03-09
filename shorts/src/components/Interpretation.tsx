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
  text: string;
}

export const Interpretation: React.FC<Props> = ({ text }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // 라벨 fade in
  const labelOpacity = interpolate(frame, [0, 12], [0, 1], {
    extrapolateRight: "clamp",
  });

  // 텍스트 스프링
  const textProgress = spring({
    frame: frame - 10,
    fps,
    config: { damping: 16 },
  });
  const textY = interpolate(textProgress, [0, 1], [40, 0]);

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        padding: "0 70px",
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
          marginBottom: 50,
          textShadow: theme.glowBlue,
          textTransform: "uppercase",
        }}
      >
        💡 해석
      </div>

      {/* 해석 카드 */}
      <div
        style={{
          opacity: textProgress,
          transform: `translateY(${textY}px)`,
          background: `linear-gradient(135deg, rgba(0,255,136,0.06) 0%, rgba(0,212,255,0.04) 100%)`,
          border: `1px solid rgba(0,255,136,0.15)`,
          borderRadius: 24,
          padding: "60px 50px",
          width: "100%",
          maxWidth: 900,
        }}
      >
        <div
          style={{
            color: theme.textPrimary,
            fontSize: 46,
            fontWeight: 600,
            fontFamily: fonts.body,
            textAlign: "center",
            lineHeight: 1.6,
            wordBreak: "keep-all" as const,
            overflowWrap: "break-word" as const,
          }}
        >
          {text}
        </div>
      </div>

      {/* 면책 문구 */}
      <div
        style={{
          opacity: interpolate(frame, [30, 50], [0, 0.6], {
            extrapolateRight: "clamp",
          }),
          marginTop: 50,
          color: theme.textMuted,
          fontSize: 24,
          fontFamily: fonts.body,
          textAlign: "center",
        }}
      >
        ⚠️ 이 영상은 참고용이에요. 투자 판단은 본인이 직접 해주세요!
      </div>
    </AbsoluteFill>
  );
};

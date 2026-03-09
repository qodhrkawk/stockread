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
import type { Scene } from "../types";

interface Props {
  scene: Scene;
  isLast: boolean;
}

// 씬 라벨별 설정
const SCENE_CONFIG: Record<
  Scene["label"],
  { emoji: string; label: string; color: string; glow: string }
> = {
  hook: { emoji: "🔥", label: "", color: theme.neonGreen, glow: theme.glowGreen },
  summary: { emoji: "📈", label: "오늘의 시장", color: theme.neonBlue, glow: theme.glowBlue },
  detail: { emoji: "🔍", label: "핵심 종목", color: theme.neonPurple, glow: "0 0 20px rgba(179,102,255,0.3)" },
  context: { emoji: "💡", label: "왜 이렇게 됐을까?", color: theme.neonBlue, glow: theme.glowBlue },
  closing: { emoji: "✨", label: "정리하면", color: theme.neonGreen, glow: theme.glowGreen },
};

export const SceneRenderer: React.FC<Props> = ({ scene, isLast }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const config = SCENE_CONFIG[scene.label];
  const totalFrames = scene.duration * fps;

  // 진입 애니메이션
  const enterProgress = spring({ frame, fps, config: { damping: 14 } });
  const enterY = interpolate(enterProgress, [0, 1], [60, 0]);

  // 퇴장 애니메이션 (마지막 씬은 페이드아웃 없음)
  const fadeOut = isLast
    ? 1
    : interpolate(
        frame,
        [totalFrames - 12, totalFrames],
        [1, 0],
        { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
      );

  // 라벨 fade in
  const labelOpacity = interpolate(frame, [0, 10], [0, 1], {
    extrapolateRight: "clamp",
  });

  // 텍스트 줄 분리 + 순차 등장
  const lines = scene.text.split("\n");
  const lineDelay = 8; // 프레임 간격

  const isHook = scene.label === "hook";

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        padding: "0 70px",
        opacity: fadeOut,
      }}
    >
      {/* 섹션 라벨 (hook은 라벨 없음) */}
      {!isHook && config.label && (
        <div
          style={{
            opacity: labelOpacity,
            color: config.color,
            fontSize: 30,
            fontWeight: 700,
            fontFamily: fonts.mono,
            letterSpacing: 3,
            marginBottom: 40,
            textShadow: config.glow,
          }}
        >
          {config.emoji} {config.label}
        </div>
      )}

      {/* 메인 콘텐츠 카드 */}
      <div
        style={{
          opacity: enterProgress,
          transform: `translateY(${enterY}px)`,
          background: isHook ? "transparent" : theme.cardBg,
          border: isHook ? "none" : `1px solid ${theme.cardBorder}`,
          borderRadius: 24,
          padding: isHook ? "0" : "50px 44px",
          width: "100%",
          maxWidth: 920,
        }}
      >
        {lines.map((line, i) => {
          const lineFrame = frame - 6 - i * lineDelay;
          const lineProgress = spring({
            frame: Math.max(0, lineFrame),
            fps,
            config: { damping: 16 },
          });
          const lineX = interpolate(lineProgress, [0, 1], [40, 0]);

          return (
            <div
              key={i}
              style={{
                opacity: lineProgress,
                transform: `translateX(${lineX}px)`,
                color: theme.textPrimary,
                fontSize: isHook ? 62 : scene.label === "detail" ? 42 : 46,
                fontWeight: isHook ? 800 : 600,
                fontFamily: isHook ? fonts.title : fonts.body,
                textAlign: "center",
                lineHeight: 1.5,
                marginBottom: i < lines.length - 1 ? 16 : 0,
                wordBreak: "keep-all" as const,
                overflowWrap: "break-word" as const,
              }}
            >
              {line}
            </div>
          );
        })}
      </div>

      {/* hook: 날짜 표시 */}
      {isHook && (
        <div
          style={{
            opacity: labelOpacity,
            marginTop: 40,
            color: config.color,
            fontSize: 32,
            fontWeight: 600,
            fontFamily: fonts.mono,
            textShadow: config.glow,
          }}
        >
          📊 주읽이
        </div>
      )}
    </AbsoluteFill>
  );
};

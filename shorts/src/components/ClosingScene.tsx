import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, spring } from "remotion";
import { theme, fonts } from "../styles/theme";
import type { Scene } from "../types";

export const ClosingScene: React.FC<{ scene: Scene }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const message = scene.message || "";

  // 라인 분리
  const lines = message.split("\n").filter(l => l.trim());

  // 전체 등장
  const containerProgress = spring({ frame: frame - 3, fps, config: { damping: 16 } });

  // 글로우 펄스
  const pulse = interpolate(frame, [0, 60], [0, Math.PI * 2]);
  const glowOpacity = 0.15 + Math.sin(pulse) * 0.05;

  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", padding: "0 60px" }}>
      {/* 배경 글로우 원 */}
      <div style={{
        position: "absolute",
        width: 400,
        height: 400,
        borderRadius: "50%",
        background: `radial-gradient(circle, rgba(0,255,136,${glowOpacity}) 0%, transparent 70%)`,
        filter: "blur(60px)",
      }} />

      {/* 메인 키워드 */}
      <div style={{
        opacity: containerProgress,
        transform: `scale(${interpolate(containerProgress, [0, 1], [0.9, 1])})`,
        display: "flex",
        flexDirection: "column" as const,
        alignItems: "center",
        gap: 20,
      }}>
        {lines.map((line, i) => {
          const lineProgress = spring({ frame: frame - 6 - i * 10, fps, config: { damping: 14 } });
          const isFirst = i === 0;
          return (
            <div key={i} style={{
              opacity: lineProgress,
              transform: `translateY(${interpolate(lineProgress, [0, 1], [20, 0])}px)`,
              color: isFirst ? theme.neonGreen : theme.textPrimary,
              fontSize: isFirst ? 56 : 40,
              fontWeight: isFirst ? 800 : 600,
              fontFamily: isFirst ? fonts.title : fonts.body,
              textAlign: "center",
              lineHeight: 1.4,
              wordBreak: "keep-all" as const,
              textShadow: isFirst ? theme.glowGreen : "none",
              letterSpacing: isFirst ? 2 : 0,
            }}>
              {line}
            </div>
          );
        })}
      </div>

      {/* 하단 구분선 + 브랜딩 */}
      <div style={{
        opacity: interpolate(frame, [20, 35], [0, 0.6], { extrapolateRight: "clamp" }),
        marginTop: 60,
        display: "flex",
        flexDirection: "column" as const,
        alignItems: "center",
        gap: 16,
      }}>
        <div style={{
          width: 60,
          height: 2,
          background: `linear-gradient(90deg, transparent, ${theme.neonGreen}, transparent)`,
        }} />
        <div style={{
          color: theme.neonGreen,
          fontSize: 26,
          fontFamily: fonts.mono,
          fontWeight: 600,
          textShadow: theme.glowGreen,
        }}>
          📊 주읽이
        </div>
      </div>
    </AbsoluteFill>
  );
};

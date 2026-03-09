import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, spring } from "remotion";
import { theme, fonts } from "../styles/theme";
import type { Scene, Card } from "../types";

const StockCard: React.FC<{ card: Card; index: number; frame: number; fps: number }> = ({ card, index, frame, fps }) => {
  const progress = spring({ frame: frame - 8 - index * 10, fps, config: { damping: 14 } });
  const isNeg = (card.change || "").includes("-");
  const changeColor = isNeg ? theme.neonRed : theme.neonGreen;

  return (
    <div style={{
      opacity: progress,
      transform: `translateX(${interpolate(progress, [0, 1], [40, 0])}px)`,
      background: theme.cardBg,
      border: `1px solid ${theme.cardBorder}`,
      borderRadius: 18,
      padding: "22px 28px",
      marginBottom: 14,
      borderLeft: `4px solid ${changeColor}`,
      width: "100%",
    }}>
      {/* 종목명 + 등락% */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
        <span style={{ color: theme.textPrimary, fontSize: 32, fontWeight: 800, fontFamily: fonts.title }}>
          {card.name}
        </span>
        <span style={{
          color: changeColor, fontSize: 34, fontWeight: 900, fontFamily: fonts.mono,
          textShadow: isNeg ? "0 0 12px rgba(255,68,102,0.3)" : "0 0 12px rgba(0,255,136,0.3)",
        }}>
          {card.change}
        </span>
      </div>
      {/* 가격 + 이유 한줄 */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        {card.price && (
          <span style={{ color: theme.textSecondary, fontSize: 24, fontFamily: fonts.mono }}>
            {card.price}
          </span>
        )}
        {card.reason && (
          <span style={{ color: theme.neonBlue, fontSize: 22, fontFamily: fonts.body, wordBreak: "keep-all" as const }}>
            {card.reason}
          </span>
        )}
      </div>
      {/* 지표 태그 */}
      {card.indicators && card.indicators.length > 0 && (
        <div style={{ display: "flex", flexWrap: "wrap" as const, gap: 6, marginTop: 8 }}>
          {card.indicators.map((ind, j) => (
            <span key={j} style={{
              color: theme.neonBlue, fontSize: 20, fontFamily: fonts.mono,
              background: "rgba(0,212,255,0.08)", borderRadius: 6, padding: "3px 8px",
            }}>
              {ind}
            </span>
          ))}
        </div>
      )}
    </div>
  );
};

export const DetailScene: React.FC<{ scene: Scene }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const segments = scene.visual_segments || [];

  const labelOpacity = interpolate(frame, [0, 10], [0, 1], { extrapolateRight: "clamp" });

  // 모든 카드 추출
  const allCards = segments.map(seg => seg.card).filter(Boolean) as Card[];

  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", padding: "0 46px" }}>
      <div style={{
        opacity: labelOpacity,
        color: theme.neonPurple, fontSize: 28, fontWeight: 700,
        fontFamily: fonts.mono, letterSpacing: 3, marginBottom: 30,
        textShadow: "0 0 20px rgba(179,102,255,0.3)",
      }}>
        🔍 핵심 종목
      </div>

      <div style={{ width: "100%", maxWidth: 920 }}>
        {allCards.map((card, i) => (
          <StockCard key={i} card={card} index={i} frame={frame} fps={fps} />
        ))}
      </div>
    </AbsoluteFill>
  );
};

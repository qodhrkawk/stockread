import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "주읽이 StockRead — AI 투자 해석",
  description: "매일 아침 7시, AI가 당신의 종목을 초보 눈높이로 해석해 드려요.",
  openGraph: {
    title: "주읽이 StockRead — AI 투자 해석",
    description: "매일 아침 7시, AI가 당신의 종목을 초보 눈높이로 해석해 드려요.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="flex justify-center min-h-screen">{children}</body>
    </html>
  );
}

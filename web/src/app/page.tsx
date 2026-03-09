import Nav from "@/components/Nav";
import Hero from "@/components/Hero";
import ReportPreview from "@/components/ReportPreview";
import Features from "@/components/Features";
import HowItWorks from "@/components/HowItWorks";
import BottomCTA from "@/components/BottomCTA";
import Footer from "@/components/Footer";
import GradientLine from "@/components/GradientLine";

export default function Home() {
  return (
    <div className="w-full max-w-[390px] min-h-screen bg-bg overflow-x-hidden">
      <div className="h-12" />
      <Nav />
      <Hero />
      <GradientLine />
      <ReportPreview />
      <GradientLine />
      <Features />
      <GradientLine />
      <HowItWorks />
      <GradientLine />
      <BottomCTA />
      <Footer />
      <div className="h-6" />
    </div>
  );
}

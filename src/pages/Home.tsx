import { useReveal } from "@/hooks/useReveal";
import Nav from "@/components/Nav";
import Hero from "@/components/Hero";
import ServicesOverview from "@/components/ServicesOverview";
import ServiceDetail from "@/components/ServiceDetail";
import Cases from "@/components/Cases";
import Process from "@/components/Process";
import About from "@/components/About";
import Footer from "@/components/Footer";

export default function Home() {
  useReveal();
  return (
    <div className="min-h-screen bg-paper-100">
      <Nav />
      <main>
        <Hero />
        <ServicesOverview />
        <ServiceDetail />
        <Cases />
        <Process />
        <About />
      </main>
      <Footer />
    </div>
  );
}

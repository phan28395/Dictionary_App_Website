import Hero from '@/components/Hero';
import Features from '@/components/Features';
import Screenshots from '@/components/Screenshots';
import HowItWorks from '@/components/HowItWorks';
import Testimonials from '@/components/Testimonials';
import Header from '@/components/Header';
import Footer from '@/components/Footer';

export default function Home() {
  return (
    <div className="min-h-screen">
      <Header />
      <main>
        <Hero />
        <Features />
        <HowItWorks />
        <Screenshots />
        <Testimonials />
      </main>
      <Footer />
    </div>
  );
}
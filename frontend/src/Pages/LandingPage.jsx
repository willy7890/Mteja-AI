import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import Hero from '../component/Hero';
import TrustBar from '../component/TrustBar';
import AboutSection from '../component/AboutSection';
import FeatureGrid from '../component/FeatureGrid';
import ProblemSection from '../component/ProblemSection';
import Testimonials from '../component/Testimonials';
import FinalCta from '../component/FinalCta';

function LandingPage({ t }) {
  const location = useLocation();

  
  useEffect(() => {
    if (!location.hash) return;
    const id = location.hash.slice(1);
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  }, [location.hash]);

  return (
    <>
      <Hero t={t} />
      <TrustBar t={t} />
      <AboutSection t={t} />

      <div style={{ background: t.sectionTint }}>
        <FeatureGrid t={t} />
      </div>

      <ProblemSection t={t} />

      <div style={{ background: t.sectionTint }}>
        <Testimonials t={t} />
      </div>

      <FinalCta t={t} />
    </>
  );
}

export default LandingPage;
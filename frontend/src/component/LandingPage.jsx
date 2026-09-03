import Hero from './Hero';
import TrustBar from './TrustBar';
import FeatureGrid from './FeatureGrid';
import ProblemSection from './ProblemSection';
import Testimonials from './Testimonials';
import FinalCta from './FinalCta';

function LandingPage({ t }) {
  return (
    <>
      <Hero t={t} />
      <TrustBar t={t} />

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
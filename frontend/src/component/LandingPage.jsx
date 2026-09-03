import Hero from './Hero';
import TrustBar from './TrustBar';
import FeatureGrid from './FeatureGrid';
import ProblemSection from './ProblemSection';
import Testimonial from './Testimonial';
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
        <Testimonial t={t} />
      </div>

      <FinalCta t={t} />
    </>
  );
}

export default LandingPage;
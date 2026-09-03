import Hero from '../component/Hero';
import TrustBar from '../component/TrustBar';
import FeatureGrid from '../component/FeatureGrid';
import ProblemSection from '../component/ProblemSection';
import Testimonial from '../component/Testimonial';
import FinalCta from '../component/FinalCta';

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
import ScrollReveal from './ScrollReveal';

function AboutSection({ t }) {
  return (
    <section id="AboutPage" className="px-6 py-24 max-w-4xl mx-auto scroll-mt-24">
      <ScrollReveal>
        <div className="text-center">
          <span
            className="inline-block text-xs font-semibold px-3 py-1 rounded-full mb-4"
            style={{ background: `${t.accent}1A`, color: t.accent }}
          >
            Our story
          </span>
          <h2 className="text-3xl sm:text-4xl font-semibold tracking-tight" style={{ color: t.text }}>
            Built for business owners drowning in messages
          </h2>
          <p className="mt-5 text-lg leading-relaxed max-w-2xl mx-auto" style={{ color: t.muted }}>
            MtejaAI started with a simple observation: small business owners across
            Tanzania were losing real customers not because their products weren't
            good enough, but because a reply came an hour too late. WhatsApp,
            Instagram, email, and phone calls all competing for the same attention,
            all day, every day.
          </p>
          <p className="mt-4 text-lg leading-relaxed max-w-2xl mx-auto" style={{ color: t.muted }}>
            We built MtejaAI to close that gap — an AI that reads every channel a
            business actually uses, replies instantly in the owner's own voice,
            and only hands over the conversations that truly need a human touch.
          </p>
        </div>
      </ScrollReveal>
    </section>
  );
}

export default AboutSection;
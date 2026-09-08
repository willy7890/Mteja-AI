import ScrollReveal from './ScrollReveal';

function FinalCta({ t }) {
  return (
    <section className="px-6 py-6">
      <ScrollReveal>
        <div
          className="max-w-6xl mx-auto rounded-3xl px-8 py-14 sm:py-16 text-center relative overflow-hidden"
          style={{ background: t.accent }}
        >
          {/* A soft radial highlight in one corner — purely decorative,
              keeps a solid-color block from looking completely flat. */}
          <div
            className="absolute -top-24 -right-24 w-64 h-64 rounded-full"
            style={{ background: t.accentText, opacity: 0.08 }}
          />

          <h2
            className="text-3xl sm:text-4xl font-semibold tracking-tight relative"
            style={{ color: t.accentText }}
          >
            Ready to stop losing customers to slow replies?
          </h2>
          <p
            className="mt-3 text-lg max-w-md mx-auto relative"
            style={{ color: t.accentText, opacity: 0.85 }}
          >
            Start your free 14-day trial today. No credit card required.
          </p>

          <div className="mt-8 flex justify-center gap-3 relative flex-wrap">
            <button
              className="px-6 py-3 rounded-full font-medium transition-transform hover:scale-[1.03]"
              style={{ background: t.accentText, color: t.accent }}
            >
              Start free trial
            </button>
            <button
              className="px-6 py-3 rounded-full font-medium border transition-colors"
              style={{ borderColor: t.accentText, color: t.accentText }}
            >
              Request a demo
            </button>
          </div>
        </div>
      </ScrollReveal>
    </section>
  );
}

export default FinalCta;
import PlatformHub from './PlatformHub';

const featureTags = [
  { text: 'Instant replies', top: '12%', left: '8%', delay: '0s' },
  { text: '24/7 AI agent', top: '68%', left: '10%', delay: '0.6s' },
  { text: 'Never miss a lead', top: '18%', left: '80%', delay: '0.3s' },
  { text: 'One inbox, every channel', top: '72%', left: '78%', delay: '0.9s' },
];

function Hero({ t }) {
  return (
    <section className="relative pt-32 pb-20 px-6 overflow-hidden">
      {/* Headline block */}
      <div className="max-w-2xl mx-auto text-center relative z-10">
        <h1
          className="text-4xl sm:text-5xl font-semibold tracking-tight leading-[1.1] headline-line"
          style={{ color: t.text }}
        >
          One inbox for every message
          <br />
          your customers send you.
        </h1>
        <p
          className="mt-5 text-lg max-w-lg mx-auto headline-line"
          style={{ color: t.muted, animationDelay: '0.25s' }}
        >
          MtejaAI reads WhatsApp, Instagram, email, and calls and replies
          before your customer looks elsewhere.
        </p>
        <div className="mt-7 flex justify-center gap-3 headline-line" style={{ animationDelay: '0.45s' }}>
          <button
            className="px-6 py-3 rounded-full font-medium transition-transform hover:scale-[1.03]"
            style={{ background: t.accent, color: t.accentText }}
          >
            Start free trial
          </button>
          <button
            className="px-6 py-3 rounded-full font-medium"
            style={{ border: `1px solid ${t.border}`, color: t.text }}
          >
            See it reply live
          </button>
        </div>
      </div>

      {}
      <div className="absolute inset-0 pointer-events-none hidden md:block" style={{ zIndex: 0 }}>
        {featureTags.map((tag) => (
          <span
            key={tag.text}
            className="absolute px-4 py-2 rounded-full text-xs font-medium float-tag"
            style={{
              top: tag.top,
              left: tag.left,
              background: t.card,
              border: `1px solid ${t.border}`,
              color: t.muted,
              animationDelay: tag.delay,
              opacity: 0.85,
            }}
          >
            {tag.text}
          </span>
        ))}
      </div>

      {/* Hub sits above the floating tags */}
      <div className="relative mt-6" style={{ zIndex: 1 }}>
        <PlatformHub t={t} />
      </div>

      <style>{`
        @keyframes headlineIn {
          from { opacity: 0; transform: translateY(14px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .headline-line {
          opacity: 0;
          animation: headlineIn 0.6s cubic-bezier(0.22, 1, 0.36, 1) forwards;
        }

        @keyframes floatTag {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-10px); }
        }
        .float-tag { animation: floatTag 5s ease-in-out infinite; }
      `}</style>
    </section>
  );
}

export default Hero;
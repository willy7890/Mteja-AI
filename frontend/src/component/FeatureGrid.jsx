import { Inbox, Zap, Sparkles, Users, BarChart3, ShieldCheck } from 'lucide-react';
import ScrollReveal from './ScrollReveal';

const features = [
  {
    Icon: Inbox,
    title: 'Unified Inbox',
    desc: 'All your conversations from every channel, in one place.',
  },
  {
    Icon: Zap,
    title: 'Smart Automation',
    desc: 'Auto-reply to common questions and route the rest to you.',
  },
  {
    Icon: Sparkles,
    title: 'AI Assist',
    desc: 'AI-powered suggestions help you reply faster and better.',
  },
  {
    Icon: Users,
    title: 'Team Collaboration',
    desc: 'Work together with your team on shared conversations.',
  },
  {
    Icon: BarChart3,
    title: 'Analytics & Reports',
    desc: 'Track response times and customer satisfaction over time.',
  },
  {
    Icon: ShieldCheck,
    title: 'Secure & Reliable',
    desc: 'Enterprise-grade security to keep your customer data safe.',
  },
];

function FeatureGrid({ t }) {
  return (
    <section className="px-6 py-24 max-w-6xl mx-auto">
      <ScrollReveal>
        <div className="text-center max-w-xl mx-auto mb-14">
          <span
            className="inline-block text-xs font-semibold px-3 py-1 rounded-full mb-4"
            style={{ background: `${t.accent}1A`, color: t.accent }}
          >
            Everything you need
          </span>
          <h2 className="text-3xl sm:text-4xl font-semibold tracking-tight" style={{ color: t.text }}>
            Powerful features to delight your customers
          </h2>
          <p className="mt-3 text-lg" style={{ color: t.muted }}>
            All the tools you need to manage conversations and grow your business.
          </p>
        </div>
      </ScrollReveal>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {features.map((f, i) => (
          <ScrollReveal key={f.title} delay={i * 80}>
            <div
              className="rounded-2xl p-6 h-full transition-transform duration-200 hover:-translate-y-1"
              style={{ background: t.card, border: `1px solid ${t.border}` }}
            >
              <div
                className="w-10 h-10 rounded-xl flex items-center justify-center mb-4"
                style={{ background: `${t.accent}1A` }}
              >
                <f.Icon size={20} color={t.accent} strokeWidth={2} />
              </div>
              <h3 className="text-base font-semibold mb-1.5" style={{ color: t.text }}>
                {f.title}
              </h3>
              <p className="text-sm leading-relaxed" style={{ color: t.muted }}>
                {f.desc}
              </p>
            </div>
          </ScrollReveal>
        ))}
      </div>
    </section>
  );
}

export default FeatureGrid;
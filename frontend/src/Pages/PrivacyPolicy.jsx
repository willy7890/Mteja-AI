import { Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';

function PrivacyPolicy({ t }) {
  return (
    <div className="px-6 pt-32 pb-24 max-w-3xl mx-auto">
      <Link
        to="/"
        className="inline-flex items-center gap-1.5 text-sm mb-8 hover:opacity-70 transition-opacity"
        style={{ color: t.muted }}
      >
        <ArrowLeft size={15} /> Back home
      </Link>

      <h1 className="text-3xl font-semibold tracking-tight mb-6" style={{ color: t.text }}>
        Privacy Policy
      </h1>

      <div className="space-y-5 text-[15px] leading-relaxed" style={{ color: t.muted }}>
        <p>
          This is placeholder text. Replace this page with your actual Privacy
          Policy before launching — especially important here since MtejaAI
          handles real customer messages (WhatsApp, Instagram, email), which
          means real personal data.
        </p>
        <p>
          A real Privacy Policy typically covers: what data you collect, why,
          how long it's kept, whether it's shared with third parties (e.g. the
          AI provider processing replies), and how a user can request their
          data be deleted.
        </p>
        <p>
          Last updated: [add date when you publish real content here].
        </p>
      </div>
    </div>
  );
}

export default PrivacyPolicy;
import { Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';

function TermsOfService({ t }) {
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
        Terms of Service
      </h1>

      <div className="space-y-5 text-[15px] leading-relaxed" style={{ color: t.muted }}>
        <p>
          This is placeholder text. Replace this page with your actual Terms of
          Service before launching publicly — ideally reviewed by someone with
          legal knowledge, since this affects your rights and your customers'.
        </p>
        <p>
          A real Terms of Service page typically covers: what the service does,
          acceptable use, account responsibilities, payment terms (if
          applicable), limitation of liability, and how disputes are handled.
        </p>
        <p>
          Last updated: [add date when you publish real content here].
        </p>
      </div>
    </div>
  );
}

export default TermsOfService;
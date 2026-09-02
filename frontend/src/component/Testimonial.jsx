import { useState } from "react";

const testimonials = [
  {
    name: "Amina Hassan",
    role: "Owner, Amina's Boutique",
    quote: "I stopped losing customers to slow replies. MtejaAI answers while I'm serving someone in-store.",
    rating: 5,
  },
  {
    name: "Peter Mwakalinga",
    role: "Founder, TechFix Dar",
    quote: "The missed-call tracking alone paid for itself in the first week.",
    rating: 5,
  },
  {
    name: "Zainab Rajabu",
    role: "Owner, Zee's Fashion House",
    quote: "My WhatsApp, Instagram, and email all in one place. I finally reply to everyone.",
    rating: 4,
  },
];


function Stars({ count, color }) {
  return (
    <div className="flex gap-0.5">
      {[1, 2, 3, 4, 5].map((i) => (
        <span key={i} style={{ color: i <= count ? color : `${color}30` }}>
          ★
        </span>
      ))}
    </div>
  );
}

function Testimonials({ t }) {
  const [hovered, setHovered] = useState(null);

  return (
    <section className="px-6 py-24 max-w-6xl mx-auto">
      <div className="max-w-xl mb-14 mx-auto text-center">
        <h2 className="text-3xl sm:text-4xl font-semibold tracking-tight" style={{ color: t.text }}>
          What changes after switching
        </h2>
        <p className="mt-3 text-lg" style={{ color: t.muted }}>
          Real feedback from business owners who stopped juggling five apps at once.
        </p>
      </div>

      <div className="grid sm:grid-cols-3 gap-5">
        {testimonials.map((r, i) => {
          const isHovered = hovered === i;
          return (
            <div
              key={r.name}
              onMouseEnter={() => setHovered(i)}
              onMouseLeave={() => setHovered(null)}
              className="rounded-2xl p-6 flex flex-col transition-transform duration-200 ease-out cursor-default"
              style={{
                background: t.card,
                border: `1px solid ${isHovered ? t.accent : t.border}`,
                transform: isHovered ? "translateY(-4px)" : "translateY(0)",
                boxShadow: isHovered ? "0 16px 32px -12px rgba(0,0,0,0.25)" : "none",
              }}
            >
              <Stars count={r.rating} color={t.accent} />
              <p className="mt-4 text-[15px] leading-relaxed flex-1" style={{ color: t.text }}>
                "{r.quote}"
              </p>
              <div className="mt-5 pt-4" style={{ borderTop: `1px solid ${t.border}` }}>
                <div className="text-sm font-medium" style={{ color: t.text }}>
                  {r.name}
                </div>
                <div className="text-xs" style={{ color: t.muted }}>
                  {r.role}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}

export default Testimonials;
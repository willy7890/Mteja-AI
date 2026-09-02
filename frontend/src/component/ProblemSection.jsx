import { useState } from "react";

const complaints = [
  {
    name: "Fatuma, boutique owner",
    quote: "By the time I reply on WhatsApp, the customer already bought from someone else.",
  },
  {
    name: "David, electronics shop",
    quote: "I have messages on Instagram, Facebook, and email. I can't check all of them every hour.",
  },
  {
    name: "Grace, salon owner",
    quote: "Missed calls during appointments mean missed bookings. It happens almost daily.",
  },
  {
    name: "Juma, online reseller",
    quote: "Customers ask the same questions over and over. I'm typing the same answer all day.",
  },
];

function ProblemSection({ t }) {
 
  const [hovered, setHovered] = useState(null);

  return (
    <section className="px-6 py-24 max-w-6xl mx-auto">
      <div className="max-w-xl mb-14">
        <h2 className="text-3xl sm:text-4xl font-semibold tracking-tight" style={{ color: t.text }}>
          Sound familiar?
        </h2>
        <p className="mt-3 text-lg" style={{ color: t.muted }}>
          This is what running a business across five different apps actually feels like.
        </p>
      </div>

      <div className="grid sm:grid-cols-2 gap-5">
        {complaints.map((c, i) => {
          const isHovered = hovered === i;
          return (
            <div
              key={c.name}
              onMouseEnter={() => setHovered(i)}
              onMouseLeave={() => setHovered(null)}
              className="rounded-2xl p-6 relative transition-transform duration-200 ease-out cursor-default"
              style={{
                background: t.card,
                border: `1px solid ${isHovered ? t.accent : t.border}`,
                transform: isHovered ? "translateY(-4px)" : "translateY(0)",
                boxShadow: isHovered ? "0 16px 32px -12px rgba(0,0,0,0.25)" : "none",
              }}
            >
              
              <div
                className="absolute w-3 h-3 rotate-45 -top-1.5 left-8 transition-colors duration-200"
                style={{
                  background: t.card,
                  borderLeft: `1px solid ${isHovered ? t.accent : t.border}`,
                  borderTop: `1px solid ${isHovered ? t.accent : t.border}`,
                }}
              />
              <p className="text-[15px] leading-relaxed" style={{ color: t.text }}>
                "{c.quote}"
              </p>
              <div className="mt-4 text-sm font-medium" style={{ color: t.muted }}>
                {c.name}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}

export default ProblemSection;
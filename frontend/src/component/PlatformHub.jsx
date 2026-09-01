import { useEffect, useState } from 'react';
import { MessageCircle, Mail, Instagram, Phone, Send, Facebook } from 'lucide-react';

// Each satellite: icon, brand color (used only for the icon itself, not
// the whole page theme), and its angle around the circle in degrees.
const platforms = [
  { Icon: MessageCircle, color: '#25D366', angle: -90 },   // WhatsApp-style
  { Icon: Instagram, color: '#E1306C', angle: -30 },
  { Icon: Mail, color: '#EA4335', angle: 30 },
  { Icon: Facebook, color: '#0084FF', angle: 90 },
  { Icon: Phone, color: '#6B7A72', angle: 150 },
  { Icon: Send, color: '#229ED9', angle: -150 },
];

const SIZE = 420;
const CENTER = SIZE / 2;
const RADIUS = 150;

function PlatformHub({ t }) {
  const [drawn, setDrawn] = useState(false);

  // Trigger the line-drawing animation once, shortly after mount.
  useEffect(() => {
    const timer = setTimeout(() => setDrawn(true), 200);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="relative mx-auto" style={{ width: SIZE, height: SIZE }}>
      <svg width={SIZE} height={SIZE} className="absolute inset-0">
        {platforms.map((p, i) => {
          const rad = (p.angle * Math.PI) / 180;
          const x = CENTER + RADIUS * Math.cos(rad);
          const y = CENTER + RADIUS * Math.sin(rad);
          // A slight curve instead of a straight line: bend the midpoint
          // perpendicular to the line direction.
          const midX = (CENTER + x) / 2 + (y - CENTER) * 0.15;
          const midY = (CENTER + y) / 2 - (x - CENTER) * 0.15;

          return (
            <path
              key={i}
              d={`M ${CENTER} ${CENTER} Q ${midX} ${midY} ${x} ${y}`}
              fill="none"
              stroke={t.accent}
              strokeWidth="2"
              strokeLinecap="round"
              strokeDasharray="300"
              strokeDashoffset={drawn ? 0 : 300}
              style={{ transition: `stroke-dashoffset 0.9s ease-out ${i * 0.08}s`, opacity: 0.5 }}
            />
          );
        })}
      </svg>

      {/* Central hub */}
      <div
        className="absolute flex items-center justify-center rounded-2xl shadow-xl"
        style={{
          width: 84,
          height: 84,
          left: CENTER - 42,
          top: CENTER - 42,
          background: t.accent,
        }}
      >
        <MessageCircle size={36} color={t.accentText} strokeWidth={2.2} />
      </div>

      {/* Satellite icons */}
      {platforms.map((p, i) => {
        const rad = (p.angle * Math.PI) / 180;
        const x = CENTER + RADIUS * Math.cos(rad);
        const y = CENTER + RADIUS * Math.sin(rad);
        const { Icon } = p;

        return (
          <div
            key={i}
            className="absolute flex items-center justify-center rounded-full shadow-lg float"
            style={{
              width: 52,
              height: 52,
              left: x - 26,
              top: y - 26,
              background: t.card,
              border: `1px solid ${t.border}`,
              animationDelay: `${i * 0.3}s`,
              opacity: drawn ? 1 : 0,
              transform: drawn ? 'scale(1)' : 'scale(0.6)',
              transition: `opacity 0.4s ease-out ${0.6 + i * 0.08}s, transform 0.4s ease-out ${0.6 + i * 0.08}s`,
            }}
          >
            <Icon size={22} color={p.color} strokeWidth={2} />
          </div>
        );
      })}

      <style>{`
        @keyframes floatY {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-6px); }
        }
        .float { animation: floatY 3s ease-in-out infinite; }
      `}</style>
    </div>
  );
}

export default PlatformHub;
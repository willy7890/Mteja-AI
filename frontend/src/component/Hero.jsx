import { useState, useEffect } from 'react';
import PlatformHub from './PlatformHub';

const script = [
  { from: 'user', text: 'Hi, is the blue jacket still available?' },
  { from: 'ai', text: 'Yes! We have it in M, L, and XL. Want me to hold one for you?' },
  { from: 'user', text: 'Yes please, size L' },
  { from: 'ai', text: 'Done ✅ Reserved for 24 hours. Payment link sent to your WhatsApp.' },
];

function Hero({ t }) {
  const [visible, setVisible] = useState(0);

  useEffect(() => {
    if (visible >= script.length) {
      const reset = setTimeout(() => setVisible(0), 2400);
      return () => clearTimeout(reset);
    }
    const timer = setTimeout(() => setVisible((v) => v + 1), 1400);
    return () => clearTimeout(timer);
  }, [visible]);

  return (
    <div className="pt-28 px-6 max-w-md mx-auto">
      <div
        className="rounded-2xl shadow-xl p-5 space-y-3 min-h-[320px]"
        style={{ background: t.card, border: `1px solid ${t.border}` }}
      >
        {script.slice(0, visible).map((msg, i) => (
          <div key={i} className={`flex ${msg.from === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div
              className="max-w-[75%] px-4 py-2 rounded-2xl text-sm"
              style={{
                background: msg.from === 'user' ? t.accent : t.bubbleAi,
                color: msg.from === 'user' ? t.accentText : t.text,
              }}
            >
              {msg.text}
              {msg.from === 'ai' && (
                <div className="text-[10px] mt-1" style={{ color: t.muted }}>
                  MtejaAI
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Hero;
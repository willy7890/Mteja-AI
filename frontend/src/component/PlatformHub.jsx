import { useEffect, useState } from "react";
import { MessageCircle, Mail, Instagram, Phone, Send, Facebook, Sun, Moon } from "lucide-react";

// `type` decides which row template renders inside the popover:
// "chat" = message list (WhatsApp/Instagram/Messenger/Telegram style),
// "inbox" = email-style rows, "calls" = call-log rows.
const platforms = [
  {
    Icon: MessageCircle, color: "#25D366", angle: -90, name: "WhatsApp", type: "chat",
    items: [
      { who: "Amina K.", text: "Is the blue jacket still available?", time: "2m" },
      { who: "Juma S.", text: "Can I pay on delivery?", time: "14m" },
      { who: "Grace M.", text: "Thank you! Order received 🙏", time: "1h" },
    ],
  },
  {
    Icon: Instagram, color: "#E1306C", angle: -30, name: "Instagram", type: "chat",
    items: [
      { who: "@neema.designs", text: "Do you ship to Mwanza?", time: "5m" },
      { who: "@collins_tz", text: "Price for the leather bag?", time: "22m" },
      { who: "@fatuma.retail", text: "Following up on my order", time: "3h" },
    ],
  },
  {
    Icon: Mail, color: "#EA4335", angle: 30, name: "Email", type: "inbox",
    items: [
      { who: "David Mwakalinga", subj: "Invoice request", time: "9:14" },
      { who: "Sarah Kimaro", subj: "Bulk order enquiry", time: "8:02" },
      { who: "Peter Nyerere", subj: "Refund status?", time: "Yesterday" },
    ],
  },
  {
    Icon: Facebook, color: "#0084FF", angle: 90, name: "Messenger", type: "chat",
    items: [
      { who: "Happiness L.", text: "Still waiting for a reply", time: "1m" },
      { who: "Baraka T.", text: "Do you have size 42?", time: "18m" },
      { who: "Zainab R.", text: "Sent the payment ✅", time: "2h" },
    ],
  },
  {
    Icon: Phone, color: "#6B7A72", angle: 150, name: "Calls", type: "calls",
    items: [
      { who: "+255 754 221 908", note: "Missed call", time: "10m" },
      { who: "+255 682 004 511", note: "Missed call", time: "47m" },
      { who: "+255 719 887 302", note: "Missed call", time: "3h" },
    ],
  },
  {
    Icon: Send, color: "#229ED9", angle: -150, name: "Telegram", type: "chat",
    items: [
      { who: "Emmanuel J.", text: "Any discount for 5 pieces?", time: "6m" },
      { who: "Rehema A.", text: "Is this original or copy?", time: "40m" },
      { who: "Victor P.", text: "Order confirmed, thanks", time: "5h" },
    ],
  },
];

const SIZE = 420;
const CENTER = SIZE / 2;
const RADIUS = 150;

// Center hub mini-conversation: shows the assistant replying to messages
// pulled in from different channels, to visually tie the satellites
// (the problem: messages piling up everywhere) to the hub (the fix).
const hubScript = [
  { from: "in", channel: "WhatsApp", text: "Is the blue jacket still available?" },
  { from: "ai", text: "Yes! Available in M, L, XL. Want one held for you?" },
  { from: "in", channel: "Instagram", text: "Do you ship to Mwanza?" },
  { from: "ai", text: "Yes, 2–3 days delivery. Want me to start your order?" },
];

function PlatformHub({ t }) {
  const [drawn, setDrawn] = useState(false);
  const [hovered, setHovered] = useState(null);
  const [centerHovered, setCenterHovered] = useState(false);
  const [hubVisible, setHubVisible] = useState(0);
  const [hubTyping, setHubTyping] = useState(false);

  useEffect(() => {
    setDrawn(false);
    const timer = setTimeout(() => setDrawn(true), 200);
    return () => clearTimeout(timer);
  }, [t]);

  // Drives the center hub's mini chat: only runs while hovered. Resets to
  // the start whenever the mouse leaves, so it always replays from message 1.
  useEffect(() => {
    if (!centerHovered) {
      setHubVisible(0);
      setHubTyping(false);
      return;
    }
    if (hubVisible >= hubScript.length) return;

    const isAi = hubScript[hubVisible].from === "ai";
    if (isAi) {
      setHubTyping(true);
      const timer = setTimeout(() => {
        setHubTyping(false);
        setHubVisible((v) => v + 1);
      }, 700);
      return () => clearTimeout(timer);
    }
    const timer = setTimeout(() => setHubVisible((v) => v + 1), 900);
    return () => clearTimeout(timer);
  }, [centerHovered, hubVisible]);

  return (
    <div className="relative mx-auto" style={{ width: SIZE, height: SIZE }}>
      <svg width={SIZE} height={SIZE} className="absolute inset-0">
        {platforms.map((p, i) => {
          const rad = (p.angle * Math.PI) / 180;
          const x = CENTER + RADIUS * Math.cos(rad);
          const y = CENTER + RADIUS * Math.sin(rad);
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

      <div
        className="absolute flex items-center justify-center rounded-2xl shadow-xl cursor-pointer"
        onMouseEnter={() => setCenterHovered(true)}
        onMouseLeave={() => setCenterHovered(false)}
        style={{
          width: 84,
          height: 84,
          left: CENTER - 42,
          top: CENTER - 42,
          background: t.accent,
          transform: centerHovered ? "scale(1.08)" : "scale(1)",
          transition: "transform 0.2s ease-out",
          zIndex: 25,
        }}
      >
        <MessageCircle size={36} color={t.accentText} strokeWidth={2.2} />
      </div>

      {centerHovered && (
        <div
          className="absolute rounded-xl shadow-2xl overflow-hidden pointer-events-none"
          style={{
            left: CENTER - 115,
            top: CENTER - 210,
            width: 230,
            background: t.card,
            border: `1px solid ${t.border}`,
            zIndex: 30,
            animation: "popIn 0.15s ease-out",
          }}
        >
          <div
            className="px-3.5 py-2.5 text-xs font-semibold flex items-center gap-2"
            style={{ background: t.accent, color: t.accentText }}
          >
            <span className="w-1.5 h-1.5 rounded-full" style={{ background: t.accentText }} />
            MtejaAI replying live
          </div>

          <div className="px-3.5 py-3 space-y-2 min-h-[150px] flex flex-col justify-end">
            {hubScript.slice(0, hubVisible).map((msg, i) => (
              <div key={i} className={`flex ${msg.from === "ai" ? "justify-end" : "justify-start"}`}>
                <div
                  className="max-w-[85%] px-2.5 py-1.5 rounded-xl text-[11px] leading-snug"
                  style={{
                    background: msg.from === "ai" ? t.accent : `${t.text}0F`,
                    color: msg.from === "ai" ? t.accentText : t.text,
                  }}
                >
                  {msg.from === "in" && (
                    <div className="text-[9px] font-semibold mb-0.5 opacity-60">{msg.channel}</div>
                  )}
                  {msg.text}
                </div>
              </div>
            ))}

            {hubTyping && (
              <div className="flex justify-end">
                <div className="px-3 py-2 rounded-xl flex gap-1" style={{ background: t.accent }}>
                  {[0, 1, 2].map((d) => (
                    <span
                      key={d}
                      className="w-1 h-1 rounded-full animate-bounce"
                      style={{ background: t.accentText, animationDelay: `${d * 0.12}s` }}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {platforms.map((p, i) => {
        const rad = (p.angle * Math.PI) / 180;
        const x = CENTER + RADIUS * Math.cos(rad);
        const y = CENTER + RADIUS * Math.sin(rad);
        const { Icon } = p;
        const isHovered = hovered === i;

        // Popover position: push it further out along the same angle the
        // icon already sits on, so it always appears "outside" the circle
        // instead of overlapping neighboring icons.
        const popX = CENTER + (RADIUS + 110) * Math.cos(rad);
        const popY = CENTER + (RADIUS + 75) * Math.sin(rad);

        return (
          <div key={i}>
            <div
              className="absolute flex items-center justify-center rounded-full shadow-lg float cursor-pointer"
              onMouseEnter={() => setHovered(i)}
              onMouseLeave={() => setHovered(null)}
              style={{
                width: 52,
                height: 52,
                left: x - 26,
                top: y - 26,
                background: t.card,
                border: isHovered ? `2px solid ${p.color}` : `1px solid ${t.border}`,
                animationDelay: `${i * 0.3}s`,
                animationPlayState: isHovered ? "paused" : "running",
                opacity: drawn ? 1 : 0,
                transform: drawn ? (isHovered ? "scale(1.15)" : "scale(1)") : "scale(0.6)",
                transition: `transform 0.2s ease-out, opacity 0.4s ease-out ${0.6 + i * 0.08}s, border 0.15s`,
                zIndex: isHovered ? 20 : 1,
              }}
            >
              <Icon size={22} color={p.color} strokeWidth={2} />

              <span
                className="absolute -top-1.5 -right-1.5 flex items-center justify-center rounded-full text-[10px] font-semibold text-white"
                style={{ width: 18, height: 18, background: "#E5484D" }}
              >
                {p.items.length}
              </span>
            </div>

            {isHovered && (
              <div
                className="absolute rounded-xl shadow-2xl overflow-hidden pointer-events-none"
                style={{
                  left: popX - 100,
                  top: popY - 90,
                  width: 220,
                  background: t.card,
                  border: `1px solid ${t.border}`,
                  zIndex: 30,
                  animation: "popIn 0.15s ease-out",
                }}
              >
                <div
                  className="px-3.5 py-2.5 text-xs font-semibold flex items-center gap-2"
                  style={{ background: p.color, color: "#fff" }}
                >
                  <Icon size={14} color="#fff" />
                  {p.name}
                </div>

                <div>
                  {p.items.map((item, idx) => (
                    <div
                      key={idx}
                      className="px-3.5 py-2 flex items-center gap-2.5"
                      style={{ borderBottom: idx < p.items.length - 1 ? `1px solid ${t.border}` : "none" }}
                    >
                      {p.type === "calls" ? (
                        <>
                          <div
                            className="w-7 h-7 rounded-full flex items-center justify-center shrink-0"
                            style={{ background: `${p.color}22` }}
                          >
                            <Phone size={13} color={p.color} />
                          </div>
                          <div className="min-w-0 flex-1">
                            <div className="text-[11px] font-medium truncate" style={{ color: t.text }}>
                              {item.who}
                            </div>
                            <div className="text-[10px]" style={{ color: p.color }}>
                              {item.note}
                            </div>
                          </div>
                        </>
                      ) : (
                        <>
                          <div
                            className="w-7 h-7 rounded-full flex items-center justify-center shrink-0 text-[10px] font-semibold text-white"
                            style={{ background: p.color }}
                          >
                            {item.who.charAt(0)}
                          </div>
                          <div className="min-w-0 flex-1">
                            <div className="text-[11px] font-medium truncate" style={{ color: t.text }}>
                              {item.who}
                            </div>
                            <div className="text-[10px] truncate" style={{ color: t.text, opacity: 0.6 }}>
                              {p.type === "inbox" ? item.subj : item.text}
                            </div>
                          </div>
                        </>
                      )}
                      <div className="text-[9px] shrink-0" style={{ color: t.text, opacity: 0.4 }}>
                        {item.time}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        );
      })}

      <style>{`
        @keyframes floatY {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-6px); }
        }
        .float { animation: floatY 3s ease-in-out infinite; }

        @keyframes popIn {
          from { opacity: 0; transform: scale(0.9); }
          to { opacity: 1; transform: scale(1); }
        }
      `}</style>
    </div>
  );
}

const themes = {
  light: {
    bg: "#F3F1EA",
    text: "#14201A",
    card: "#FFFFFF",
    accent: "#2F6F4E",
    accentText: "#FFFFFF",
    border: "rgba(20,32,26,0.10)",
  },
  dark: {
    bg: "#0B1220",
    text: "#F2F0E8",
    card: "#141E2B",
    accent: "#4FD1C5",
    accentText: "#0B1220",
    border: "rgba(242,240,232,0.12)",
  },
};

export default PlatformHub;
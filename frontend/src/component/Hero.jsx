import React,{ useState, useEffect } from "react";

const script = [
  { from: "user", text: "Hi, is the blue jacket still available?" },
  { from: "ai", text: "Yes! We have it in M, L, and XL. Want me to hold one for you?" },
  { from: "user", text: "Yes please, size L" },
  { from: "ai", text: "Done ✅ Reserved for 24 hours. Payment link sent to your WhatsApp." },
];

function ChatDemo() {
  const [visible, setVisible] = useState(0);

  useEffect(() => {
    if (visible >= script.length) return;
    const timer = setTimeout(() => setVisible(v => v + 1), 1400);
    return () => clearTimeout(timer);
  }, [visible]);

  return (
    <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-5 space-y-3 min-h-[320px]">
      {script.slice(0, visible).map((msg, i) => (
        <div
          key={i}
          className={`flex ${msg.from === "user" ? "justify-end" : "justify-start"} animate-[fadeIn_0.4s_ease-out]`}
        >
          <div
            className={`max-w-[75%] px-4 py-2 rounded-2xl text-sm ${
              msg.from === "user"
                ? "bg-indigo-600 text-white rounded-br-sm"
                : "bg-gray-100 text-gray-800 rounded-bl-sm"
            }`}
          >
            {msg.text}
            {msg.from === "ai" && (
              <div className="text-[10px] text-gray-400 mt-1">MtejaAI</div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

export default Hero
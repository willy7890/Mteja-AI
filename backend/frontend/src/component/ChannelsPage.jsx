import React from "react";
import { Send, MessageSquare, Camera, Mail, PhoneCall, Video } from "lucide-react";

export const ChannelsPage = ({ t, onOpenTelegramModal }) => {
  const channelsList = [
    {
      id: "telegram",
      name: "Telegram",
      description: "Unganisha Telegram Bot kupokea na kujibu jumbe za wateja.",
      icon: Send,
      color: "#0088cc",
      connected: false,
      action: onOpenTelegramModal,
    },
    {
      id: "whatsapp",
      name: "WhatsApp Business",
      description: "Unganisha WhatsApp Cloud API kwa mawasiliano ya haraka.",
      icon: MessageSquare,
      color: "#25D366",
      connected: true,
      action: () => alert("WhatsApp ipo connected tayari!"),
    },
    {
      id: "tiktok",
      name: "TikTok Direct Messages",
      description: "Unganisha akaunti yako ya TikTok Business kupokea DM.",
      icon: Video,
      color: "#00f2fe",
      connected: false,
      action: () => alert("TikTok modal inakuja hivi karibuni!"),
    },
    {
      id: "email",
      name: "Email Integration",
      description: "Unganisha barua pepe yako (SMTP/IMAP) kwa maombi ya wateja.",
      icon: Mail,
      color: "#4285F4",
      connected: true,
      action: () => alert("Email ipo connected tayari!"),
    },
  ];

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight" style={{ color: t.text }}>
          Channels Manager 🌐
        </h1>
        <p className="text-sm mt-1" style={{ color: t.muted }}>
          Dhibiti na uunganishe chaneli zote za mawasiliano za MtejaAI hapa.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {channelsList.map((ch) => {
          const Icon = ch.icon;
          return (
            <div
              key={ch.id}
              className="p-5 rounded-2xl flex flex-col justify-between space-y-4 border transition-all"
              style={{ background: t.card, borderColor: t.border }}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div
                    className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0"
                    style={{ background: `${ch.color}15` }}
                  >
                    <Icon size={24} color={ch.color} />
                  </div>
                  <div>
                    <h3 className="font-semibold text-base" style={{ color: t.text }}>
                      {ch.name}
                    </h3>
                    <span
                      className={`inline-block text-[10px] font-bold px-2 py-0.5 rounded-full mt-1 ${
                        ch.connected ? "bg-green-500/10 text-green-500" : "bg-gray-500/10 text-gray-400"
                      }`}
                    >
                      {ch.connected ? "Connected 🟢" : "Not Connected 🔴"}
                    </span>
                  </div>
                </div>
              </div>

              <p className="text-xs leading-relaxed" style={{ color: t.muted }}>
                {ch.description}
              </p>

              <div className="pt-2">
                <button
                  onClick={ch.action}
                  className="w-full py-2.5 px-4 rounded-xl font-medium text-xs transition-opacity hover:opacity-90"
                  style={{
                    background: ch.connected ? t.surface : t.accent,
                    color: ch.connected ? t.text : t.accentText,
                  }}
                >
                  {ch.connected ? "Settings / Manage" : "Connect Channel"}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
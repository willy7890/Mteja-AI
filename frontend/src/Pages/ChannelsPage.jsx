import React, { useState } from 'react';
import {
  MessageSquare,
  Instagram,
  Mail,
  PhoneCall,
  CheckCircle2,
  RefreshCw,
  Settings,
  ExternalLink,
  ShieldCheck,
  QrCode,
  Smartphone,
  Plus,
  X,
  AlertCircle
} from 'lucide-react';
import { ChannelIntegration, ChannelType, PageId } from '../../types';

interface ChannelsPageProps {
  channels: ChannelIntegration[];
  onNavigate: (page: PageId) => void;
}

export const ChannelsPage: React.FC<ChannelsPageProps> = ({
  channels: initialChannels,
  onNavigate,
}) => {
  const [channels, setChannels] = useState<ChannelIntegration[]>(initialChannels);
  const [activeModalChannel, setActiveModalChannel] = useState<ChannelIntegration | null>(null);
  const [syncingId, setSyncingId] = useState<string | null>(null);

  const handleSync = (id: string) => {
    setSyncingId(id);
    setTimeout(() => {
      setSyncingId(null);
    }, 1200);
  };

  const getChannelIcon = (type: ChannelType) => {
    switch (type) {
      case 'whatsapp': return <MessageSquare className="w-6 h-6 text-white" />;
      case 'instagram': return <Instagram className="w-6 h-6 text-white" />;
      case 'email': return <Mail className="w-6 h-6 text-white" />;
      case 'call': return <PhoneCall className="w-6 h-6 text-white" />;
    }
  };

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-[#10231C] tracking-tight">Channels & Integrations</h2>
          <p className="text-xs text-[#68756F] mt-1">
            Connect your customer touchpoints into a unified agentic AI pipeline.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-[#35D98A]/20 text-xs font-bold text-[#10231C]">
            <span className="w-2 h-2 rounded-full bg-[#287A59] animate-pulse" />
            <span>4 / 4 Channels Operational</span>
          </span>
        </div>
      </div>

      {/* Security Banner */}
      <div className="p-4 rounded-2xl bg-[#10231C] text-white flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-[#287A59] flex items-center justify-center text-white font-bold">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-white">Meta Cloud API & Africa's Talking Telecom Certified</h4>
            <p className="text-[11px] text-[#8E9B95] mt-0.5">
              Zero rate limits, end-to-end encryption, and compliant with Tanzanian data privacy directives.
            </p>
          </div>
        </div>
        <button
          onClick={() => onNavigate('inbox')}
          className="hidden sm:inline-flex items-center gap-1 text-xs text-[#35D98A] font-bold hover:underline"
        >
          <span>Open Unified Inbox</span>
          <ExternalLink className="w-3 h-3" />
        </button>
      </div>

      {/* Integration Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {channels.map((ch) => (
          <div
            key={ch.id}
            className="p-6 rounded-2xl bg-white border border-[#E2E4DF] hover:border-[#287A59]/40 transition-colors shadow-2xs flex flex-col justify-between space-y-5"
          >
            <div>
              {/* Header */}
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div
                    className="w-12 h-12 rounded-xl flex items-center justify-center shadow-xs"
                    style={{ backgroundColor: ch.iconBg }}
                  >
                    {getChannelIcon(ch.type)}
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-[#10231C]">{ch.name}</h3>
                    <div className="flex items-center gap-1.5 mt-0.5">
                      <span className="w-2 h-2 rounded-full bg-[#35D98A]" />
                      <span className="text-xs font-semibold text-[#287A59]">
                        {ch.connected ? 'Connected & Active' : 'Not Connected'}
                      </span>
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => handleSync(ch.id)}
                  disabled={syncingId === ch.id}
                  className="p-2 rounded-lg text-[#68756F] hover:bg-[#F7F6F1] hover:text-[#10231C] transition-colors"
                  title="Force refresh synchronization"
                >
                  <RefreshCw className={`w-4 h-4 ${syncingId === ch.id ? 'animate-spin text-[#287A59]' : ''}`} />
                </button>
              </div>

              {/* Account details & sync status */}
              <div className="mt-4 p-3 rounded-xl bg-[#F7F6F1] border border-[#E2E4DF] space-y-1 text-xs">
                <div className="flex justify-between">
                  <span className="text-[#68756F]">Account Identifier:</span>
                  <span className="font-semibold text-[#10231C] truncate max-w-[200px]">{ch.accountInfo}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#68756F]">Last Synchronization:</span>
                  <span className="font-medium text-[#10231C]">{ch.lastSync}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#68756F]">Status:</span>
                  <span className="text-[#287A59] font-medium">{ch.statusText}</span>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center justify-between pt-3 border-t border-[#E2E4DF] text-xs">
              <button
                onClick={() => setActiveModalChannel(ch)}
                className="font-bold text-[#14201B] hover:text-[#287A59] flex items-center gap-1.5"
              >
                <Settings className="w-3.5 h-3.5" />
                <span>Configure Settings</span>
              </button>

              <button
                onClick={() => setActiveModalChannel(ch)}
                className="px-3 py-1.5 rounded-lg bg-[#10231C] text-white font-bold hover:bg-[#287A59] transition-colors"
              >
                Reconnect Channel
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Connection & Setup Modal */}
      {activeModalChannel && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-xs">
          <div className="bg-white w-full max-w-lg rounded-2xl border border-[#E2E4DF] p-6 shadow-2xl space-y-4 animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between border-b border-[#E2E4DF] pb-3">
              <div className="flex items-center gap-2.5">
                <div
                  className="w-8 h-8 rounded-lg flex items-center justify-center shadow-xs"
                  style={{ backgroundColor: activeModalChannel.iconBg }}
                >
                  {getChannelIcon(activeModalChannel.type)}
                </div>
                <div>
                  <h3 className="text-sm font-bold text-[#10231C]">{activeModalChannel.name} Connection</h3>
                  <p className="text-[11px] text-[#68756F]">Verify webhook credentials and auto-reply permissions</p>
                </div>
              </div>
              <button
                onClick={() => setActiveModalChannel(null)}
                className="p-1 rounded-md text-[#68756F] hover:bg-[#F7F6F1]"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Channel-specific connect flow */}
            {activeModalChannel.type === 'whatsapp' && (
              <div className="space-y-4 text-xs">
                <div className="p-4 rounded-xl bg-[#F7F6F1] border border-[#E2E4DF] flex items-center gap-4">
                  <div className="p-3 bg-white rounded-lg border border-[#E2E4DF] shadow-2xs flex-shrink-0">
                    <QrCode className="w-20 h-20 text-[#10231C]" />
                  </div>
                  <div>
                    <h4 className="font-bold text-[#10231C]">Scan to Pair WhatsApp Business</h4>
                    <p className="text-[#68756F] mt-1">
                      Open WhatsApp on your phone &gt; Settings &gt; Linked Devices &gt; Scan this QR code to enable real-time message sync.
                    </p>
                    <span className="inline-block mt-2 font-bold text-[#287A59]">
                      ✓ Meta Cloud API Token Verified
                    </span>
                  </div>
                </div>

                <div>
                  <label className="block font-semibold text-[#14201B] mb-1">WhatsApp Business Phone Number</label>
                  <input
                    type="text"
                    defaultValue="+255 754 892 100"
                    className="w-full p-2.5 rounded-xl border border-[#E2E4DF] bg-white font-mono text-xs"
                  />
                </div>
              </div>
            )}

            {activeModalChannel.type === 'instagram' && (
              <div className="space-y-3 text-xs">
                <p className="text-[#68756F]">
                  MtejaAI uses Meta Business Graph API to receive Direct Messages and Story Mentions.
                </p>
                <div className="p-3 rounded-xl bg-[#F7F6F1] border border-[#E2E4DF] space-y-1">
                  <div className="flex justify-between">
                    <span className="text-[#68756F]">Connected Profile:</span>
                    <span className="font-bold text-[#10231C]">@zawadi_emporium_tz</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-[#68756F]">Followers:</span>
                    <span className="font-medium">14,200</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-[#68756F]">Story Mention Webhook:</span>
                    <span className="font-bold text-[#287A59]">Active (Instant trigger)</span>
                  </div>
                </div>
              </div>
            )}

            {activeModalChannel.type === 'email' && (
              <div className="space-y-3 text-xs">
                <p className="text-[#68756F]">
                  Synchronized with Google Workspace corporate MX records for support@zawadi.co.tz.
                </p>
                <div>
                  <label className="block font-semibold text-[#14201B] mb-1">Support Inbound Email</label>
                  <input
                    type="email"
                    defaultValue="support@zawadi.co.tz"
                    className="w-full p-2.5 rounded-xl border border-[#E2E4DF] bg-white text-xs"
                  />
                </div>
              </div>
            )}

            {activeModalChannel.type === 'call' && (
              <div className="space-y-3 text-xs">
                <p className="text-[#68756F]">
                  Powered by Africa's Talking Telecom SIP gateway with Swahili voice model. Missed calls automatically trigger a WhatsApp brochure within 10 seconds.
                </p>
                <div className="p-3 rounded-xl bg-[#F7F6F1] border border-[#E2E4DF] space-y-1">
                  <span className="font-bold text-[#10231C]">SIP Hotline: +255 22 211 4900</span>
                  <p className="text-[#68756F]">Auto-record and speech-to-text enabled.</p>
                </div>
              </div>
            )}

            <div className="flex items-center justify-end gap-2 pt-3 border-t border-[#E2E4DF] text-xs">
              <button
                type="button"
                onClick={() => setActiveModalChannel(null)}
                className="px-4 py-2 rounded-xl font-semibold text-[#68756F] hover:bg-[#F7F6F1]"
              >
                Close
              </button>
              <button
                type="button"
                onClick={() => setActiveModalChannel(null)}
                className="px-4 py-2 rounded-xl bg-[#287A59] text-white font-bold hover:bg-[#1f5f45]"
              >
                Save Integration
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
export default ChannelsPage;
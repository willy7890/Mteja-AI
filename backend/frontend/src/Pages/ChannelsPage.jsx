import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  RefreshCw,
  Settings,
  ExternalLink,
  ShieldCheck,
  X,
  Loader2,
} from 'lucide-react';
import {
  FaWhatsapp,
  FaTelegram,
  FaTiktok,
  FaInstagram,
  FaFacebookF,
  FaEnvelope,
  FaCommentSms,
  FaPhone,
} from 'react-icons/fa6';
import { apiAuthPost, apiGet } from '../api/Client';

const DEFAULT_CHANNELS = [
  {
    id: 'whatsapp',
    type: 'whatsapp',
    name: 'WhatsApp Business',
    iconBg: '#25D366',
    connected: false,
    accountInfo: 'Not connected',
    lastSync: '—',
    statusText: 'Connect to start receiving messages',
    icon: FaWhatsapp,
  },
  {
    id: 'telegram',
    type: 'telegram',
    name: 'Telegram',
    iconBg: '#229ED9',
    connected: false,
    accountInfo: 'Not connected',
    lastSync: '—',
    statusText: 'Connect bot to receive messages',
    icon: FaTelegram,
  },
  {
    id: 'instagram',
    type: 'instagram',
    name: 'Instagram Direct',
    iconBg: '#E4405F',
    connected: false,
    accountInfo: 'Not connected',
    lastSync: '—',
    statusText: 'Connect Meta Business account',
    icon: FaInstagram,
  },
  {
    id: 'email',
    type: 'email',
    name: 'Email',
    iconBg: '#4285F4',
    connected: false,
    accountInfo: 'Not connected',
    lastSync: '—',
    statusText: 'Connect inbox to sync emails',
    icon: FaEnvelope,
  },
  {
    id: 'sms',
    type: 'sms',
    name: 'Normal SMS',
    iconBg: '#287A59',
    connected: false,
    accountInfo: 'Not connected',
    lastSync: '—',
    statusText: 'Connect an SMS provider to receive texts',
    icon: FaCommentSms,
  },
  {
    id: 'tiktok',
    type: 'tiktok',
    name: 'TikTok Direct Messages',
    iconBg: '#111111',
    connected: false,
    accountInfo: 'Not connected',
    lastSync: '—',
    statusText: 'Connect TikTok Business to receive DMs',
    icon: FaTiktok,
  },
  {
    id: 'facebook',
    type: 'facebook',
    name: 'Facebook Messenger',
    iconBg: '#1877F2',
    connected: false,
    accountInfo: 'Not connected',
    lastSync: '—',
    statusText: 'Connect Facebook Page Messenger',
    icon: FaFacebookF,
  },
  {
    id: 'call',
    type: 'call',
    name: 'Phone & Voice',
    iconBg: '#287A59',
    connected: false,
    accountInfo: 'Not connected',
    lastSync: '—',
    statusText: 'Connect for missed-call handling',
    icon: FaPhone,
  },
];

function ChannelsPage() {
  const navigate = useNavigate();
  const [channels, setChannels] = useState(DEFAULT_CHANNELS);
  const [loading, setLoading] = useState(true);
  const [activeModal, setActiveModal] = useState(null);
  const [syncingId, setSyncingId] = useState(null);
  const [telegramActionLoading, setTelegramActionLoading] = useState(false);
  const [telegramError, setTelegramError] = useState('');

  const updateTelegramChannel = (status) => {
    setChannels((current) =>
      current.map((channel) => {
        if (channel.type !== 'telegram') return channel;
        const bot = status?.bot;
        const connected = Boolean(status?.connected && status?.webhook?.configured);
        return {
          ...channel,
          connected,
          accountInfo: connected && bot?.username ? `@${bot.username}` : 'Not connected',
          lastSync: connected ? 'Just now' : '—',
          statusText: connected
            ? 'Receiving Telegram messages'
            : status?.error || 'Connect bot to receive messages',
        };
      })
    );
  };

  const loadTelegramStatus = async () => {
    try {
      const status = await apiGet('/api/v1/telegram/status');
      updateTelegramChannel(status);
    } catch (error) {
      updateTelegramChannel({ error: error.message });
    }
  };

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        await loadTelegramStatus();
      } catch {
        await loadTelegramStatus();
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const handleSync = (id) => {
    setSyncingId(id);
    if (id === 'telegram') {
      loadTelegramStatus().finally(() => setSyncingId(null));
      return;
    }
    setTimeout(() => setSyncingId(null), 1000);
  };

  const handleTelegramAction = async () => {
    if (!activeModal || activeModal.type !== 'telegram') return;
    setTelegramActionLoading(true);
    setTelegramError('');
    try {
      const path = activeModal.connected
        ? '/api/v1/telegram/disconnect'
        : '/api/v1/telegram/connect';
      await apiAuthPost(path, {});
      await loadTelegramStatus();
      setActiveModal(null);
    } catch (error) {
      setTelegramError(error.message || 'Telegram connection failed');
    } finally {
      setTelegramActionLoading(false);
    }
  };

  const getChannelIcon = (type, size = 'w-6 h-6') => {
    const cls = `${size} text-white`;
    switch (type) {
      case 'whatsapp': return <FaWhatsapp className={cls} />;
      case 'telegram': return <FaTelegram className={cls} />;
      case 'tiktok': return <FaTiktok className={cls} />;
      case 'instagram': return <FaInstagram className={cls} />;
      case 'facebook': return <FaFacebookF className={cls} />;
      case 'email': return <FaEnvelope className={cls} />;
      case 'sms': return <FaCommentSms className={cls} />;
      case 'call': return <FaPhone className={cls} />;
      default:
        return <MessageSquare className={cls} />;
    }
  };

  const connectedCount = channels.filter((c) => c.connected).length;

  if (loading) {
    return (
      <div className="p-6 md:p-8 flex items-center justify-center min-h-[50vh]">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="w-7 h-7 animate-spin text-[#287A59]" />
          <p className="text-sm text-[#68756F]">Loading channels...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-[#10231C] tracking-tight">
            Channels & Integrations
          </h2>
          <p className="text-xs text-[#68756F] mt-1">
            Connect seven channels into one unified inbox.
          </p>
        </div>

        <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-[#F7F6F1] text-xs font-bold text-[#10231C]">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>
            {connectedCount} / {channels.length} Connected
          </span>
        </span>
      </div>

      {/* Banner */}
      <div className="p-4 rounded-2xl bg-[#10231C] text-white flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-[#287A59] flex items-center justify-center">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-white">
              Secure channel connections
            </h4>
            <p className="text-[11px] text-[#8E9B95] mt-0.5">
              Messages stay encrypted. Only connected channels appear in your Inbox.
            </p>
          </div>
        </div>
        <button
          onClick={() => navigate('/dashboard/inbox')}
          className="hidden sm:inline-flex items-center gap-1 text-xs text-[#35D98A] font-bold hover:underline"
        >
          Open Unified Inbox
          <ExternalLink className="w-3 h-3" />
        </button>
      </div>

      {/* Channel cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {channels.map((ch) => (
          <div
            key={ch.id}
            className="p-6 rounded-2xl bg-white border border-[#E2E4DF] hover:border-[#287A59]/40 transition-colors flex flex-col justify-between space-y-5"
          >
            <div>
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div
                    className="w-12 h-12 rounded-xl flex items-center justify-center"
                    style={{ backgroundColor: ch.iconBg || '#287A59' }}
                  >
                    {getChannelIcon(ch.type)}
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-[#10231C]">{ch.name}</h3>
                    <div className="flex items-center gap-1.5 mt-0.5">
                      {ch.connected ? (
                        <ShieldCheck className="w-3.5 h-3.5 text-[#287A59]" />
                      ) : (
                        <Settings className="w-3.5 h-3.5 text-[#68756F]" />
                      )}
                      <span
                        className={`text-xs font-semibold ${
                          ch.connected ? 'text-[#287A59]' : 'text-[#68756F]'
                        }`}
                      >
                        {ch.connected ? 'Connected' : 'Not connected'}
                      </span>
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => handleSync(ch.id)}
                  disabled={syncingId === ch.id}
                  className="p-2 rounded-lg text-[#68756F] hover:bg-[#F7F6F1]"
                  title="Refresh"
                >
                  <RefreshCw
                    className={`w-4 h-4 ${
                      syncingId === ch.id ? 'animate-spin text-[#287A59]' : ''
                    }`}
                  />
                </button>
              </div>

              <div className="mt-4 p-3 rounded-xl bg-[#F7F6F1] border border-[#E2E4DF] space-y-1 text-xs">
                <div className="flex justify-between gap-2">
                  <span className="text-[#68756F]">Account:</span>
                  <span className="font-semibold text-[#10231C] truncate max-w-[180px]">
                    {ch.accountInfo || '—'}
                  </span>
                </div>
                <div className="flex justify-between gap-2">
                  <span className="text-[#68756F]">Last sync:</span>
                  <span className="font-medium text-[#10231C]">
                    {ch.lastSync || '—'}
                  </span>
                </div>
                <div className="flex justify-between gap-2">
                  <span className="text-[#68756F]">Status:</span>
                  <span
                    className={
                      ch.connected ? 'text-[#287A59] font-medium' : 'text-[#68756F]'
                    }
                  >
                    {ch.statusText || (ch.connected ? 'Active' : 'Not connected')}
                  </span>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between pt-3 border-t border-[#E2E4DF] text-xs">
              <button
                onClick={() => setActiveModal(ch)}
                className="font-bold text-[#14201B] hover:text-[#287A59] flex items-center gap-1.5"
              >
                <Settings className="w-3.5 h-3.5" />
                Configure
              </button>

              <button
                onClick={() => setActiveModal(ch)}
                className="px-3 py-1.5 rounded-lg bg-[#10231C] text-white font-bold hover:bg-[#287A59] transition-colors"
              >
                {ch.connected ? 'Manage' : 'Connect'}
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Modal */}
      {activeModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40">
          <div className="bg-white w-full max-w-lg rounded-2xl border border-[#E2E4DF] p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-[#E2E4DF] pb-3">
              <div className="flex items-center gap-2.5">
                <div
                  className="w-8 h-8 rounded-lg flex items-center justify-center"
                  style={{ backgroundColor: activeModal.iconBg || '#287A59' }}
                >
                  {getChannelIcon(activeModal.type, 'w-4 h-4')}
                </div>
                <div>
                  <h3 className="text-sm font-bold text-[#10231C]">
                    {activeModal.name}
                  </h3>
                  <p className="text-[11px] text-[#68756F]">
                    {activeModal.connected
                      ? 'Manage connection'
                      : 'Connect this channel'}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setActiveModal(null)}
                className="p-1 rounded-md text-[#68756F] hover:bg-[#F7F6F1]"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="text-xs space-y-3">
              {activeModal.type === 'whatsapp' && (
                <p className="text-[#68756F]">
                  Connect WhatsApp Business via Meta Cloud API. You will need a
                  Business phone number and API token from Meta.
                </p>
              )}
              {activeModal.type === 'telegram' && (
                <div className="space-y-2 text-[#68756F]">
                  <p>
                    Telegram is configured securely on the backend. This browser
                    never receives or stores your bot token.
                  </p>
                  <p>
                    The Connect action registers the server webhook with Telegram.
                  </p>
                </div>
              )}
              {activeModal.type === 'instagram' && (
                <p className="text-[#68756F]">
                  Connect via Meta Business so Instagram DMs appear in your
                  Unified Inbox.
                </p>
              )}
              {activeModal.type === 'email' && (
                <p className="text-[#68756F]">
                  Connect your support email so customer emails sync into the
                  inbox.
                </p>
              )}
              {activeModal.type === 'sms' && (
                <p className="text-[#68756F]">
                  Connect an SMS provider to receive and respond to standard text messages.
                </p>
              )}
              {activeModal.type === 'call' && (
                <p className="text-[#68756F]">
                  Connect your business line so missed calls can trigger follow-up
                  messages.
                </p>
              )}

              <div className="p-3 rounded-xl bg-[#F7F6F1] border border-[#E2E4DF]">
                <p className="text-[#68756F]">
                  Set <span className="font-mono">TELEGRAM_BOT_TOKEN</span> and
                  <span className="font-mono"> TELEGRAM_WEBHOOK_URL</span> in the
                  backend environment before connecting.
                </p>
              </div>
            </div>

            {activeModal.type === 'telegram' && telegramError && (
              <p className="rounded-xl bg-red-50 px-3 py-2 text-xs text-red-700">
                {telegramError}
              </p>
            )}

            <div className="flex items-center justify-end gap-2 pt-3 border-t border-[#E2E4DF] text-xs">
              <button
                type="button"
                onClick={() => setActiveModal(null)}
                className="px-4 py-2 rounded-xl font-semibold text-[#68756F] hover:bg-[#F7F6F1]"
              >
                Close
              </button>
              <button
                type="button"
                onClick={activeModal.type === 'telegram' ? handleTelegramAction : () => setActiveModal(null)}
                disabled={telegramActionLoading}
                className="px-4 py-2 rounded-xl bg-[#287A59] text-white font-bold hover:bg-[#1f5f45] disabled:opacity-60"
              >
                {telegramActionLoading
                  ? 'Connecting...'
                  : activeModal.type === 'telegram'
                    ? activeModal.connected ? 'Disconnect' : 'Connect Telegram'
                    : activeModal.connected ? 'Save' : 'Continue setup'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ChannelsPage;
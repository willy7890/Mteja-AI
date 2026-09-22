import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  MessageSquare,
  Sparkles,
  ArrowUpRight,
  Camera,
  Mail,
  PhoneCall,
  Zap,
  Loader2,
} from 'lucide-react';
import { apiGet } from '../api/Client';

function getGreeting(fullName) {
  const hour = new Date().getHours();
  let greeting = 'Good evening';

  if (hour >= 5 && hour < 12) {
    greeting = 'Good morning';
  } else if (hour >= 12 && hour < 17) {
    greeting = 'Good afternoon';
  }

  const firstName = fullName?.trim()?.split(/\s+/)[0] || 'there';
  return `${greeting}, ${firstName}`;
}

function DashboardPage({ t }) {
  const navigate = useNavigate();
  const [dateRange, setDateRange] = useState('30d');
  const [loading, setLoading] = useState(true);
  const [conversations, setConversations] = useState([]);
  const [stats, setStats] = useState(null);
  const [user, setUser] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    async function loadDashboard() {
      setLoading(true);
      setError('');

      try {
        const endDate = new Date();
        const startDate = new Date(endDate);
        startDate.setDate(endDate.getDate() - 30);
        const analyticsParams = new URLSearchParams({
          start_date: startDate.toISOString().slice(0, 10),
          end_date: endDate.toISOString().slice(0, 10),
        });
        const [userData, convData, statsData] = await Promise.all([
          apiGet('/api/v1/auth/me').catch(() => null),
          apiGet('/api/v1/conversations/conversations/').catch(() => []),
          apiGet(`/api/v1/analytics/overview?${analyticsParams}`).catch(() => null),
        ]);

        setUser(userData);
        setConversations(convData?.items || convData || []);
        setStats(statsData || null);
      } catch (err) {
        console.error(err);
        setError('Failed to load dashboard data');
        setConversations([]);
        setStats(null);
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, [dateRange]);

  const getChannelIcon = (ch) => {
    switch ((ch || '').toLowerCase()) {
      case 'whatsapp':
        return <MessageSquare size={14} color="#25D366" />;
      case 'instagram':
        return <Camera size={14} color="#E4405F" />;
      case 'email':
        return <Mail size={14} color="#4285F4" />;
      case 'call':
      case 'phone':
        return <PhoneCall size={14} color="#287A59" />;
      case 'telegram':
        return <MessageSquare size={14} color="#229ED9" />;
      default:
        return <MessageSquare size={14} color={t.accent} />;
    }
  };

  const rangeLabels = {
    today: 'Today',
    '7d': '7D',
    '30d': '30D',
    this_month: 'Month',
  };

  if (loading) {
    return (
      <div className="p-6 md:p-8 flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-3">
          <Loader2 size={28} className="animate-spin" style={{ color: t.accent }} />
          <p className="text-sm" style={{ color: t.muted }}>
            Loading dashboard...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 md:p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold" style={{ color: t.text }}>
            {getGreeting(user?.full_name || user?.name)}
          </h2>
          <p className="mt-1 text-sm" style={{ color: t.muted }}>
            Here's what's happening with your customers.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <div
            className="rounded-full p-1 flex items-center"
            style={{ background: t.card, border: `1px solid ${t.border}` }}
          >
            {['today', '7d', '30d', 'this_month'].map((range) => {
              const isSelected = dateRange === range;
              return (
                <button
                  key={range}
                  onClick={() => setDateRange(range)}
                  className="px-3 py-1 rounded-full text-xs font-semibold transition-colors"
                  style={{
                    background: isSelected ? t.accent : 'transparent',
                    color: isSelected ? t.accentText : t.muted,
                  }}
                >
                  {rangeLabels[range]}
                </button>
              );
            })}
          </div>

          <button
            onClick={() => navigate('/dashboard/inbox')}
            className="hidden sm:inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs font-medium transition-colors"
            style={{ background: t.accent, color: t.accentText }}
          >
            <Sparkles size={14} />
            <span>Open AI Inbox</span>
          </button>
        </div>
      </div>

      {error && (
        <div
          className="px-4 py-3 rounded-xl text-sm"
          style={{ background: 'rgba(229,72,77,0.1)', color: '#E5484D' }}
        >
          {error}
        </div>
      )}

      {/* Stats row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div
          className="p-6 rounded-2xl flex flex-col justify-between"
          style={{ background: t.card, border: `1px solid ${t.border}` }}
        >
          <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: t.muted }}>
            Total Conversations
          </span>
          <div className="flex items-baseline justify-between mt-4">
            <h3 className="text-3xl font-bold" style={{ color: t.text }}>
              {stats?.total_conversations ?? 0}
            </h3>
          </div>
        </div>

        <div
          className="p-6 rounded-2xl flex flex-col justify-between"
          style={{ background: t.card, border: `1px solid ${t.border}` }}
        >
          <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: t.muted }}>
            AI Replies Handled
          </span>
          <div className="flex items-baseline justify-between mt-4">
            <h3 className="text-3xl font-bold" style={{ color: t.accent }}>
              {stats?.ai_replies ?? 0}
            </h3>
          </div>
        </div>

        <div
          className="p-6 rounded-2xl flex flex-col justify-between"
          style={{ background: t.card, border: `1px solid ${t.border}` }}
        >
          <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: t.muted }}>
            Response Rate
          </span>
          <div className="flex items-baseline justify-between mt-4">
            <h3 className="text-3xl font-bold" style={{ color: t.text }}>
              {stats?.response_rate != null ? `${stats.response_rate}%` : '—'}
            </h3>
          </div>
        </div>

        <div className="p-6 rounded-2xl flex flex-col justify-between" style={{ background: t.accent }}>
          <span
            className="text-xs font-semibold uppercase tracking-wider"
            style={{ color: t.accentText, opacity: 0.75 }}
          >
            Revenue Influenced
          </span>
          <div className="flex items-baseline justify-between mt-4">
            <h3 className="text-3xl font-bold" style={{ color: t.accentText }}>
              {stats?.revenue != null ? `TZS ${stats.revenue}` : '—'}
            </h3>
          </div>
        </div>
      </div>

      {/* Recent conversations + AI efficiency */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div
          className="lg:col-span-2 rounded-2xl flex flex-col overflow-hidden"
          style={{ background: t.card, border: `1px solid ${t.border}` }}
        >
          <div
            className="p-5 flex justify-between items-center"
            style={{ borderBottom: `1px solid ${t.border}` }}
          >
            <div>
              <h3 className="font-semibold text-sm" style={{ color: t.text }}>
                Recent Conversations
              </h3>
              <p className="text-xs" style={{ color: t.muted }}>
                Live customer inquiries across all channels
              </p>
            </div>
            <button
              onClick={() => navigate('/dashboard/inbox')}
              className="text-xs font-medium hover:underline flex items-center gap-1"
              style={{ color: t.accent }}
            >
              View all <ArrowUpRight size={14} />
            </button>
          </div>

          <div className="overflow-y-auto max-h-[460px]">
            {conversations.length === 0 ? (
              <div className="p-10 text-center">
                <MessageSquare
                  size={32}
                  style={{ color: t.muted, margin: '0 auto 12px' }}
                />
                <p className="text-sm font-medium" style={{ color: t.text }}>
                  No conversations yet
                </p>
                <p className="text-xs mt-1" style={{ color: t.muted }}>
                  When customers message you on WhatsApp, Telegram, Instagram or
                  Email, they will appear here.
                </p>
              </div>
            ) : (
              conversations.slice(0, 8).map((conv) => (
                <div
                  key={conv.id}
                  onClick={() =>
                    navigate('/dashboard/inbox', {
                      state: { conversationId: conv.id },
                    })
                  }
                  className="flex items-center p-4 transition-colors cursor-pointer justify-between gap-4"
                  style={{ borderBottom: `1px solid ${t.border}` }}
                  onMouseEnter={(e) =>
                    (e.currentTarget.style.background = `${t.text}0D`)
                  }
                  onMouseLeave={(e) =>
                    (e.currentTarget.style.background = 'transparent')
                  }
                >
                  <div className="flex items-center gap-3.5 min-w-0">
                    <div className="relative flex-shrink-0">
                      <img
                        src={
                          conv.avatar ||
                          `https://ui-avatars.com/api/?name=${encodeURIComponent(
                            conv.customer_name || conv.customerName || 'C'
                          )}&background=2F6F4E&color=fff`
                        }
                        alt={conv.customer_name || conv.customerName || 'Customer'}
                        className="w-10 h-10 rounded-full object-cover"
                        style={{ border: `1px solid ${t.border}` }}
                      />
                      <div
                        className="absolute -bottom-1 -right-1 p-0.5 rounded-full"
                        style={{ background: t.card }}
                      >
                        {getChannelIcon(conv.channel)}
                      </div>
                    </div>

                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <span
                          className="text-xs font-bold truncate"
                          style={{ color: t.text }}
                        >
                          {conv.customer_name || conv.customerName || 'Unknown'}
                        </span>
                        <span
                          className="text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider"
                          style={{ background: t.surface, color: t.text }}
                        >
                          {conv.channel}
                        </span>
                        {(conv.unread || conv.unread_count > 0) && (
                          <span
                            className="w-2 h-2 rounded-full"
                            style={{ background: t.accent }}
                          />
                        )}
                      </div>
                      <p
                        className="text-xs truncate max-w-md mt-0.5"
                        style={{ color: t.muted }}
                      >
                        {conv.last_message || conv.lastMessage || '—'}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 flex-shrink-0 text-right">
                    <span
                      className="text-[9px] font-bold px-2 py-0.5 rounded-full"
                      style={
                        conv.is_ai_handled || conv.isAiHandled
                          ? { background: `${t.accent}1A`, color: t.accent }
                          : {
                              background: 'rgba(217,119,6,0.12)',
                              color: '#B45309',
                            }
                      }
                    >
                      {conv.is_ai_handled || conv.isAiHandled
                        ? 'AI Handled'
                        : 'Attention Needed'}
                    </span>
                    <span
                      className="text-xs font-medium min-w-[50px]"
                      style={{ color: t.muted }}
                    >
                      {conv.timestamp || conv.updated_at || ''}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* AI efficiency */}
        <div
          className="rounded-2xl p-6 flex flex-col justify-between"
          style={{ background: t.card, border: `1px solid ${t.border}` }}
        >
          <div>
            <div className="flex items-center justify-between mb-4">
              <span className="font-semibold text-sm" style={{ color: t.text }}>
                AI Agent Efficiency
              </span>
            </div>

            <div className="mt-6 space-y-4">
              {[
                {
                  label: 'AI Handled',
                  value: stats?.ai_handled_percent ?? 0,
                },
                {
                  label: 'Response Rate',
                  value: stats?.response_rate ?? 0,
                },
                {
                  label: 'Resolution Rate',
                  value: stats?.resolution_rate ?? 0,
                },
              ].map((row) => (
                <div key={row.label}>
                  <div className="flex justify-between text-xs mb-1.5 font-medium">
                    <span style={{ color: t.muted }}>{row.label}</span>
                    <span className="font-semibold" style={{ color: t.text }}>
                      {row.value}%
                    </span>
                  </div>
                  <div
                    className="w-full h-1.5 rounded-full overflow-hidden"
                    style={{ background: t.surface }}
                  >
                    <div
                      className="h-full"
                      style={{
                        width: `${Math.min(100, row.value)}%`,
                        background: t.accent,
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div
            className="p-4 rounded-xl mt-6"
            style={{ background: t.surface, border: `1px solid ${t.border}` }}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div
                  className="w-2 h-2 rounded-full animate-pulse"
                  style={{ background: t.accent }}
                />
                <span className="text-xs font-semibold" style={{ color: t.text }}>
                  Agent Status
                </span>
              </div>
              <button
                onClick={() => navigate('/dashboard/ai-agent')}
                className="text-[11px] font-bold hover:underline"
                style={{ color: t.accent }}
              >
                Config
              </button>
            </div>
            <p className="text-[11px] mt-1.5" style={{ color: t.muted }}>
              {conversations.length === 0
                ? 'Waiting for first conversations...'
                : 'Connected and ready'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default DashboardPage;
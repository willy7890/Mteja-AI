import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  MessageSquare,
  Sparkles,
  ArrowUpRight,
  Camera,
  Mail,
  PhoneCall,
  Zap,
} from 'lucide-react';


const MOCK_CONVERSATIONS = [
  { id: '1', avatar: 'https://ui-avatars.com/api/?name=Amina+K&background=2F6F4E&color=fff', customerName: 'Amina K.', channel: 'whatsapp', unread: true, lastMessage: 'Is the blue jacket still available?', isAiHandled: true, timestamp: '2m' },
  { id: '2', avatar: 'https://ui-avatars.com/api/?name=Juma+S&background=E1306C&color=fff', customerName: 'Juma S.', channel: 'instagram', unread: true, lastMessage: 'Can I pay on delivery?', isAiHandled: true, timestamp: '14m' },
  { id: '3', avatar: 'https://ui-avatars.com/api/?name=Grace+M&background=4285F4&color=fff', customerName: 'Grace M.', channel: 'email', unread: false, lastMessage: 'Thank you! Order received.', isAiHandled: false, timestamp: '1h' },
  { id: '4', avatar: 'https://ui-avatars.com/api/?name=David+M&background=287A59&color=fff', customerName: 'David M.', channel: 'call', unread: false, lastMessage: 'Missed call — no voicemail', isAiHandled: false, timestamp: '3h' },
];

function DashboardPage({ t, conversations, recentConversations }) {
  const navigate = useNavigate();
  const convList = recentConversations || conversations || MOCK_CONVERSATIONS;
  const [dateRange, setDateRange] = useState('30d');

  const metrics = {
    today: { total: '84', aiReplies: '71', responseRate: '99.1%', sales: 'TZS 620,000', totalChange: '+12.5%', aiPercent: '84.5% OF TOTAL', rateWidth: '99%', salesChange: '+TZS 180K' },
    '7d': { total: '412', aiReplies: '348', responseRate: '98.8%', sales: 'TZS 1.65M', totalChange: '+15.2%', aiPercent: '84.4% OF TOTAL', rateWidth: '98%', salesChange: '+TZS 450K' },
    '30d': { total: '1,284', aiReplies: '946', responseRate: '98.4%', sales: 'TZS 4.8M', totalChange: '+18.4%', aiPercent: '73% OF TOTAL', rateWidth: '98%', salesChange: '+TZS 1.2M' },
    this_month: { total: '920', aiReplies: '710', responseRate: '98.6%', sales: 'TZS 3.4M', totalChange: '+17.0%', aiPercent: '77.1% OF TOTAL', rateWidth: '98%', salesChange: '+TZS 850K' },
  }[dateRange];

  const chartDays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const incomingData = [45, 62, 58, 80, 72, 94, 110];
  const aiRepliesData = [38, 54, 49, 68, 62, 81, 96];
  const maxVal = 120;
  const getY = (val) => 140 - (val / maxVal) * 110;
  const incomingPoints = incomingData.map((d, i) => `${30 + i * 65},${getY(d)}`).join(' ');
  const aiPoints = aiRepliesData.map((d, i) => `${30 + i * 65},${getY(d)}`).join(' ');

 
  const getChannelIcon = (ch) => {
    switch (ch) {
      case 'whatsapp': return <MessageSquare size={14} color="#25D366" />;
      case 'instagram': return <Instagram size={14} color="#E4405F" />;
      case 'email': return <Mail size={14} color="#4285F4" />;
      case 'call': return <PhoneCall size={14} color="#287A59" />;
      default: return <MessageSquare size={14} color={t.accent} />;
    }
  };

  const rangeLabels = { today: 'Today', '7d': '7D', '30d': '30D', this_month: 'Month' };

  return (
    <div className="p-6 md:p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold" style={{ color: t.text }}>
            Good morning, Zawadi Emporium
          </h2>
          <p className="mt-1 text-sm" style={{ color: t.muted }}>
            Here's what's happening with your customers today.
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

      {/* Stats row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="p-6 rounded-2xl flex flex-col justify-between" style={{ background: t.card, border: `1px solid ${t.border}` }}>
          <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: t.muted }}>Total Conversations</span>
          <div className="flex items-baseline justify-between mt-4">
            <h3 className="text-3xl font-bold" style={{ color: t.text }}>{metrics.total}</h3>
            <span className="text-xs font-semibold px-2 py-1 rounded" style={{ background: `${t.accent}1A`, color: t.accent }}>{metrics.totalChange}</span>
          </div>
        </div>

        <div className="p-6 rounded-2xl flex flex-col justify-between" style={{ background: t.card, border: `1px solid ${t.border}` }}>
          <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: t.muted }}>AI Replies Handled</span>
          <div className="flex items-baseline justify-between mt-4">
            <h3 className="text-3xl font-bold" style={{ color: t.accent }}>{metrics.aiReplies}</h3>
            <span className="text-[10px] font-semibold uppercase tracking-wider" style={{ color: t.muted }}>{metrics.aiPercent}</span>
          </div>
        </div>

        <div className="p-6 rounded-2xl flex flex-col justify-between" style={{ background: t.card, border: `1px solid ${t.border}` }}>
          <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: t.muted }}>Response Rate</span>
          <div className="flex items-baseline justify-between mt-4">
            <h3 className="text-3xl font-bold" style={{ color: t.text }}>{metrics.responseRate}</h3>
            <div className="w-16 h-1.5 rounded-full mb-2 overflow-hidden" style={{ background: t.surface }}>
              <div className="h-full" style={{ width: metrics.rateWidth, background: t.accent }} />
            </div>
          </div>
        </div>

        {/* Emphasis card — reuses the same accent-fill treatment as your
            FinalCta banner, so "important number" reads consistently
            across the whole site, not just this one dashboard card. */}
        <div className="p-6 rounded-2xl flex flex-col justify-between" style={{ background: t.accent }}>
          <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: t.accentText, opacity: 0.75 }}>Revenue Influenced</span>
          <div className="flex items-baseline justify-between mt-4">
            <h3 className="text-3xl font-bold" style={{ color: t.accentText }}>{metrics.sales}</h3>
            <span className="text-xs font-semibold" style={{ color: t.accentText }}>{metrics.salesChange}</span>
          </div>
        </div>
      </div>

      {/* Recent conversations + AI efficiency */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 rounded-2xl flex flex-col overflow-hidden" style={{ background: t.card, border: `1px solid ${t.border}` }}>
          <div className="p-5 flex justify-between items-center" style={{ borderBottom: `1px solid ${t.border}` }}>
            <div>
              <h3 className="font-semibold text-sm" style={{ color: t.text }}>Recent Conversations</h3>
              <p className="text-xs" style={{ color: t.muted }}>Live customer inquiries across WhatsApp, Instagram, Email, & Calls</p>
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
            {convList.slice(0, 6).map((conv) => (
              <div
                key={conv.id}
                onClick={() => navigate('/dashboard/inbox', { state: { conversationId: conv.id } })}
                className="flex items-center p-4 transition-colors cursor-pointer justify-between gap-4"
                style={{ borderBottom: `1px solid ${t.border}` }}
                onMouseEnter={(e) => (e.currentTarget.style.background = `${t.text}0D`)}
                onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
              >
                <div className="flex items-center gap-3.5 min-w-0">
                  <div className="relative flex-shrink-0">
                    <img
                      src={conv.avatar}
                      alt={conv.customerName}
                      className="w-10 h-10 rounded-full object-cover"
                      style={{ border: `1px solid ${t.border}` }}
                    />
                    <div className="absolute -bottom-1 -right-1 p-0.5 rounded-full" style={{ background: t.card }}>
                      {getChannelIcon(conv.channel)}
                    </div>
                  </div>

                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold truncate" style={{ color: t.text }}>{conv.customerName}</span>
                      <span
                        className="text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider"
                        style={{ background: t.surface, color: t.text }}
                      >
                        {conv.channel}
                      </span>
                      {conv.unread && <span className="w-2 h-2 rounded-full" style={{ background: t.accent }} />}
                    </div>
                    <p className="text-xs truncate max-w-md mt-0.5" style={{ color: t.muted }}>{conv.lastMessage}</p>
                  </div>
                </div>

                <div className="flex items-center gap-3 flex-shrink-0 text-right">
                  <span
                    className="text-[9px] font-bold px-2 py-0.5 rounded-full"
                    style={
                      conv.isAiHandled
                        ? { background: `${t.accent}1A`, color: t.accent }
                        : { background: 'rgba(217,119,6,0.12)', color: '#B45309' }
                    }
                  >
                    {conv.isAiHandled ? 'AI Handled' : 'Attention Needed'}
                  </span>
                  <span className="text-xs font-medium min-w-[50px]" style={{ color: t.muted }}>{conv.timestamp}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-2xl p-6 flex flex-col justify-between" style={{ background: t.card, border: `1px solid ${t.border}` }}>
          <div>
            <div className="flex items-center justify-between mb-4">
              <span className="font-semibold text-sm" style={{ color: t.text }}>AI Agent Efficiency</span>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full" style={{ background: `${t.accent}1A`, color: t.accent }}>Optimal</span>
            </div>

            <div className="mt-6 space-y-4">
              {[
                { label: 'Swahili Intent Accuracy', value: 94 },
                { label: 'English Support', value: 98 },
                { label: 'Autonomous Resolution', value: 88.2 },
              ].map((row) => (
                <div key={row.label}>
                  <div className="flex justify-between text-xs mb-1.5 font-medium">
                    <span style={{ color: t.muted }}>{row.label}</span>
                    <span className="font-semibold" style={{ color: t.text }}>{row.value}%</span>
                  </div>
                  <div className="w-full h-1.5 rounded-full overflow-hidden" style={{ background: t.surface }}>
                    <div className="h-full" style={{ width: `${row.value}%`, background: t.accent }} />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="p-4 rounded-xl mt-6" style={{ background: t.surface, border: `1px solid ${t.border}` }}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full animate-pulse" style={{ background: t.accent }} />
                <span className="text-xs font-semibold" style={{ color: t.text }}>Agent Training: Active</span>
              </div>
              <button onClick={() => navigate('/dashboard/ai-agent')} className="text-[11px] font-bold hover:underline" style={{ color: t.accent }}>
                Config
              </button>
            </div>
            <p className="text-[11px] mt-1.5" style={{ color: t.muted }}>
              Trained on Kariakoo price catalog, delivery matrices & FAQ
            </p>
          </div>
        </div>
      </div>

      {/* Conversation activity chart + leads funnel */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 p-6 rounded-2xl" style={{ background: t.card, border: `1px solid ${t.border}` }}>
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold tracking-tight" style={{ color: t.text }}>Conversation Activity</h3>
              <p className="text-xs" style={{ color: t.muted }}>Incoming inquiries vs. instant AI responses over the past 7 days</p>
            </div>
            <div className="flex items-center gap-4 text-xs font-medium">
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full" style={{ background: t.text }} />
                <span style={{ color: t.muted }}>Incoming (481)</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full" style={{ background: t.accent }} />
                <span className="font-semibold" style={{ color: t.text }}>AI Handled (398)</span>
              </div>
            </div>
          </div>

          <div className="relative w-full h-44">
            <svg viewBox="0 0 450 160" className="w-full h-full overflow-visible">
              <line x1="20" y1="30" x2="440" y2="30" stroke={t.border} strokeWidth="1" strokeDasharray="3 3" />
              <line x1="20" y1="75" x2="440" y2="75" stroke={t.border} strokeWidth="1" strokeDasharray="3 3" />
              <line x1="20" y1="120" x2="440" y2="120" stroke={t.border} strokeWidth="1" />
              <polygon points={`30,140 ${aiPoints} 420,140`} fill={`${t.accent}14`} />
              <polyline fill="none" stroke={t.text} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" points={incomingPoints} />
              <polyline fill="none" stroke={t.accent} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" points={aiPoints} />
              {incomingData.map((d, i) => (
                <circle key={`inc-${i}`} cx={30 + i * 65} cy={getY(d)} r="3.5" fill={t.card} stroke={t.text} strokeWidth="2" />
              ))}
              {aiRepliesData.map((d, i) => (
                <circle key={`ai-${i}`} cx={30 + i * 65} cy={getY(d)} r="3.5" fill={t.card} stroke={t.accent} strokeWidth="2" />
              ))}
              {chartDays.map((day, i) => (
                <text key={day} x={30 + i * 65} y="155" textAnchor="middle" fontSize="11" fill={t.muted}>{day}</text>
              ))}
            </svg>
          </div>

          <div className="mt-4 pt-3 flex items-center justify-between text-xs" style={{ borderTop: `1px solid ${t.border}`, color: t.muted }}>
            <span>Peak activity occurs between <b>11:00 AM – 2:30 PM EAT</b></span>
            <button onClick={() => navigate('/dashboard/analytics')} className="font-bold hover:underline flex items-center gap-1" style={{ color: t.accent }}>
              Detailed Analytics <ArrowUpRight size={12} />
            </button>
          </div>
        </div>

        <div className="p-6 rounded-2xl flex flex-col justify-between" style={{ background: t.card, border: `1px solid ${t.border}` }}>
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-bold tracking-tight" style={{ color: t.text }}>Leads Conversion Funnel</h3>
              <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full" style={{ background: `${t.accent}1A`, color: t.accent }}>42.8%</span>
            </div>
            <p className="text-xs mb-4" style={{ color: t.muted }}>How inquiries progress into recorded purchases</p>

            <div className="space-y-3">
              {[
                { label: 'New conversations', value: '1,284 (100%)', width: '100%', color: t.text },
                { label: 'Qualified leads', value: '612 (47.6%)', width: '47.6%', color: t.accent },
                { label: 'Interested customers', value: '298 (23.2%)', width: '23.2%', color: `${t.accent}99` },
                { label: 'Converted customers', value: '127 (9.8%)', width: '9.8%', color: t.accent },
              ].map((row) => (
                <div key={row.label}>
                  <div className="flex justify-between text-xs font-semibold mb-1">
                    <span style={{ color: t.text }}>{row.label}</span>
                    <span style={{ color: t.text }}>{row.value}</span>
                  </div>
                  <div className="w-full h-2 rounded-full overflow-hidden" style={{ background: t.surface }}>
                    <div className="h-full rounded-full" style={{ width: row.width, background: row.color }} />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-4 pt-3 flex items-center justify-between text-xs" style={{ borderTop: `1px solid ${t.border}`, color: t.muted }}>
            <span>Avg deal size: <b>TZS 37,800</b></span>
            <button onClick={() => navigate('/dashboard/customers')} className="font-bold hover:underline" style={{ color: t.accent }}>
              View CRM Leads
            </button>
          </div>
        </div>
      </div>

      {/* Channel performance + AI health */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="p-6 rounded-2xl" style={{ background: t.card, border: `1px solid ${t.border}` }}>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-bold tracking-tight" style={{ color: t.text }}>Channel Performance</h3>
            <button onClick={() => navigate('/dashboard/channels')} className="text-xs font-semibold hover:underline" style={{ color: t.accent }}>Manage</button>
          </div>
          <p className="text-xs mb-4" style={{ color: t.muted }}>Volume and response rates across connected platforms</p>

          <div className="space-y-3.5">
            {[
              { icon: <MessageSquare size={16} color="#25D366" />, bg: 'rgba(37,211,102,0.1)', name: 'WhatsApp Business', sub: '892 chats · 99.2% rate', pct: '69.5%' },
              { icon: <Instagram size={16} color="#E4405F" />, bg: 'rgba(228,64,95,0.1)', name: 'Instagram Direct', sub: '244 chats · 97.4% rate', pct: '19.0%' },
              { icon: <Mail size={16} color="#4285F4" />, bg: 'rgba(66,133,244,0.1)', name: 'Corporate Email', sub: '86 threads · 96.1% rate', pct: '6.7%' },
              { icon: <PhoneCall size={16} color="#287A59" />, bg: 'rgba(40,122,89,0.1)', name: 'Phone & Voice', sub: '62 calls · 100% transcribed', pct: '4.8%' },
            ].map((row) => (
              <div key={row.name} className="p-3 rounded-xl flex items-center justify-between" style={{ background: t.surface, border: `1px solid ${t.border}` }}>
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: row.bg }}>{row.icon}</div>
                  <div>
                    <h4 className="text-xs font-bold" style={{ color: t.text }}>{row.name}</h4>
                    <p className="text-[11px]" style={{ color: t.muted }}>{row.sub}</p>
                  </div>
                </div>
                <span className="text-xs font-extrabold" style={{ color: t.accent }}>{row.pct}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="lg:col-span-2 p-6 rounded-2xl flex flex-col justify-between" style={{ background: t.card, border: `1px solid ${t.border}` }}>
          <div>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg flex items-center justify-center" style={{ background: `${t.accent}1A` }}>
                  <Zap size={16} color={t.accent} />
                </div>
                <h3 className="text-sm font-bold tracking-tight" style={{ color: t.text }}>AI Agent Performance & Health</h3>
              </div>
              <span className="text-xs font-semibold px-2.5 py-1 rounded-full" style={{ background: `${t.accent}1A`, color: t.text }}>Autonomous Level: High</span>
            </div>
            <p className="text-xs mb-6" style={{ color: t.muted }}>Real-time resolution analytics and human handoff telemetry</p>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              {[
                { label: 'AI Handled', value: '82.4%', sub: 'Autonomous' },
                { label: 'Avg Response Time', value: '1.4s', sub: 'Sub-second peak' },
                { label: 'Resolution Rate', value: '88.2%', sub: 'No human needed' },
                { label: 'Escalation Rate', value: '11.8%', sub: 'High-value quotes' },
              ].map((box) => (
                <div key={box.label} className="p-4 rounded-xl" style={{ background: t.surface, border: `1px solid ${t.border}` }}>
                  <p className="text-xs" style={{ color: t.muted }}>{box.label}</p>
                  <p className="text-2xl font-bold mt-1" style={{ color: t.text }}>{box.value}</p>
                  <p className="text-[11px] font-semibold mt-1" style={{ color: t.accent }}>{box.sub}</p>
                </div>
              ))}
            </div>

            <div className="mt-6 p-4 rounded-xl flex items-center justify-between" style={{ background: `${t.accent}0D`, border: `1px solid ${t.accent}33` }}>
              <div>
                <h4 className="text-xs font-bold" style={{ color: t.text }}>Trained on Zawadi Emporium Swahili & English FAQs</h4>
                <p className="text-[11px] mt-0.5" style={{ color: t.muted }}>142 knowledge items active · Kariakoo, Mikocheni & Masaki delivery matrices loaded</p>
              </div>
              <button onClick={() => navigate('/dashboard/ai-agent')} className="px-3 py-1.5 rounded-lg text-xs font-bold transition-colors" style={{ background: t.accent, color: t.accentText }}>
                Configure AI
              </button>
            </div>
          </div>

          <div className="mt-4 pt-3 flex items-center justify-between text-xs" style={{ borderTop: `1px solid ${t.border}`, color: t.muted }}>
            <span>Last trained: <b>Today at 07:15 AM EAT</b></span>
            <span className="font-bold" style={{ color: t.accent }}>Zero downtime in 90 days</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default DashboardPage;
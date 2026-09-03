import React, { useState } from 'react';
import {
  MessageSquare,
  Sparkles,
  TrendingUp,
  ArrowUpRight,
  Clock,
  CheckCircle2,
  DollarSign,
  Users,
  Instagram,
  Mail,
  PhoneCall,
  ChevronDown,
  ExternalLink,
  ShieldCheck,
  Zap,
  Filter,
  Calendar
} from 'lucide-react';
import { Conversation, PageId } from '../../types';

interface DashboardPageProps {
  conversations?: Conversation[];
  recentConversations?: Conversation[];
  kpi?: any;
  channels?: any[];
  onNavigate: (page: PageId) => void;
  onSelectConversation: (convId: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  conversations,
  recentConversations,
  onNavigate,
  onSelectConversation,
}) => {
  const convList = recentConversations || conversations || [];
  const [dateRange, setDateRange] = useState<'today' | '7d' | '30d' | 'this_month'>('30d');

  // Interactive mock metrics that adjust gracefully with date range
  const metrics = {
    today: {
      total: '84',
      aiReplies: '71',
      responseRate: '99.1%',
      leads: '14',
      sales: 'TZS 620,000',
      totalChange: '+12.5%',
      aiPercent: '84.5% OF TOTAL',
      rateWidth: '99%',
      salesChange: '+TZS 180K',
    },
    '7d': {
      total: '412',
      aiReplies: '348',
      responseRate: '98.8%',
      leads: '42',
      sales: 'TZS 1.65M',
      totalChange: '+15.2%',
      aiPercent: '84.4% OF TOTAL',
      rateWidth: '98%',
      salesChange: '+TZS 450K',
    },
    '30d': {
      total: '1,284',
      aiReplies: '946',
      responseRate: '98.4%',
      leads: '127',
      sales: 'TZS 4.8M',
      totalChange: '+18.4%',
      aiPercent: '73% OF TOTAL',
      rateWidth: '98%',
      salesChange: '+TZS 1.2M',
    },
    this_month: {
      total: '920',
      aiReplies: '710',
      responseRate: '98.6%',
      leads: '89',
      sales: 'TZS 3.4M',
      totalChange: '+17.0%',
      aiPercent: '77.1% OF TOTAL',
      rateWidth: '98%',
      salesChange: '+TZS 850K',
    }
  }[dateRange];

  // SVG Line Chart points for Conversation Activity (Incoming vs AI Replies)
  const chartDays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const incomingData = [45, 62, 58, 80, 72, 94, 110];
  const aiRepliesData = [38, 54, 49, 68, 62, 81, 96];

  const maxVal = 120;
  const getY = (val: number) => 140 - (val / maxVal) * 110;

  const incomingPoints = incomingData.map((d, i) => `${30 + i * 65},${getY(d)}`).join(' ');
  const aiPoints = aiRepliesData.map((d, i) => `${30 + i * 65},${getY(d)}`).join(' ');

  const getChannelIcon = (ch: string) => {
    switch (ch) {
      case 'whatsapp': return <MessageSquare className="w-3.5 h-3.5 text-[#25D366]" />;
      case 'instagram': return <Instagram className="w-3.5 h-3.5 text-[#E4405F]" />;
      case 'email': return <Mail className="w-3.5 h-3.5 text-[#4285F4]" />;
      case 'call': return <PhoneCall className="w-3.5 h-3.5 text-[#287A59]" />;
      default: return <MessageSquare className="w-3.5 h-3.5 text-[#287A59]" />;
    }
  };

  return (
    <div className="p-6 md:p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header Greeting & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-[#10231C]">
            Good morning, Zawadi Emporium
          </h2>
          <p className="text-[#68756F] mt-1 text-sm">
            Here’s what’s happening with your customers today.
          </p>
        </div>

        {/* Date range selector */}
        <div className="flex items-center gap-2">
          <div className="bg-white border border-[#E2E4DF] rounded-full p-1 flex items-center shadow-2xs">
            {(['today', '7d', '30d', 'this_month'] as const).map((range) => {
              const labels = {
                today: 'Today',
                '7d': '7D',
                '30d': '30D',
                this_month: 'Month',
              };
              const isSelected = dateRange === range;
              return (
                <button
                  key={range}
                  onClick={() => setDateRange(range)}
                  className={`px-3 py-1 rounded-full text-xs font-semibold transition-all cursor-pointer ${
                    isSelected
                      ? 'bg-[#10231C] text-white shadow-xs'
                      : 'text-[#68756F] hover:text-[#10231C]'
                  }`}
                >
                  {labels[range]}
                </button>
              );
            })}
          </div>

          <button
            onClick={() => onNavigate('inbox')}
            className="hidden sm:inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#287A59] hover:bg-[#10231C] text-white text-xs font-medium transition-colors shadow-2xs cursor-pointer"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Open AI Inbox</span>
          </button>
        </div>
      </div>

      {/* STATS ROW: 4 Geometric Balance Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Card 1: Total Conversations */}
        <div className="bg-white p-6 rounded-2xl border border-[#E2E4DF] flex flex-col justify-between shadow-2xs">
          <span className="text-xs font-semibold text-[#68756F] uppercase tracking-wider">
            Total Conversations
          </span>
          <div className="flex items-baseline justify-between mt-4">
            <h3 className="text-3xl font-bold text-[#10231C]">{metrics.total}</h3>
            <span className="text-xs text-[#287A59] font-semibold bg-[#287A59]/10 px-2 py-1 rounded">
              {metrics.totalChange}
            </span>
          </div>
        </div>

        {/* Card 2: AI Replies Handled */}
        <div className="bg-white p-6 rounded-2xl border border-[#E2E4DF] flex flex-col justify-between shadow-2xs">
          <span className="text-xs font-semibold text-[#68756F] uppercase tracking-wider">
            AI Replies Handled
          </span>
          <div className="flex items-baseline justify-between mt-4">
            <h3 className="text-3xl font-bold text-[#287A59]">{metrics.aiReplies}</h3>
            <span className="text-[10px] text-[#68756F] font-semibold uppercase tracking-wider">
              {metrics.aiPercent}
            </span>
          </div>
        </div>

        {/* Card 3: Response Rate */}
        <div className="bg-white p-6 rounded-2xl border border-[#E2E4DF] flex flex-col justify-between shadow-2xs">
          <span className="text-xs font-semibold text-[#68756F] uppercase tracking-wider">
            Response Rate
          </span>
          <div className="flex items-baseline justify-between mt-4">
            <h3 className="text-3xl font-bold text-[#10231C]">{metrics.responseRate}</h3>
            <div className="w-16 h-1.5 bg-[#F7F6F1] rounded-full mb-2 overflow-hidden">
              <div className="bg-[#35D98A] h-full" style={{ width: metrics.rateWidth }} />
            </div>
          </div>
        </div>

        {/* Card 4: Revenue Influenced (Hero Dark Contrast) */}
        <div className="bg-[#10231C] p-6 rounded-2xl flex flex-col justify-between shadow-xs">
          <span className="text-xs font-semibold text-[#9EA7A2] uppercase tracking-wider">
            Revenue Influenced
          </span>
          <div className="flex items-baseline justify-between mt-4">
            <h3 className="text-3xl font-bold text-white">{metrics.sales}</h3>
            <span className="text-xs text-[#35D98A] font-semibold">
              {metrics.salesChange}
            </span>
          </div>
        </div>
      </div>

      {/* MAIN CONTENT GRID: 3 Columns (Geometric Balance) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Recent Conversations / Live Feed */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-[#E2E4DF] flex flex-col overflow-hidden shadow-2xs">
          <div className="p-5 border-b border-[#E2E4DF] flex justify-between items-center">
            <div>
              <h3 className="font-semibold text-sm text-[#10231C]">Recent Conversations</h3>
              <p className="text-xs text-[#68756F]">Live customer inquiries across WhatsApp, Instagram, Email, & Calls</p>
            </div>
            <button
              onClick={() => onNavigate('inbox')}
              className="text-xs text-[#287A59] font-medium hover:underline flex items-center gap-1 cursor-pointer"
            >
              View all <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="divide-y divide-[#E2E4DF]/60 overflow-y-auto max-h-[460px]">
            {convList.slice(0, 6).map((conv) => (
              <div
                key={conv.id}
                onClick={() => {
                  onSelectConversation(conv.id);
                  onNavigate('inbox');
                }}
                className="flex items-center p-4 hover:bg-[#F7F6F1] transition-colors cursor-pointer justify-between gap-4 group"
              >
                <div className="flex items-center gap-3.5 min-w-0">
                  <div className="relative flex-shrink-0">
                    <img
                      src={conv.avatar}
                      alt={conv.customerName}
                      className="w-10 h-10 rounded-full object-cover border border-[#E2E4DF]"
                    />
                    <div className="absolute -bottom-1 -right-1 p-0.5 bg-white rounded-full shadow-2xs">
                      {getChannelIcon(conv.channel)}
                    </div>
                  </div>

                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-[#10231C] group-hover:text-[#287A59] transition-colors truncate">
                        {conv.customerName}
                      </span>
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#E2E4DF] text-[#14201B] uppercase tracking-wider">
                        {conv.channel}
                      </span>
                      {conv.unread && (
                        <span className="w-2 h-2 rounded-full bg-[#287A59]" />
                      )}
                    </div>
                    <p className="text-xs text-[#68756F] truncate max-w-md mt-0.5">
                      {conv.lastMessage}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3 flex-shrink-0 text-right">
                  <span
                    className={`text-[9px] font-bold px-2 py-0.5 rounded-full ${
                      conv.isAiHandled
                        ? 'bg-[#287A59]/10 text-[#287A59]'
                        : 'bg-amber-500/10 text-amber-700'
                    }`}
                  >
                    {conv.isAiHandled ? 'AI Handled' : 'Attention Needed'}
                  </span>
                  <span className="text-xs text-[#68756F] font-medium min-w-[50px]">
                    {conv.timestamp}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right 1 Col: AI Agent Efficiency (Geometric Balance Theme) */}
        <div className="bg-white rounded-2xl border border-[#E2E4DF] p-6 flex flex-col justify-between shadow-2xs">
          <div>
            <div className="flex items-center justify-between mb-4">
              <span className="font-semibold text-sm text-[#10231C]">AI Agent Efficiency</span>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#35D98A]/20 text-[#10231C]">
                Optimal
              </span>
            </div>

            <div className="mt-6 space-y-4">
              <div>
                <div className="flex justify-between text-xs mb-1.5 font-medium">
                  <span className="text-[#68756F]">Swahili Intent Accuracy</span>
                  <span className="font-semibold text-[#10231C]">94%</span>
                </div>
                <div className="w-full h-1.5 bg-[#F7F6F1] rounded-full overflow-hidden">
                  <div className="bg-[#287A59] h-full w-[94%]" />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs mb-1.5 font-medium">
                  <span className="text-[#68756F]">English Support</span>
                  <span className="font-semibold text-[#10231C]">98%</span>
                </div>
                <div className="w-full h-1.5 bg-[#F7F6F1] rounded-full overflow-hidden">
                  <div className="bg-[#287A59] h-full w-[98%]" />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs mb-1.5 font-medium">
                  <span className="text-[#68756F]">Avg. Response Delay</span>
                  <span className="font-semibold text-[#10231C]">1.4s</span>
                </div>
                <div className="w-full h-1.5 bg-[#F7F6F1] rounded-full overflow-hidden">
                  <div className="bg-[#35D98A] h-full w-[85%]" />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs mb-1.5 font-medium">
                  <span className="text-[#68756F]">Autonomous Resolution</span>
                  <span className="font-semibold text-[#10231C]">88.2%</span>
                </div>
                <div className="w-full h-1.5 bg-[#F7F6F1] rounded-full overflow-hidden">
                  <div className="bg-[#287A59] h-full w-[88%]" />
                </div>
              </div>
            </div>
          </div>

          <div className="bg-[#F7F6F1] p-4 rounded-xl border border-[#E2E4DF] mt-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-[#35D98A] animate-pulse" />
                <span className="text-xs font-semibold text-[#10231C]">Agent Training: Active</span>
              </div>
              <button
                onClick={() => onNavigate('ai-agent')}
                className="text-[11px] font-bold text-[#287A59] hover:underline cursor-pointer"
              >
                Config
              </button>
            </div>
            <p className="text-[11px] text-[#68756F] mt-1.5">
              Trained on Kariakoo price catalog, delivery matrices & FAQ
            </p>
          </div>
        </div>
      </div>

      {/* Grid: 1. Conversation Activity + 2. Leads Funnel */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Section 1: Conversation Activity (SVG Line Chart) */}
        <div className="lg:col-span-2 bg-white p-6 rounded-2xl border border-[#E2E4DF] shadow-2xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-[#10231C] tracking-tight">Conversation Activity</h3>
              <p className="text-xs text-[#68756F]">Incoming inquiries vs. instant AI responses over the past 7 days</p>
            </div>
            <div className="flex items-center gap-4 text-xs font-medium">
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-[#10231C]" />
                <span className="text-[#68756F]">Incoming (481)</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-[#287A59]" />
                <span className="text-[#10231C] font-semibold">AI Handled (398)</span>
              </div>
            </div>
          </div>

          {/* Line Chart Canvas Area */}
          <div className="relative w-full h-44">
            <svg viewBox="0 0 450 160" className="w-full h-full overflow-visible">
              {/* Subtle Grid lines */}
              <line x1="20" y1="30" x2="440" y2="30" stroke="#F1F3EE" strokeWidth="1" strokeDasharray="3 3" />
              <line x1="20" y1="75" x2="440" y2="75" stroke="#F1F3EE" strokeWidth="1" strokeDasharray="3 3" />
              <line x1="20" y1="120" x2="440" y2="120" stroke="#F1F3EE" strokeWidth="1" />

              {/* Area under AI Curve */}
              <polygon
                points={`30,140 ${aiPoints} 420,140`}
                fill="rgba(40, 122, 89, 0.08)"
              />

              {/* Incoming conversations line */}
              <polyline
                fill="none"
                stroke="#10231C"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
                points={incomingPoints}
              />

              {/* AI replies line */}
              <polyline
                fill="none"
                stroke="#287A59"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
                points={aiPoints}
              />

              {/* Data points */}
              {incomingData.map((d, i) => (
                <circle
                  key={`inc-${i}`}
                  cx={30 + i * 65}
                  cy={getY(d)}
                  r="3.5"
                  className="fill-white stroke-[#10231C] stroke-2 hover:r-5 transition-all cursor-pointer"
                />
              ))}
              {aiRepliesData.map((d, i) => (
                <circle
                  key={`ai-${i}`}
                  cx={30 + i * 65}
                  cy={getY(d)}
                  r="3.5"
                  className="fill-white stroke-[#287A59] stroke-2 hover:r-5 transition-all cursor-pointer"
                />
              ))}

              {/* X Axis Labels */}
              {chartDays.map((day, i) => (
                <text
                  key={day}
                  x={30 + i * 65}
                  y="155"
                  textAnchor="middle"
                  className="text-[11px] fill-[#68756F] font-medium"
                >
                  {day}
                </text>
              ))}
            </svg>
          </div>

          <div className="mt-4 pt-3 border-t border-[#E2E4DF] flex items-center justify-between text-xs text-[#68756F]">
            <span>Peak activity occurs between <b>11:00 AM – 2:30 PM EAT</b> (Dar es Salaam lunch hours)</span>
            <button onClick={() => onNavigate('analytics')} className="text-[#287A59] font-bold hover:underline flex items-center gap-1">
              Detailed Analytics <ArrowUpRight className="w-3 h-3" />
            </button>
          </div>
        </div>

        {/* Section 2: Leads Funnel */}
        <div className="bg-white p-6 rounded-2xl border border-[#E2E4DF] shadow-2xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-bold text-[#10231C] tracking-tight">Leads Conversion Funnel</h3>
              <span className="text-[11px] font-semibold text-[#287A59] bg-[#287A59]/10 px-2 py-0.5 rounded-full">
                42.8% Conversion
              </span>
            </div>
            <p className="text-xs text-[#68756F] mb-4">How customer inquiries progress into recorded purchases</p>

            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-xs font-semibold mb-1">
                  <span className="text-[#14201B]">New conversations</span>
                  <span className="text-[#10231C]">1,284 (100%)</span>
                </div>
                <div className="w-full h-2 bg-[#F7F6F1] rounded-full overflow-hidden">
                  <div className="h-full bg-[#10231C] rounded-full" style={{ width: '100%' }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs font-semibold mb-1">
                  <span className="text-[#14201B]">Qualified leads</span>
                  <span className="text-[#10231C]">612 (47.6%)</span>
                </div>
                <div className="w-full h-2 bg-[#F7F6F1] rounded-full overflow-hidden">
                  <div className="h-full bg-[#287A59] rounded-full" style={{ width: '47.6%' }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs font-semibold mb-1">
                  <span className="text-[#14201B]">Interested customers</span>
                  <span className="text-[#10231C]">298 (23.2%)</span>
                </div>
                <div className="w-full h-2 bg-[#F7F6F1] rounded-full overflow-hidden">
                  <div className="h-full bg-[#35D98A] rounded-full" style={{ width: '23.2%' }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs font-semibold mb-1">
                  <span className="text-[#14201B]">Converted customers</span>
                  <span className="text-[#287A59] font-bold">127 (9.8%)</span>
                </div>
                <div className="w-full h-2 bg-[#F7F6F1] rounded-full overflow-hidden">
                  <div className="h-full bg-[#287A59] rounded-full" style={{ width: '9.8%' }} />
                </div>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-[#E2E4DF] flex items-center justify-between text-xs">
            <span className="text-[#68756F]">Avg deal size: <b>TZS 37,800</b></span>
            <button onClick={() => onNavigate('customers')} className="text-[#287A59] font-bold hover:underline">
              View CRM Leads
            </button>
          </div>
        </div>
      </div>

      {/* Grid: 3. Channel Performance + 5. AI Performance */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Section 3: Channel Performance */}
        <div className="bg-white p-6 rounded-2xl border border-[#E2E4DF] shadow-2xs">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-bold text-[#10231C] tracking-tight">Channel Performance</h3>
            <button onClick={() => onNavigate('channels')} className="text-xs text-[#287A59] font-semibold hover:underline">
              Manage
            </button>
          </div>
          <p className="text-xs text-[#68756F] mb-4">Volume and response rates across connected platforms</p>

          <div className="space-y-3.5">
            {/* WhatsApp */}
            <div className="p-3 rounded-xl bg-[#F7F6F1] border border-[#E2E4DF] flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-[#25D366]/10 text-[#25D366] flex items-center justify-center">
                  <MessageSquare className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-[#10231C]">WhatsApp Business</h4>
                  <p className="text-[11px] text-[#68756F]">892 chats • 99.2% rate</p>
                </div>
              </div>
              <span className="text-xs font-extrabold text-[#287A59]">69.5%</span>
            </div>

            {/* Instagram */}
            <div className="p-3 rounded-xl bg-[#F7F6F1] border border-[#E2E4DF] flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-[#E4405F]/10 text-[#E4405F] flex items-center justify-center">
                  <Instagram className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-[#10231C]">Instagram Direct</h4>
                  <p className="text-[11px] text-[#68756F]">244 chats • 97.4% rate</p>
                </div>
              </div>
              <span className="text-xs font-extrabold text-[#287A59]">19.0%</span>
            </div>

            {/* Email */}
            <div className="p-3 rounded-xl bg-[#F7F6F1] border border-[#E2E4DF] flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-[#4285F4]/10 text-[#4285F4] flex items-center justify-center">
                  <Mail className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-[#10231C]">Corporate Email</h4>
                  <p className="text-[11px] text-[#68756F]">86 threads • 96.1% rate</p>
                </div>
              </div>
              <span className="text-xs font-extrabold text-[#287A59]">6.7%</span>
            </div>

            {/* Calls */}
            <div className="p-3 rounded-xl bg-[#F7F6F1] border border-[#E2E4DF] flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-[#287A59]/10 text-[#287A59] flex items-center justify-center">
                  <PhoneCall className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-[#10231C]">Phone & Voice Transcripts</h4>
                  <p className="text-[11px] text-[#68756F]">62 calls • 100% transcribed</p>
                </div>
              </div>
              <span className="text-xs font-extrabold text-[#287A59]">4.8%</span>
            </div>
          </div>
        </div>

        {/* Section 5: AI Performance Panel */}
        <div className="lg:col-span-2 bg-white p-6 rounded-2xl border border-[#E2E4DF] shadow-2xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-[#287A59]/15 text-[#287A59] flex items-center justify-center">
                  <Zap className="w-4 h-4" />
                </div>
                <h3 className="text-sm font-bold text-[#10231C] tracking-tight">AI Agent Performance & Health</h3>
              </div>
              <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-[#35D98A]/20 text-[#10231C]">
                Autonomous Level: High
              </span>
            </div>
            <p className="text-xs text-[#68756F] mb-6">Real-time resolution analytics and human handoff telemetry</p>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="p-4 rounded-xl bg-[#F7F6F1] border border-[#E2E4DF]">
                <p className="text-xs text-[#68756F]">AI Handled</p>
                <p className="text-2xl font-bold text-[#10231C] mt-1">82.4%</p>
                <p className="text-[11px] text-[#287A59] font-semibold mt-1">Autonomous</p>
              </div>

              <div className="p-4 rounded-xl bg-[#F7F6F1] border border-[#E2E4DF]">
                <p className="text-xs text-[#68756F]">Avg Response Time</p>
                <p className="text-2xl font-bold text-[#10231C] mt-1">1.4s</p>
                <p className="text-[11px] text-[#287A59] font-semibold mt-1">Sub-second peak</p>
              </div>

              <div className="p-4 rounded-xl bg-[#F7F6F1] border border-[#E2E4DF]">
                <p className="text-xs text-[#68756F]">Resolution Rate</p>
                <p className="text-2xl font-bold text-[#10231C] mt-1">88.2%</p>
                <p className="text-[11px] text-[#287A59] font-semibold mt-1">No human needed</p>
              </div>

              <div className="p-4 rounded-xl bg-[#F7F6F1] border border-[#E2E4DF]">
                <p className="text-xs text-[#68756F]">Escalation Rate</p>
                <p className="text-2xl font-bold text-[#10231C] mt-1">11.8%</p>
                <p className="text-[11px] text-[#68756F] font-semibold mt-1">High-value quotes</p>
              </div>
            </div>

            {/* AI Learning Progress Banner */}
            <div className="mt-6 p-4 rounded-xl bg-[#287A59]/5 border border-[#287A59]/20 flex items-center justify-between">
              <div>
                <h4 className="text-xs font-bold text-[#10231C]">Trained on Zawadi Emporium Swahili & English FAQs</h4>
                <p className="text-[11px] text-[#68756F] mt-0.5">
                  142 Knowledge items active • Kariakoo, Mikocheni & Masaki delivery matrices loaded
                </p>
              </div>
              <button
                onClick={() => onNavigate('ai-agent')}
                className="px-3 py-1.5 rounded-lg bg-[#287A59] text-white text-xs font-bold hover:bg-[#1f5f45] transition-colors"
              >
                Configure AI
              </button>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-[#E2E4DF] flex items-center justify-between text-xs text-[#68756F]">
            <span>Last trained: <b>Today at 07:15 AM EAT</b></span>
            <span className="text-[#287A59] font-bold">Zero downtime in 90 days</span>
          </div>
        </div>
      </div>

    </div>
  );
};

export default DashboardPage;
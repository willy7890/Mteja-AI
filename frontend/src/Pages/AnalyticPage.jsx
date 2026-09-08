import React, { useState } from 'react';
import {
  BarChart3,
  TrendingUp,
  Clock,
  CheckCircle2,
  Users,
  DollarSign,
  Calendar,
  Sparkles,
  ArrowUpRight,
  ArrowDownRight,
  Download,
  Filter
} from 'lucide-react';
import { PageId } from '../../types';

interface AnalyticsPageProps {
  onNavigate: (page: PageId) => void;
}

export const AnalyticsPage: React.FC<AnalyticsPageProps> = ({ onNavigate }) => {
  const [timeRange, setTimeRange] = useState<'today' | '7d' | '30d' | '90d' | 'custom'>('30d');

  // Dynamic stats per time range
  const data = {
    today: {
      total: '84',
      aiHandled: '71 (84.5%)',
      humanHandled: '13 (15.5%)',
      avgResponse: '1.2s',
      resolutionRate: '90.2%',
      leadsGenerated: '14',
      conversionRate: '12.4%',
      revenueInfluenced: 'TZS 620,000',
    },
    '7d': {
      total: '412',
      aiHandled: '348 (84.4%)',
      humanHandled: '64 (15.6%)',
      avgResponse: '1.3s',
      resolutionRate: '89.1%',
      leadsGenerated: '42',
      conversionRate: '11.8%',
      revenueInfluenced: 'TZS 1.65M',
    },
    '30d': {
      total: '1,284',
      aiHandled: '1,058 (82.4%)',
      humanHandled: '226 (17.6%)',
      avgResponse: '1.4s',
      resolutionRate: '88.2%',
      leadsGenerated: '127',
      conversionRate: '9.8%',
      revenueInfluenced: 'TZS 4.8M',
    },
    '90d': {
      total: '3,840',
      aiHandled: '3,110 (81.0%)',
      humanHandled: '730 (19.0%)',
      avgResponse: '1.5s',
      resolutionRate: '87.4%',
      leadsGenerated: '380',
      conversionRate: '10.2%',
      revenueInfluenced: 'TZS 14.2M',
    },
    custom: {
      total: '1,650',
      aiHandled: '1,353 (82.0%)',
      humanHandled: '297 (18.0%)',
      avgResponse: '1.4s',
      resolutionRate: '88.0%',
      leadsGenerated: '162',
      conversionRate: '9.9%',
      revenueInfluenced: 'TZS 6.1M',
    }
  }[timeRange];

  // Bar chart heights for daily volume
  const dailyBars = [35, 52, 44, 78, 65, 92, 108, 85, 96, 115, 82, 120];

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-8">
      {/* Header & Date Selector */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-[#10231C] tracking-tight">Performance Analytics</h2>
          <p className="text-xs text-[#68756F] mt-1">
            Real-time conversion metrics, customer response latencies, and revenue impact across Tanzania.
          </p>
        </div>

        {/* Time range selector */}
        <div className="flex items-center gap-2">
          <div className="bg-white border border-[#E2E4DF] rounded-xl p-1 flex items-center shadow-2xs">
            {(['today', '7d', '30d', '90d', 'custom'] as const).map((range) => {
              const labels = {
                today: 'Today',
                '7d': '7 Days',
                '30d': '30 Days',
                '90d': '90 Days',
                custom: 'Custom',
              };
              const isSelected = timeRange === range;
              return (
                <button
                  key={range}
                  onClick={() => setTimeRange(range)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
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
            className="p-2 rounded-xl bg-white border border-[#E2E4DF] text-[#68756F] hover:text-[#10231C] shadow-2xs"
            title="Export CSV Report"
          >
            <Download className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* 8 Primary Metrics Cards Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-[#E2E4DF] shadow-2xs">
          <span className="text-xs text-[#68756F] font-semibold">Total Conversations</span>
          <p className="text-2xl font-bold text-[#10231C] mt-2">{data.total}</p>
          <span className="text-[11px] font-semibold text-[#287A59] mt-1 inline-flex items-center gap-1">
            <TrendingUp className="w-3 h-3" /> +18.4% vs prev period
          </span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-[#E2E4DF] shadow-2xs">
          <span className="text-xs text-[#68756F] font-semibold">AI Handled</span>
          <p className="text-2xl font-bold text-[#287A59] mt-2">{data.aiHandled}</p>
          <span className="text-[11px] font-semibold text-[#287A59] mt-1 inline-flex items-center gap-1">
            Autonomous resolution
          </span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-[#E2E4DF] shadow-2xs">
          <span className="text-xs text-[#68756F] font-semibold">Human Handled</span>
          <p className="text-2xl font-bold text-[#10231C] mt-2">{data.humanHandled}</p>
          <span className="text-[11px] font-semibold text-[#68756F] mt-1 inline-flex items-center gap-1">
            High-value quotes & escrow
          </span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-[#E2E4DF] shadow-2xs">
          <span className="text-xs text-[#68756F] font-semibold">Avg Response Time</span>
          <p className="text-2xl font-bold text-[#10231C] mt-2">{data.avgResponse}</p>
          <span className="text-[11px] font-semibold text-[#287A59] mt-1 inline-flex items-center gap-1">
            Competitor benchmark: 14 mins
          </span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-[#E2E4DF] shadow-2xs">
          <span className="text-xs text-[#68756F] font-semibold">Resolution Rate</span>
          <p className="text-2xl font-bold text-[#10231C] mt-2">{data.resolutionRate}</p>
          <span className="text-[11px] font-semibold text-[#287A59] mt-1 inline-flex items-center gap-1">
            Resolved within 1 message
          </span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-[#E2E4DF] shadow-2xs">
          <span className="text-xs text-[#68756F] font-semibold">Leads Generated</span>
          <p className="text-2xl font-bold text-[#10231C] mt-2">{data.leadsGenerated}</p>
          <span className="text-[11px] font-semibold text-[#287A59] mt-1 inline-flex items-center gap-1">
            Verified phone & delivery location
          </span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-[#E2E4DF] shadow-2xs">
          <span className="text-xs text-[#68756F] font-semibold">Conversion Rate</span>
          <p className="text-2xl font-bold text-[#10231C] mt-2">{data.conversionRate}</p>
          <span className="text-[11px] font-semibold text-[#287A59] mt-1 inline-flex items-center gap-1">
            Inquiry to paid order
          </span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-[#E2E4DF] shadow-2xs">
          <span className="text-xs text-[#68756F] font-semibold">Revenue Influenced</span>
          <p className="text-2xl font-bold text-[#287A59] mt-2">{data.revenueInfluenced}</p>
          <span className="text-[11px] font-semibold text-[#287A59] mt-1 inline-flex items-center gap-1">
            Direct customer sales
          </span>
        </div>
      </div>

      {/* Analytics Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart 1: Conversation Volume & AI Distribution */}
        <div className="bg-white p-6 rounded-2xl border border-[#E2E4DF] shadow-2xs space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-[#10231C]">Daily Conversation Volume</h3>
              <p className="text-xs text-[#68756F]">Inquiries processed per day (Last 12 intervals)</p>
            </div>
            <span className="text-xs font-bold text-[#287A59]">Peak: 120 chats/day</span>
          </div>

          <div className="h-48 flex items-end justify-between gap-2 pt-6 pb-2 border-b border-[#E2E4DF]">
            {dailyBars.map((val, idx) => (
              <div key={idx} className="flex-1 flex flex-col items-center gap-1.5 h-full justify-end group">
                <div
                  className="w-full bg-[#287A59]/80 group-hover:bg-[#287A59] rounded-t-md transition-all relative"
                  style={{ height: `${(val / 130) * 100}%` }}
                >
                  <span className="opacity-0 group-hover:opacity-100 absolute -top-6 left-1/2 -translate-x-1/2 bg-[#10231C] text-white text-[10px] px-1.5 py-0.5 rounded pointer-events-none transition-opacity">
                    {val}
                  </span>
                </div>
                <span className="text-[10px] text-[#68756F]">D{idx + 1}</span>
              </div>
            ))}
          </div>

          <div className="flex items-center justify-between text-xs text-[#68756F]">
            <span>Average volume: <b>78 conversations / day</b></span>
            <span className="text-[#287A59] font-bold">82% automated</span>
          </div>
        </div>

        {/* Chart 2: Channel Performance Breakdown */}
        <div className="bg-white p-6 rounded-2xl border border-[#E2E4DF] shadow-2xs space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-[#10231C]">Channel Share & Conversion</h3>
              <p className="text-xs text-[#68756F]">Lead velocity by messaging channel</p>
            </div>
            <span className="text-xs font-bold text-[#10231C]">4 Connected</span>
          </div>

          <div className="space-y-3 pt-2">
            <div>
              <div className="flex justify-between text-xs font-semibold mb-1">
                <span className="text-[#10231C]">WhatsApp Business</span>
                <span className="text-[#287A59]">69.5% (892 convos • 48.2% sales)</span>
              </div>
              <div className="w-full h-2.5 bg-[#F7F6F1] rounded-full overflow-hidden">
                <div className="h-full bg-[#25D366] rounded-full" style={{ width: '69.5%' }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-semibold mb-1">
                <span className="text-[#10231C]">Instagram Direct</span>
                <span className="text-[#287A59]">19.0% (244 convos • 32.1% sales)</span>
              </div>
              <div className="w-full h-2.5 bg-[#F7F6F1] rounded-full overflow-hidden">
                <div className="h-full bg-[#E4405F] rounded-full" style={{ width: '19.0%' }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-semibold mb-1">
                <span className="text-[#10231C]">Corporate Email</span>
                <span className="text-[#287A59]">6.7% (86 convos • 14.5% sales)</span>
              </div>
              <div className="w-full h-2.5 bg-[#F7F6F1] rounded-full overflow-hidden">
                <div className="h-full bg-[#4285F4] rounded-full" style={{ width: '6.7%' }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-semibold mb-1">
                <span className="text-[#10231C]">Phone & Voice Transcripts</span>
                <span className="text-[#287A59]">4.8% (62 convos • 28.0% sales)</span>
              </div>
              <div className="w-full h-2.5 bg-[#F7F6F1] rounded-full overflow-hidden">
                <div className="h-full bg-[#287A59] rounded-full" style={{ width: '4.8%' }} />
              </div>
            </div>
          </div>

          <div className="pt-2 border-t border-[#E2E4DF] flex items-center justify-between text-xs text-[#68756F]">
            <span>WhatsApp yields highest conversion for Dar es Salaam buyers</span>
            <button onClick={() => onNavigate('channels')} className="text-[#287A59] font-bold hover:underline">
              Channel Settings
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  TrendingUp,
  Download,
  Loader2,
  BarChart3,
} from 'lucide-react';
import { apiGet } from '../api/Client';

function AnalyticsPage() {
  const navigate = useNavigate();
  const [timeRange, setTimeRange] = useState('30d');
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError('');
      try {
        const endDate = new Date();
        const startDate = new Date(endDate);
        const days = Number.parseInt(timeRange, 10) || 30;
        startDate.setDate(endDate.getDate() - days);
        const params = new URLSearchParams({
          start_date: startDate.toISOString().slice(0, 10),
          end_date: endDate.toISOString().slice(0, 10),
        });
        const data = await apiGet(`/api/v1/analytics/overview?${params}`);
        setStats(data || null);
      } catch (err) {
        console.error(err);
        setStats(null);
        setError('Unable to load analytics right now.');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [timeRange]);

  const labels = {
    today: 'Today',
    '7d': '7 Days',
    '30d': '30 Days',
    '90d': '90 Days',
  };

  if (loading) {
    return (
      <div className="p-6 md:p-8 flex items-center justify-center min-h-[50vh]">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="w-7 h-7 animate-spin text-[#287A59]" />
          <p className="text-sm text-[#68756F]">Loading analytics...</p>
        </div>
      </div>
    );
  }

  const total = stats?.total_conversations ?? 0;
  const aiHandled = stats?.ai_replies ?? 0;
  const humanHandled = stats?.human_handled ?? Math.max(0, total - aiHandled);
  const avgResponse = stats?.avg_response_time ?? '—';
  const resolutionRate = stats?.resolution_rate != null ? `${stats.resolution_rate}%` : '—';
  const leads = stats?.leads_generated ?? 0;
  const conversion = stats?.conversion_rate != null ? `${stats.conversion_rate}%` : '—';
  const revenue = stats?.revenue != null ? `TZS ${stats.revenue}` : '—';
  const aiPercent =
    total > 0 ? `${Math.round((aiHandled / total) * 100)}%` : '0%';
  const humanPercent =
    total > 0 ? `${Math.round((humanHandled / total) * 100)}%` : '0%';

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-[#10231C] tracking-tight">
            Performance Analytics
          </h2>
          <p className="text-xs text-[#68756F] mt-1">
            Conversations, AI performance, and revenue impact.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <div className="bg-white border border-[#E2E4DF] rounded-xl p-1 flex items-center">
            {['today', '7d', '30d', '90d'].map((range) => {
              const isSelected = timeRange === range;
              return (
                <button
                  key={range}
                  onClick={() => setTimeRange(range)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                    isSelected
                      ? 'bg-[#10231C] text-white'
                      : 'text-[#68756F] hover:text-[#10231C]'
                  }`}
                >
                  {labels[range]}
                </button>
              );
            })}
          </div>

          <button
            className="p-2 rounded-xl bg-white border border-[#E2E4DF] text-[#68756F] hover:text-[#10231C]"
            title="Export"
          >
            <Download className="w-4 h-4" />
          </button>
        </div>
      </div>

      {error && (
        <div className="px-4 py-3 rounded-xl text-sm bg-red-50 text-red-600">
          {error}
        </div>
      )}

      {/* Metrics */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-[#E2E4DF]">
          <span className="text-xs text-[#68756F] font-semibold">
            Total Conversations
          </span>
          <p className="text-2xl font-bold text-[#10231C] mt-2">{total}</p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-[#E2E4DF]">
          <span className="text-xs text-[#68756F] font-semibold">AI Handled</span>
          <p className="text-2xl font-bold text-[#287A59] mt-2">
            {aiHandled} ({aiPercent})
          </p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-[#E2E4DF]">
          <span className="text-xs text-[#68756F] font-semibold">
            Human Handled
          </span>
          <p className="text-2xl font-bold text-[#10231C] mt-2">
            {humanHandled} ({humanPercent})
          </p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-[#E2E4DF]">
          <span className="text-xs text-[#68756F] font-semibold">
            Avg Response Time
          </span>
          <p className="text-2xl font-bold text-[#10231C] mt-2">{avgResponse}</p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-[#E2E4DF]">
          <span className="text-xs text-[#68756F] font-semibold">
            Resolution Rate
          </span>
          <p className="text-2xl font-bold text-[#10231C] mt-2">
            {resolutionRate}
          </p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-[#E2E4DF]">
          <span className="text-xs text-[#68756F] font-semibold">
            Leads Generated
          </span>
          <p className="text-2xl font-bold text-[#10231C] mt-2">{leads}</p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-[#E2E4DF]">
          <span className="text-xs text-[#68756F] font-semibold">
            Conversion Rate
          </span>
          <p className="text-2xl font-bold text-[#10231C] mt-2">{conversion}</p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-[#E2E4DF]">
          <span className="text-xs text-[#68756F] font-semibold">
            Revenue Influenced
          </span>
          <p className="text-2xl font-bold text-[#287A59] mt-2">{revenue}</p>
        </div>
      </div>

      {/* Empty / charts area */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-2xl border border-[#E2E4DF] space-y-4">
          <div>
            <h3 className="text-sm font-bold text-[#10231C]">
              Conversation Volume
            </h3>
            <p className="text-xs text-[#68756F]">
              Inquiries over the selected period
            </p>
          </div>

          {total === 0 ? (
            <div className="h-48 flex flex-col items-center justify-center text-center">
              <BarChart3 className="w-8 h-8 text-[#68756F] mb-2" />
              <p className="text-sm font-medium text-[#10231C]">No data yet</p>
              <p className="text-xs text-[#68756F] mt-1">
                Charts will appear when customers start messaging.
              </p>
            </div>
          ) : (
            <div className="h-48 flex items-end justify-center text-xs text-[#68756F]">
              Chart data will load from API
            </div>
          )}
        </div>

        <div className="bg-white p-6 rounded-2xl border border-[#E2E4DF] space-y-4">
          <div>
            <h3 className="text-sm font-bold text-[#10231C]">
              Channel Performance
            </h3>
            <p className="text-xs text-[#68756F]">
              Share by messaging channel
            </p>
          </div>

          {total === 0 ? (
            <div className="h-48 flex flex-col items-center justify-center text-center">
              <TrendingUp className="w-8 h-8 text-[#68756F] mb-2" />
              <p className="text-sm font-medium text-[#10231C]">No channel data</p>
              <p className="text-xs text-[#68756F] mt-1">
                Connect WhatsApp, Telegram or Instagram to see breakdown.
              </p>
            </div>
          ) : (
            <div className="space-y-3 pt-2 text-xs text-[#68756F]">
              Channel breakdown will load from API
            </div>
          )}

          <div className="pt-2 border-t border-[#E2E4DF] flex justify-end">
            <button
              onClick={() => navigate('/dashboard/channels')}
              className="text-xs text-[#287A59] font-bold hover:underline"
            >
              Channel Settings
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AnalyticsPage;
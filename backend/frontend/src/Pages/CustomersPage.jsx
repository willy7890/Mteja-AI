import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  Users,
  MessageSquare,
  Camera,
  Mail,
  PhoneCall,
  Loader2,
  Plus,
  Filter,
  ChevronRight,
} from 'lucide-react';
import { apiGet } from '../api/Client';

function CustomersPage({ t }) {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [customers, setCustomers] = useState([]);
  const [search, setSearch] = useState('');
  const [channelFilter, setChannelFilter] = useState('all');
  const [error, setError] = useState('');

  useEffect(() => {
    async function loadCustomers() {
      setLoading(true);
      setError('');
      try {
        const data = await apiGet('/api/v1/customers');
        setCustomers(data?.items || data || []);
      } catch (err) {
        console.error(err);
        setError('Failed to load customers');
        setCustomers([]);
      } finally {
        setLoading(false);
      }
    }

    loadCustomers();
  }, []);

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

  const filtered = customers.filter((c) => {
    const name = (c.name || c.full_name || c.customer_name || '').toLowerCase();
    const phone = (c.phone || c.phone_number || '').toLowerCase();
    const email = (c.email || '').toLowerCase();
    const q = search.toLowerCase();

    const matchesSearch =
      !q || name.includes(q) || phone.includes(q) || email.includes(q);

    const matchesChannel =
      channelFilter === 'all' ||
      (c.channel || c.last_channel || '').toLowerCase() === channelFilter;

    return matchesSearch && matchesChannel;
  });

  if (loading) {
    return (
      <div className="p-6 md:p-8 flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-3">
          <Loader2 size={28} className="animate-spin" style={{ color: t.accent }} />
          <p className="text-sm" style={{ color: t.muted }}>
            Loading customers...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 md:p-8 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold" style={{ color: t.text }}>
            Customers
          </h2>
          <p className="mt-1 text-sm" style={{ color: t.muted }}>
            All customers who have contacted you across channels
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span
            className="text-xs font-semibold px-3 py-1.5 rounded-full"
            style={{ background: t.surface, color: t.muted }}
          >
            {customers.length} total
          </span>
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

      {/* Search + Filter */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search
            size={16}
            className="absolute left-3.5 top-1/2 -translate-y-1/2"
            style={{ color: t.muted }}
          />
          <input
            type="text"
            placeholder="Search by name, phone or email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 rounded-xl text-sm outline-none"
            style={{
              background: t.card,
              border: `1px solid ${t.border}`,
              color: t.text,
            }}
          />
        </div>

        <div className="flex items-center gap-1.5 overflow-x-auto">
          {['all', 'whatsapp', 'telegram', 'instagram', 'email', 'call'].map(
            (ch) => {
              const isActive = channelFilter === ch;
              return (
                <button
                  key={ch}
                  onClick={() => setChannelFilter(ch)}
                  className="px-3 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-colors"
                  style={{
                    background: isActive ? t.accent : t.card,
                    color: isActive ? t.accentText : t.muted,
                    border: `1px solid ${isActive ? t.accent : t.border}`,
                  }}
                >
                  {ch === 'all' ? 'All channels' : ch.charAt(0).toUpperCase() + ch.slice(1)}
                </button>
              );
            }
          )}
        </div>
      </div>

      {/* Customer list */}
      <div
        className="rounded-2xl overflow-hidden"
        style={{ background: t.card, border: `1px solid ${t.border}` }}
      >
        {filtered.length === 0 ? (
          <div className="p-14 text-center">
            <Users size={36} style={{ color: t.muted, margin: '0 auto 14px' }} />
            <p className="text-sm font-medium" style={{ color: t.text }}>
              {customers.length === 0 ? 'No customers yet' : 'No matching customers'}
            </p>
            <p className="text-xs mt-1.5 max-w-sm mx-auto" style={{ color: t.muted }}>
              {customers.length === 0
                ? 'When someone messages you on WhatsApp, Telegram, Instagram or Email, they will automatically appear here.'
                : 'Try changing the search or filter.'}
            </p>
          </div>
        ) : (
          <div className="divide-y" style={{ borderColor: t.border }}>
            {/* Table header */}
            <div
              className="hidden sm:grid grid-cols-12 gap-4 px-5 py-3 text-[11px] font-bold uppercase tracking-wider"
              style={{ color: t.muted, background: t.surface }}
            >
              <div className="col-span-4">Customer</div>
              <div className="col-span-2">Channel</div>
              <div className="col-span-3">Contact</div>
              <div className="col-span-2">Last seen</div>
              <div className="col-span-1"></div>
            </div>

            {filtered.map((c) => {
              const name = c.name || c.full_name || c.customer_name || 'Unknown';
              const channel = c.channel || c.last_channel || '—';
              const phone = c.phone || c.phone_number || '';
              const email = c.email || '';
              const lastSeen = c.last_seen || c.updated_at || c.last_message_at || '';

              return (
                <div
                  key={c.id}
                  onClick={() =>
                    navigate('/dashboard/inbox', {
                      state: { customerId: c.id, conversationId: c.last_conversation_id },
                    })
                  }
                  className="grid grid-cols-1 sm:grid-cols-12 gap-3 sm:gap-4 px-5 py-4 items-center cursor-pointer transition-colors"
                  onMouseEnter={(e) =>
                    (e.currentTarget.style.background = `${t.text}08`)
                  }
                  onMouseLeave={(e) =>
                    (e.currentTarget.style.background = 'transparent')
                  }
                >
                  {/* Name + avatar */}
                  <div className="col-span-4 flex items-center gap-3 min-w-0">
                    <img
                      src={
                        c.avatar ||
                        `https://ui-avatars.com/api/?name=${encodeURIComponent(
                          name
                        )}&background=2F6F4E&color=fff`
                      }
                      alt={name}
                      className="w-10 h-10 rounded-full object-cover flex-shrink-0"
                      style={{ border: `1px solid ${t.border}` }}
                    />
                    <div className="min-w-0">
                      <p className="text-sm font-semibold truncate" style={{ color: t.text }}>
                        {name}
                      </p>
                      <p className="text-[11px] truncate sm:hidden" style={{ color: t.muted }}>
                        {phone || email || channel}
                      </p>
                    </div>
                  </div>

                  {/* Channel */}
                  <div className="col-span-2 hidden sm:flex items-center gap-2">
                    {getChannelIcon(channel)}
                    <span className="text-xs font-medium capitalize" style={{ color: t.text }}>
                      {channel}
                    </span>
                  </div>

                  {/* Contact */}
                  <div className="col-span-3 hidden sm:block min-w-0">
                    <p className="text-xs truncate" style={{ color: t.text }}>
                      {phone || email || '—'}
                    </p>
                  </div>

                  {/* Last seen */}
                  <div className="col-span-2 hidden sm:block">
                    <p className="text-xs" style={{ color: t.muted }}>
                      {lastSeen || '—'}
                    </p>
                  </div>

                  {/* Arrow */}
                  <div className="col-span-1 hidden sm:flex justify-end">
                    <ChevronRight size={16} style={{ color: t.muted }} />
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

export default CustomersPage;
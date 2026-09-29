import { useEffect } from "react";
import {
  LayoutDashboard, Inbox, Users, Bot, Zap, BarChart3, ShieldCheck,
  UserCheck, Settings, CreditCard, ChevronRight, X,
} from "lucide-react";
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

export const Sidebar = ({
  t,
  user,
  currentPage,
  activePage,
  onNavigate,
  unreadInboxCount,
  mobileOpen,
  onCloseMobile,
  activeChannelFilter,
  onSelectChannelFilter,
}) => {
  const current = currentPage || activePage || "dashboard";
  const profileAvatar = user?.avatar_url || localStorage.getItem('mteja_profile_avatar');

  // While the full-screen menu is open on a phone: lock page scroll, close with Escape
  useEffect(() => {
    if (!mobileOpen) return;

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    const onKey = (e) => {
      if (e.key === "Escape" && onCloseMobile) onCloseMobile();
    };
    window.addEventListener("keydown", onKey);

    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener("keydown", onKey);
    };
  }, [mobileOpen, onCloseMobile]);

  const mainNavItems = [
    { id: "dashboard", label: "Overview", icon: LayoutDashboard },
    { id: "inbox", label: "Inbox", icon: Inbox, badge: unreadInboxCount > 0 ? unreadInboxCount : undefined },
    { id: "customers", label: "Customers", icon: Users },
    { id: "ai-agent", label: "AI Agent", icon: Bot, badge: "Active"},
    { id: "automations", label: "Automations", icon: Zap },
    { id: "analytics", label: "Analytics", icon: BarChart3 },
  ];
  if (user?.is_superuser) {
    mainNavItems.push({ id: "admin", label: "Admin", icon: ShieldCheck });
  }
  const channelItems = [
    { channel: "whatsapp", label: "WhatsApp", icon: FaWhatsapp, count: "Active" },
    { channel: "telegram", label: "Telegram", icon: FaTelegram, count: "Active" },
    { channel: "tiktok", label: "TikTok", icon: FaTiktok, count: "New" },
    { channel: "instagram", label: "Instagram", icon: FaInstagram, count: "1 new" },
    { channel: "facebook", label: "Facebook", icon: FaFacebookF, count: "New" },
    { channel: "email", label: "Email", icon: FaEnvelope, count: "Synced" },
    { channel: "sms", label: "Normal SMS", icon: FaCommentSms, count: "New" },
    { channel: "call", label: "Calls & Voice", icon: FaPhone, count: "1 voice" },
  ];

  const handleChannelClick = (channel) => {
    if (onSelectChannelFilter) onSelectChannelFilter(channel);
    onNavigate("inbox");
    if (onCloseMobile) onCloseMobile();
  };

  const handleItemNavigate = (page) => {
    if (page === "inbox" && onSelectChannelFilter) onSelectChannelFilter(null);
    onNavigate(page);
    if (onCloseMobile) onCloseMobile();
  };

  return (
    <aside
      /*
       * Phone  (< 768px): closed = display:none (takes NO space, so the page
       *                   uses the full screen); open = full-screen menu.
       * Tablet/desktop  : normal sticky sidebar, 260px wide.
       */
      className={`flex-col justify-between flex-shrink-0 select-none overflow-y-auto fixed top-0 left-0 z-50 w-full h-[100dvh] md:sticky md:left-auto md:z-30 md:w-[260px] md:h-screen ${
        mobileOpen ? "flex" : "hidden md:flex"
      }`}
      style={{ background: t.card, borderRight: `1px solid ${t.border}` }}
    >
      <div className="px-5 md:px-6 pb-2 pt-[calc(1rem+env(safe-area-inset-top,0px))] md:pt-6">
        <div className="flex items-center justify-between mb-6">
          <button
            onClick={() => handleItemNavigate("dashboard")}
            className="flex items-center gap-2.5 text-left"
            title="MtejaAI Dashboard"
          >
            <img src="/signi-ai.png" alt="Signi AI" className="h-9 w-auto max-w-[150px] object-contain" />
          </button>

          {onCloseMobile && (
            <button
              onClick={onCloseMobile}
              aria-label="Close menu"
              className="md:hidden flex items-center justify-center w-11 h-11 rounded-xl"
              style={{ color: t.text, background: t.surface }}
            >
              <X size={22} />
            </button>
          )}
        </div>

        <nav className="space-y-1">
          {mainNavItems.map((item) => {
            const Icon = item.icon;
            const isActive = current === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleItemNavigate(item.id)}
                className="w-full flex items-center justify-between px-3 py-3 md:py-2 rounded-lg font-medium text-base md:text-sm transition-colors"
                style={{
                  background: isActive ? t.surface : 'transparent',
                  color: isActive ? t.accent : t.muted,
                  fontWeight: isActive ? 600 : 500,
                }}
              >
                <div className="flex items-center gap-3">
                  <Icon size={20} color={isActive ? t.accent : t.muted} />
                  <span>{item.label}</span>
                </div>
                {item.badge !== undefined && (
                  <span
                    className="text-[10px] font-bold px-2 py-0.5 rounded-full"
                    style={
                      typeof item.badge === "number"
                        ? { background: t.accent, color: t.accentText }
                        : { background: `${t.accent}26`, color: t.accent }
                    }
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        <div className="mt-8">
          <div className="flex items-center justify-between px-3 mb-2">
            <span className="text-[10px] font-bold uppercase tracking-widest" style={{ color: t.muted }}>Channels</span>
            <button onClick={() => handleItemNavigate("channels")} className="text-[10px] font-bold uppercase tracking-wider hover:underline" style={{ color: t.accent }}>
              Manage
            </button>
          </div>
          <div className="space-y-1">
            {channelItems.map((item) => {
              const Icon = item.icon;
              const isSelected = current === "inbox" && activeChannelFilter === item.channel;
              return (
                <button
                  key={item.channel}
                  onClick={() => handleChannelClick(item.channel)}
                  className="w-full flex items-center justify-between px-3 py-3 md:py-2 rounded-lg text-base md:text-sm transition-colors"
                  style={{
                    background: isSelected ? t.surface : 'transparent',
                    color: isSelected ? t.accent : t.muted,
                    fontWeight: isSelected ? 600 : 400,
                  }}
                >
                  <div className="flex items-center gap-3">
                    <Icon size={18} aria-hidden="true" />
                    <span>{item.label}</span>
                  </div>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full" style={{ background: t.surface, color: t.text }}>
                    {item.count}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        <div className="mt-6">
          <div className="px-3 mb-2">
            <span className="text-[10px] font-bold uppercase tracking-widest" style={{ color: t.muted }}>Management</span>
          </div>
          <div className="space-y-1">
            {[
              { id: 'team', label: 'Team', Icon: UserCheck },
              { id: 'billing', label: 'Billing & Usage', Icon: CreditCard },
              { id: 'settings', label: 'Settings', Icon: Settings },
            ].map(({ id, label, Icon }) => {
              const isActive = current === id;
              return (
                <button
                  key={id}
                  onClick={() => handleItemNavigate(id)}
                  className="w-full flex items-center gap-3 px-3 py-3 md:py-2 rounded-lg text-base md:text-sm transition-colors"
                  style={{
                    background: isActive ? t.surface : 'transparent',
                    color: isActive ? t.accent : t.muted,
                    fontWeight: isActive ? 600 : 400,
                  }}
                >
                  <Icon size={20} color={isActive ? t.accent : t.muted} />
                  <span>{label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      <div
        className="mt-auto px-5 pt-5 pb-[calc(1.25rem+env(safe-area-inset-bottom,0px))]"
        style={{ borderTop: `1px solid ${t.border}`, background: t.card }}
      >
        <button onClick={() => handleItemNavigate("profile")} className="w-full flex items-center gap-3 text-left p-2 rounded-xl transition-colors" style={{ background: 'transparent' }}>
          <div className="w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm flex-shrink-0" style={{ background: t.text, color: t.bg }}>
            {/* First letter of the real name, falling back to "?" only
                if user data somehow isn't loaded yet. */}
            {profileAvatar ? (
              <img src={profileAvatar} alt={user?.full_name || 'Profile'} className="w-full h-full rounded-full object-cover" />
            ) : (user?.full_name ? user.full_name.charAt(0).toUpperCase() : '?')}
          </div>
          <div className="min-w-0 flex-1">
            <div className="text-sm font-semibold truncate" style={{ color: t.text }}>
              {user?.full_name || 'Loading…'}
            </div>
            <div className="text-[11px] truncate" style={{ color: t.muted }}>
              {user?.email || ''}
            </div>
          </div>
          <ChevronRight size={16} color={t.muted} />
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
import { useState, useRef, useEffect } from "react";
import { Search, Bell, LogOut, User, CreditCard, Settings, Layers, ChevronDown } from "lucide-react";

export const TopHeader = ({
  t,
  currentPage,
  activePage,
  unreadCount,
  unreadNotificationsCount,
  onNavigate,
  onOpenCommandPalette,
  onToggleMobileMenu,
}) => {
  const current = currentPage || activePage || "dashboard";
  const notifCount = unreadCount ?? unreadNotificationsCount ?? 0;
  const [profileDropdownOpen, setProfileDropdownOpen] = useState(false);
  const [pageSwitcherOpen, setPageSwitcherOpen] = useState(false);
  const dropdownRef = useRef(null);
  const switcherRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) setProfileDropdownOpen(false);
      if (switcherRef.current && !switcherRef.current.contains(event.target)) setPageSwitcherOpen(false);
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const getPageTitle = (page) => {
    const titles = {
      dashboard: "Dashboard Overview", inbox: "Unified Inbox", customers: "Customer CRM",
      "ai-agent": "AI Agent Studio", automations: "Automations & Workflows",
      analytics: "Performance Analytics", channels: "Channels & Integrations",
      team: "Team Members", settings: "Platform Settings", billing: "Billing & Subscriptions",
      notifications: "Notifications & Alerts", profile: "User Profile",
    };
    return titles[page] || "Overview";
  };


  const allPages = [
    { id: "dashboard", label: "Dashboard Overview", category: "Core" },
    { id: "inbox", label: "Unified Inbox", category: "Core" },
    { id: "customers", label: "Customer CRM", category: "Core" },
    { id: "ai-agent", label: "AI Agent Studio", category: "AI" },
    { id: "automations", label: "Automations", category: "AI" },
    { id: "analytics", label: "Analytics & Reports", category: "Intelligence" },
    { id: "channels", label: "Channels (WA, IG, Email, Calls)", category: "Integrations" },
    { id: "team", label: "Team Members", category: "Settings" },
    { id: "settings", label: "Platform Settings", category: "Settings" },
    { id: "billing", label: "Billing & Usage (TZS)", category: "Settings" },
    { id: "notifications", label: "Notifications Center", category: "Core" },
    { id: "profile", label: "My Profile", category: "Account" },
  ];

  return (
    <header className="h-16 flex items-center justify-between px-4 sm:px-8 sticky top-0 z-20" style={{ background: t.card, borderBottom: `1px solid ${t.border}` }}>
      <div className="flex items-center gap-3">
        {onToggleMobileMenu && (
          <button onClick={onToggleMobileMenu} className="md:hidden p-1.5 rounded-lg" style={{ color: t.muted }} title="Toggle Menu">
            <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        )}

        <h1 className="text-lg font-semibold" style={{ color: t.text }}>{getPageTitle(current)}</h1>

        <div className="relative" ref={switcherRef}>
          <button
            onClick={() => setPageSwitcherOpen(!pageSwitcherOpen)}
            className="hidden sm:flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full font-medium transition-colors"
            style={{ background: `${t.accent}1A`, color: t.accent, border: `1px solid ${t.accent}33` }}
            title="Jump to any dashboard page"
          >
            <Layers size={14} />
            <span>All Views</span>
            <ChevronDown size={12} />
          </button>

          {pageSwitcherOpen && (
            <div className="absolute left-0 mt-2 w-72 rounded-2xl shadow-lg p-2 z-50 max-h-96 overflow-y-auto" style={{ background: t.card, border: `1px solid ${t.border}` }}>
              <div className="px-2.5 py-1.5 text-[10px] font-bold uppercase tracking-widest" style={{ color: t.muted, borderBottom: `1px solid ${t.border}` }}>
                All Dashboard Views
              </div>
              <div className="space-y-0.5 mt-1">
                {allPages.map((p) => {
                  const isCurrent = current === p.id;
                  return (
                    <button
                      key={p.id}
                      onClick={() => { onNavigate(p.id); setPageSwitcherOpen(false); }}
                      className="w-full text-left px-2.5 py-1.5 rounded-lg text-xs font-medium flex items-center justify-between transition-colors"
                      style={{ background: isCurrent ? t.accent : 'transparent', color: isCurrent ? t.accentText : t.text }}
                    >
                      <span>{p.label}</span>
                      <span className="text-[10px] px-1.5 py-0.5 rounded" style={{ background: isCurrent ? `${t.accentText}33` : t.surface, color: isCurrent ? t.accentText : t.muted }}>
                        {p.category}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="flex items-center gap-3 sm:gap-4">
        <div onClick={onOpenCommandPalette} className="relative cursor-pointer" title="Search conversations... (Cmd+K)">
          <input
            type="text"
            readOnly
            placeholder="Search conversations..."
            className="pl-10 pr-4 py-2 border-none rounded-full text-sm w-44 md:w-64 outline-none cursor-pointer"
            style={{ background: t.surface, color: t.text }}
          />
          <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2" style={{ color: t.muted }} />
        </div>

        <div
          onClick={() => onNavigate("notifications")}
          className="w-8 h-8 flex items-center justify-center rounded-full cursor-pointer transition-colors relative"
          style={{ color: t.muted }}
          title="Notifications"
        >
          <Bell size={18} />
          {notifCount > 0 && (
            <span className="absolute top-1 right-1 w-2 h-2 rounded-full" style={{ background: t.accent, boxShadow: `0 0 0 2px ${t.card}` }} />
          )}
        </div>

        <button
          onClick={() => onNavigate("inbox")}
          className="hidden sm:inline-flex px-4 py-2 rounded-full text-sm font-medium transition-colors"
          style={{ background: t.accent, color: t.accentText }}
        >
          New Broadcast
        </button>

        <div className="relative" ref={dropdownRef}>
          <button
            onClick={() => setProfileDropdownOpen(!profileDropdownOpen)}
            className="w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs transition-all"
            style={{ background: t.text, color: t.bg }}
          >
            KM
          </button>

          {profileDropdownOpen && (
            <div className="absolute right-0 mt-2 w-56 rounded-2xl shadow-lg p-2 z-50" style={{ background: t.card, border: `1px solid ${t.border}` }}>
              <div className="px-3 py-2" style={{ borderBottom: `1px solid ${t.border}` }}>
                <p className="text-xs font-bold" style={{ color: t.text }}>Khamis M.</p>
                <p className="text-[11px] truncate" style={{ color: t.muted }}>Zawadi Emporium</p>
                <div className="mt-1 flex items-center gap-1 text-[10px] font-semibold" style={{ color: t.accent }}>
                  <span>● Dar es Salaam, Tanzania</span>
                </div>
              </div>

              <div className="py-1">
                {[
                  { id: 'profile', label: 'My Profile', Icon: User },
                  { id: 'billing', label: 'Billing & Subscription', Icon: CreditCard },
                  { id: 'settings', label: 'Settings', Icon: Settings },
                ].map(({ id, label, Icon }) => (
                  <button
                    key={id}
                    onClick={() => { onNavigate(id); setProfileDropdownOpen(false); }}
                    className="w-full flex items-center gap-2.5 px-3 py-1.5 text-xs rounded-lg transition-colors"
                    style={{ color: t.text }}
                  >
                    <Icon size={14} color={t.muted} />
                    <span>{label}</span>
                  </button>
                ))}
              </div>

              <div className="pt-1" style={{ borderTop: `1px solid ${t.border}` }}>
                <button
                  onClick={() => { onNavigate("login"); setProfileDropdownOpen(false); }}
                  className="w-full flex items-center gap-2.5 px-3 py-1.5 text-xs rounded-lg transition-colors"
                  style={{ color: t.text }}
                >
                  <LogOut size={14} color={t.muted} />
                  <span>Sign out</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default TopHeader;
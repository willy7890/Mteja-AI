import {
  LayoutDashboard,
  Inbox,
  Users,
  Bot,
  Zap,
  BarChart3,
  MessageSquare,
  Instagram,
  Mail,
  PhoneCall,
  UserCheck,
  Settings,
  CreditCard,
  ChevronRight
} from "lucide-react";
export const Sidebar = ({
  activePage,
  currentPage,
  onNavigate,
  unreadInboxCount,
  mobileOpen,
  onCloseMobile,
  activeChannelFilter,
  onSelectChannelFilter
}) => {
  const current = currentPage || activePage || "dashboard";
  const mainNavItems = [
    { id: "dashboard", label: "Overview", icon: LayoutDashboard },
    { id: "inbox", label: "Inbox", icon: Inbox, badge: unreadInboxCount > 0 ? unreadInboxCount : void 0 },
    { id: "customers", label: "Customers", icon: Users },
    { id: "ai-agent", label: "AI Agent", icon: Bot, badge: "Active" },
    { id: "automations", label: "Automations", icon: Zap },
    { id: "analytics", label: "Analytics", icon: BarChart3 }
  ];
  const channelItems = [
    { channel: "whatsapp", label: "WhatsApp", icon: MessageSquare, count: "Active", color: "#25D366" },
    { channel: "instagram", label: "Instagram", icon: Instagram, count: "1 new", color: "#E4405F" },
    { channel: "email", label: "Email", icon: Mail, count: "Synced", color: "#4285F4" },
    { channel: "call", label: "Calls & Voice", icon: PhoneCall, count: "1 voice", color: "#287A59" }
  ];
  const handleChannelClick = (channel) => {
    if (onSelectChannelFilter) {
      onSelectChannelFilter(channel);
    }
    onNavigate("inbox");
    if (onCloseMobile) onCloseMobile();
  };
  const handleItemNavigate = (page) => {
    if (page === "inbox" && onSelectChannelFilter) {
      onSelectChannelFilter(null);
    }
    onNavigate(page);
    if (onCloseMobile) onCloseMobile();
  };
  return <>
      {
    /* Mobile Backdrop */
  }
      {mobileOpen && <div
    className="fixed inset-0 bg-black/40 z-40 md:hidden backdrop-blur-xs"
    onClick={onCloseMobile}
  />}

      <aside
    className={`w-[260px] flex-shrink-0 bg-white border-r border-[#E2E4DF] flex flex-col justify-between h-screen sticky top-0 select-none z-50 md:z-30 transition-transform duration-200 ease-in-out ${mobileOpen ? "fixed left-0 top-0 translate-x-0" : "fixed -translate-x-full md:relative md:translate-x-0"}`}
  >
        {
    /* Top Branding Section */
  }
        <div className="p-6 pb-2">
          <div className="flex items-center justify-between mb-6">
            <button
    onClick={() => handleItemNavigate("dashboard")}
    className="flex items-center gap-2.5 text-left group"
    title="MtejaAI Dashboard"
  >
              {
    /* Geometric Balance Icon: Rounded square with center circle */
  }
              <div className="w-8 h-8 bg-[#287A59] rounded-lg flex items-center justify-center flex-shrink-0 shadow-xs">
                <div className="w-4 h-4 bg-[#35D98A] rounded-full" />
              </div>
              <span className="text-xl font-bold tracking-tight text-[#10231C]">
                Mteja<span className="text-[#287A59]">AI</span>
              </span>
            </button>

            {onCloseMobile && <button
    onClick={onCloseMobile}
    className="md:hidden p-1.5 rounded-lg text-[#68756F] hover:bg-[#F7F6F1]"
  >
                ✕
              </button>}
          </div>

          {
    /* Navigation Items */
  }
          <nav className="space-y-1">
            {mainNavItems.map((item) => {
    const Icon = item.icon;
    const isActive = current === item.id;
    return <button
      key={item.id}
      onClick={() => handleItemNavigate(item.id)}
      className={`w-full flex items-center justify-between px-3 py-2 rounded-lg font-medium text-sm transition-colors cursor-pointer ${isActive ? "bg-[#F7F6F1] text-[#287A59] font-semibold" : "text-[#68756F] hover:bg-[#F7F6F1] hover:text-[#10231C]"}`}
    >
                  <div className="flex items-center gap-3">
                    <Icon className={`w-5 h-5 ${isActive ? "text-[#287A59]" : "text-[#68756F]"}`} />
                    <span>{item.label}</span>
                  </div>
                  {item.badge !== void 0 && <span
      className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${typeof item.badge === "number" ? "bg-[#287A59] text-white" : "bg-[#287A59]/15 text-[#287A59]"}`}
    >
                      {item.badge}
                    </span>}
                </button>;
  })}
          </nav>

          {
    /* Channels Section */
  }
          <div className="mt-8">
            <div className="flex items-center justify-between px-3 mb-2">
              <span className="text-[10px] font-bold uppercase tracking-widest text-[#68756F]">
                Channels
              </span>
              <button
    onClick={() => handleItemNavigate("channels")}
    className="text-[10px] text-[#287A59] hover:underline font-bold uppercase tracking-wider"
  >
                Manage
              </button>
            </div>
            <div className="space-y-1">
              {channelItems.map((item) => {
    const Icon = item.icon;
    const isSelected = current === "inbox" && activeChannelFilter === item.channel;
    return <button
      key={item.channel}
      onClick={() => handleChannelClick(item.channel)}
      className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm transition-colors cursor-pointer ${isSelected ? "bg-[#F7F6F1] text-[#287A59] font-semibold" : "text-[#68756F] hover:bg-[#F7F6F1] hover:text-[#10231C]"}`}
    >
                    <div className="flex items-center gap-3">
                      <div
      className="w-2 h-2 rounded-full"
      style={{ backgroundColor: item.color }}
    />
                      <span>{item.label}</span>
                    </div>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#E2E4DF] text-[#14201B]">
                      {item.count}
                    </span>
                  </button>;
  })}
            </div>
          </div>

          {
    /* Admin / Management Section */
  }
          <div className="mt-6">
            <div className="px-3 mb-2">
              <span className="text-[10px] font-bold uppercase tracking-widest text-[#68756F]">
                Management
              </span>
            </div>
            <div className="space-y-1">
              <button
    onClick={() => handleItemNavigate("team")}
    className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors cursor-pointer ${current === "team" ? "bg-[#F7F6F1] text-[#287A59] font-semibold" : "text-[#68756F] hover:bg-[#F7F6F1] hover:text-[#10231C]"}`}
  >
                <UserCheck className={`w-5 h-5 ${current === "team" ? "text-[#287A59]" : "text-[#68756F]"}`} />
                <span>Team</span>
              </button>
              <button
    onClick={() => handleItemNavigate("billing")}
    className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors cursor-pointer ${current === "billing" ? "bg-[#F7F6F1] text-[#287A59] font-semibold" : "text-[#68756F] hover:bg-[#F7F6F1] hover:text-[#10231C]"}`}
  >
                <CreditCard className={`w-5 h-5 ${current === "billing" ? "text-[#287A59]" : "text-[#68756F]"}`} />
                <span>Billing & Usage</span>
              </button>
              <button
    onClick={() => handleItemNavigate("settings")}
    className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors cursor-pointer ${current === "settings" ? "bg-[#F7F6F1] text-[#287A59] font-semibold" : "text-[#68756F] hover:bg-[#F7F6F1] hover:text-[#10231C]"}`}
  >
                <Settings className={`w-5 h-5 ${current === "settings" ? "text-[#287A59]" : "text-[#68756F]"}`} />
                <span>Settings</span>
              </button>
            </div>
          </div>
        </div>

        {
    /* Geometric Balance Footer with Bold Circular Monogram */
  }
        <div className="mt-auto border-t border-[#E2E4DF] p-5 bg-white">
          <button
    onClick={() => handleItemNavigate("profile")}
    className="w-full flex items-center gap-3 text-left hover:bg-[#F7F6F1] p-2 rounded-xl transition-colors"
  >
            <div className="w-10 h-10 rounded-full bg-[#10231C] text-white flex items-center justify-center font-bold text-sm flex-shrink-0 shadow-xs">
              KM
            </div>
            <div className="min-w-0 flex-1">
              <div className="text-sm font-semibold text-[#10231C] truncate">Khamis M.</div>
              <div className="text-[11px] text-[#68756F] truncate">Zawadi Emporium</div>
            </div>
            <ChevronRight className="w-4 h-4 text-[#68756F]" />
          </button>
        </div>
      </aside>
    </>;
};
export default Sidebar;
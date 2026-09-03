import { useState, useRef, useEffect } from "react";
import {
  Search,
  Bell,
  LogOut,
  User,
  CreditCard,
  Settings,
  Layers,
  ChevronDown
} from "lucide-react";
export const TopHeader = ({
  activePage,
  currentPage,
  currentUser,
  unreadCount,
  unreadNotificationsCount,
  onNavigate,
  onOpenCommandPalette,
  onToggleMobileMenu
}) => {
  const current = currentPage || activePage || "dashboard";
  const notifCount = unreadCount ?? unreadNotificationsCount ?? 0;
  const [profileDropdownOpen, setProfileDropdownOpen] = useState(false);
  const [pageSwitcherOpen, setPageSwitcherOpen] = useState(false);
  const dropdownRef = useRef(null);
  const switcherRef = useRef(null);
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setProfileDropdownOpen(false);
      }
      if (switcherRef.current && !switcherRef.current.contains(event.target)) {
        setPageSwitcherOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);
  const getPageTitle = (page) => {
    switch (page) {
      case "dashboard":
        return "Dashboard Overview";
      case "inbox":
        return "Unified Inbox";
      case "conversation-detail":
        return "Conversation Detail";
      case "customers":
        return "Customer CRM";
      case "ai-agent":
        return "AI Agent Studio";
      case "automations":
        return "Automations & Workflows";
      case "analytics":
        return "Performance Analytics";
      case "channels":
        return "Channels & Integrations";
      case "team":
        return "Team Members";
      case "settings":
        return "Platform Settings";
      case "billing":
        return "Billing & Subscriptions";
      case "notifications":
        return "Notifications & Alerts";
      case "profile":
        return "User Profile";
      case "login":
        return "Sign In (Auth)";
      case "signup":
        return "Create Account (Auth)";
      case "forgot-password":
        return "Password Reset (Auth)";
      default:
        return "Overview";
    }
  };
  const allPages = [
    { id: "dashboard", label: "1. Dashboard Overview", category: "Core" },
    { id: "inbox", label: "2. Unified Inbox", category: "Core" },
    { id: "conversation-detail", label: "3. Conversation Detail", category: "Core" },
    { id: "customers", label: "4. Customer CRM", category: "Core" },
    { id: "ai-agent", label: "5. AI Agent Studio", category: "AI" },
    { id: "automations", label: "6. Automations", category: "AI" },
    { id: "analytics", label: "7. Analytics & Reports", category: "Intelligence" },
    { id: "channels", label: "8. Channels (WA, IG, Email, Calls)", category: "Integrations" },
    { id: "team", label: "9. Team Members", category: "Settings" },
    { id: "settings", label: "10. Platform Settings", category: "Settings" },
    { id: "billing", label: "11. Billing & Usage (TZS)", category: "Settings" },
    { id: "notifications", label: "12. Notifications Center", category: "Core" },
    { id: "profile", label: "13. My Profile", category: "Account" },
    { id: "login", label: "14. Login (Split Screen)", category: "Auth" },
    { id: "signup", label: "15. Sign Up (Split Screen)", category: "Auth" },
    { id: "forgot-password", label: "16. Forgot Password", category: "Auth" }
  ];
  return <header className="h-16 bg-white border-b border-[#E2E4DF] flex items-center justify-between px-4 sm:px-8 sticky top-0 z-20">
      {
    /* Left: Hamburger (mobile), Page Title & View Switcher */
  }
      <div className="flex items-center gap-3">
        {onToggleMobileMenu && <button
    onClick={onToggleMobileMenu}
    className="md:hidden p-1.5 rounded-lg text-[#68756F] hover:bg-[#F7F6F1]"
    title="Toggle Menu"
  >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>}

        <h1 className="text-lg font-semibold text-[#10231C]">
          {getPageTitle(current)}
        </h1>

        {
    /* Quick View Switcher Dropdown */
  }
        <div className="relative" ref={switcherRef}>
          <button
    onClick={() => setPageSwitcherOpen(!pageSwitcherOpen)}
    className="hidden sm:flex items-center gap-1.5 text-xs text-[#287A59] bg-[#287A59]/10 hover:bg-[#287A59]/15 border border-[#287A59]/20 px-2.5 py-1 rounded-full font-medium transition-colors"
    title="Explore all 16 designed views"
  >
            <Layers className="w-3.5 h-3.5" />
            <span>All 16 Views</span>
            <ChevronDown className="w-3 h-3 text-[#287A59]" />
          </button>

          {pageSwitcherOpen && <div className="absolute left-0 mt-2 w-72 bg-white rounded-2xl shadow-lg border border-[#E2E4DF] p-2 z-50 animate-in fade-in zoom-in-95 duration-100 max-h-96 overflow-y-auto">
              <div className="px-2.5 py-1.5 text-[10px] font-bold uppercase tracking-widest text-[#68756F] border-b border-[#E2E4DF] mb-1">
                All 16 App Views
              </div>
              <div className="space-y-0.5">
                {allPages.map((p) => <button
    key={p.id}
    onClick={() => {
      onNavigate(p.id);
      setPageSwitcherOpen(false);
    }}
    className={`w-full text-left px-2.5 py-1.5 rounded-lg text-xs font-medium flex items-center justify-between transition-colors ${current === p.id ? "bg-[#287A59] text-white font-semibold" : "text-[#14201B] hover:bg-[#F7F6F1]"}`}
  >
                    <span>{p.label}</span>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded ${current === p.id ? "bg-white/20 text-white" : "bg-[#E2E4DF] text-[#68756F]"}`}>
                      {p.category}
                    </span>
                  </button>)}
              </div>
            </div>}
        </div>
      </div>

      {
    /* Right: Search, Notifications, Broadcast button, and Profile */
  }
      <div className="flex items-center gap-3 sm:gap-4">
        {
    /* Geometric Balance Rounded-Full Search Bar */
  }
        <div
    onClick={onOpenCommandPalette}
    className="relative cursor-pointer group"
    title="Search conversations... (Cmd+K)"
  >
          <input
    type="text"
    readOnly
    placeholder="Search conversations..."
    className="pl-10 pr-4 py-2 bg-[#F7F6F1] border-none rounded-full text-sm w-44 md:w-64 outline-none focus:ring-1 focus:ring-[#287A59] text-[#14201B] cursor-pointer placeholder:text-[#68756F]"
  />
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-[#68756F] group-hover:text-[#287A59] transition-colors" />
        </div>

        {
    /* Notifications Icon (Circular) */
  }
        <div
    onClick={() => onNavigate("notifications")}
    className="w-8 h-8 flex items-center justify-center text-[#68756F] cursor-pointer hover:text-[#287A59] rounded-full hover:bg-[#F7F6F1] transition-colors relative"
    title="Notifications"
  >
          <Bell className="w-5 h-5" />
          {notifCount > 0 && <span className="absolute top-1 right-1 w-2 h-2 bg-[#287A59] rounded-full ring-2 ring-white" />}
        </div>

        {
    /* Geometric Balance Action Button: New Broadcast */
  }
        <button
    onClick={() => onNavigate("inbox")}
    className="hidden sm:inline-flex bg-[#287A59] text-white px-4 py-2 rounded-full text-sm font-medium hover:bg-[#10231C] transition-colors shadow-2xs"
  >
          New Broadcast
        </button>

        {
    /* User Profile Menu */
  }
        <div className="relative" ref={dropdownRef}>
          <button
    onClick={() => setProfileDropdownOpen(!profileDropdownOpen)}
    className="w-8 h-8 rounded-full bg-[#10231C] text-white flex items-center justify-center font-bold text-xs hover:ring-2 hover:ring-[#287A59] transition-all cursor-pointer"
  >
            BK
          </button>

          {profileDropdownOpen && <div className="absolute right-0 mt-2 w-56 bg-white rounded-2xl shadow-lg border border-[#E2E4DF] p-2 z-50 animate-in fade-in zoom-in-95 duration-100">
              <div className="px-3 py-2 border-b border-[#E2E4DF]">
                <p className="text-xs font-bold text-[#10231C]">Baraka K.</p>
                <p className="text-[11px] text-[#68756F] truncate">Baraka Electronics</p>
                <div className="mt-1 flex items-center gap-1 text-[10px] text-[#287A59] font-semibold">
                  <span>● Dar es Salaam, Tanzania</span>
                </div>
              </div>

              <div className="py-1">
                <button
    onClick={() => {
      onNavigate("profile");
      setProfileDropdownOpen(false);
    }}
    className="w-full flex items-center gap-2.5 px-3 py-1.5 text-xs text-[#14201B] hover:bg-[#F7F6F1] rounded-lg transition-colors"
  >
                  <User className="w-3.5 h-3.5 text-[#68756F]" />
                  <span>My Profile</span>
                </button>
                <button
    onClick={() => {
      onNavigate("billing");
      setProfileDropdownOpen(false);
    }}
    className="w-full flex items-center gap-2.5 px-3 py-1.5 text-xs text-[#14201B] hover:bg-[#F7F6F1] rounded-lg transition-colors"
  >
                  <CreditCard className="w-3.5 h-3.5 text-[#68756F]" />
                  <span>Billing & Subscription</span>
                </button>
                <button
    onClick={() => {
      onNavigate("settings");
      setProfileDropdownOpen(false);
    }}
    className="w-full flex items-center gap-2.5 px-3 py-1.5 text-xs text-[#14201B] hover:bg-[#F7F6F1] rounded-lg transition-colors"
  >
                  <Settings className="w-3.5 h-3.5 text-[#68756F]" />
                  <span>Settings</span>
                </button>
              </div>

              <div className="border-t border-[#E2E4DF] pt-1">
                <button
    onClick={() => {
      onNavigate("login");
      setProfileDropdownOpen(false);
    }}
    className="w-full flex items-center gap-2.5 px-3 py-1.5 text-xs text-[#14201B] hover:bg-[#F7F6F1] rounded-lg transition-colors"
  >
                  <LogOut className="w-3.5 h-3.5 text-[#68756F]" />
                  <span>Sign In Screen</span>
                </button>
              </div>
            </div>}
        </div>
      </div>
    </header>;
};
export default TopHeader;
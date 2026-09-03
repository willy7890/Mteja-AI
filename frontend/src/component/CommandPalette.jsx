import { useState, useEffect } from "react";
import {
  Search,
  Bot,
  Inbox,
  Users,
  LayoutDashboard,
  Zap,
  BarChart3,
  MessageSquare,
  Settings,
  CreditCard,
  User,
  Bell,
  X,
  ArrowRight
} from "lucide-react";
export const CommandPalette = ({
  isOpen,
  onClose,
  onNavigate
}) => {
  const [query, setQuery] = useState("");
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        if (isOpen) onClose();
        else {
        }
      }
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);
  if (!isOpen) return null;
  const actions = [
    { label: "Go to Dashboard Overview", page: "dashboard", icon: LayoutDashboard, category: "Pages" },
    { label: "Open Unified Inbox (4 unread)", page: "inbox", icon: Inbox, category: "Pages" },
    { label: "View Customers CRM & Profiles", page: "customers", icon: Users, category: "Pages" },
    { label: "AI Agent Studio & Simulator", page: "ai-agent", icon: Bot, category: "AI Tools" },
    { label: "Automations & Workflow Builder", page: "automations", icon: Zap, category: "AI Tools" },
    { label: "Analytics & Conversation Volume", page: "analytics", icon: BarChart3, category: "Intelligence" },
    { label: "Channels & Integrations (WhatsApp, IG)", page: "channels", icon: MessageSquare, category: "Channels" },
    { label: "Team Members & Roles", page: "team", icon: Users, category: "Settings" },
    { label: "Billing & Usage Limits (TZS)", page: "billing", icon: CreditCard, category: "Settings" },
    { label: "Platform Settings & AI Voice", page: "settings", icon: Settings, category: "Settings" },
    { label: "Notifications & Alerts", page: "notifications", icon: Bell, category: "Alerts" },
    { label: "User Profile & Preferences", page: "profile", icon: User, category: "Account" },
    { label: "Switch to Login Screen", page: "login", icon: ArrowRight, category: "Auth" },
    { label: "Switch to Sign Up Screen", page: "signup", icon: ArrowRight, category: "Auth" }
  ];
  const filtered = actions.filter(
    (a) => a.label.toLowerCase().includes(query.toLowerCase()) || a.category.toLowerCase().includes(query.toLowerCase())
  );
  return <div className="fixed inset-0 z-50 flex items-start justify-center pt-24 px-4 bg-[#10231C]/40 backdrop-blur-xs animate-in fade-in duration-150">
      <div className="w-full max-w-xl bg-white rounded-2xl shadow-2xl border border-[#E2E4DF] overflow-hidden">
        {
    /* Search Header */
  }
        <div className="flex items-center px-4 py-3 border-b border-[#E2E4DF]">
          <Search className="w-4 h-4 text-[#68756F] mr-3" />
          <input
    type="text"
    placeholder="Type a page, command, or customer search..."
    value={query}
    onChange={(e) => setQuery(e.target.value)}
    autoFocus
    className="w-full bg-transparent text-sm text-[#10231C] placeholder-[#68756F] focus:outline-none"
  />
          <button
    onClick={onClose}
    className="p-1 rounded-md text-[#68756F] hover:bg-[#F7F6F1]"
  >
            <X className="w-4 h-4" />
          </button>
        </div>

        {
    /* Results List */
  }
        <div className="max-h-80 overflow-y-auto p-2 space-y-1">
          {filtered.length === 0 ? <div className="py-8 text-center text-xs text-[#68756F]">
              No matching pages or commands found for "{query}".
            </div> : filtered.map((item, idx) => {
    const Icon = item.icon;
    return <button
      key={idx}
      onClick={() => {
        onNavigate(item.page);
        onClose();
      }}
      className="w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-medium text-[#14201B] hover:bg-[#F7F6F1] hover:text-[#10231C] transition-colors text-left group"
    >
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 rounded-md bg-[#287A59]/10 text-[#287A59] flex items-center justify-center">
                      <Icon className="w-3.5 h-3.5" />
                    </div>
                    <span>{item.label}</span>
                  </div>
                  <span className="text-[10px] text-[#68756F] uppercase font-semibold px-2 py-0.5 rounded bg-gray-100 group-hover:bg-gray-200">
                    {item.category}
                  </span>
                </button>;
  })}
        </div>

        <div className="px-4 py-2 bg-[#F7F6F1] border-t border-[#E2E4DF] flex items-center justify-between text-[11px] text-[#68756F]">
          <span>Use <b>↑</b> <b>↓</b> to navigate</span>
          <span><b>ESC</b> to close</span>
        </div>
      </div>
    </div>;
};
export default CommandPalette;
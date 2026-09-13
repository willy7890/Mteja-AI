import React, { useState } from 'react';
import {
  Bell,
  CheckCircle2,
  Sparkles,
  AlertTriangle,
  User,
  Clock,
  ArrowRight,
  Filter,
  CheckCheck
} from 'lucide-react';
import { NotificationItem, PageId } from '../../types';

interface NotificationsPageProps {
  notifications: NotificationItem[];
  onNavigate: (page: PageId) => void;
  onSelectConversation?: (id: string) => void;
}

export const NotificationsPage: React.FC<NotificationsPageProps> = ({
  notifications: initialNotifications,
  onNavigate,
  onSelectConversation,
}) => {
  const [notifications, setNotifications] = useState<NotificationItem[]>(initialNotifications);
  const [filter, setFilter] = useState<'all' | 'ai' | 'escalation' | 'customer' | 'system'>('all');

  const handleMarkAllRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, unread: false })));
  };

  const filtered = notifications.filter((n) => {
    if (filter === 'all') return true;
    return n.type === filter;
  });

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'escalation':
        return (
          <div className="w-8 h-8 rounded-full bg-amber-100 text-amber-800 flex items-center justify-center flex-shrink-0">
            <AlertTriangle className="w-4 h-4" />
          </div>
        );
      case 'ai':
        return (
          <div className="w-8 h-8 rounded-full bg-[#287A59]/15 text-[#287A59] flex items-center justify-center flex-shrink-0">
            <Sparkles className="w-4 h-4" />
          </div>
        );
      case 'customer':
        return (
          <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center flex-shrink-0">
            <User className="w-4 h-4" />
          </div>
        );
      default:
        return (
          <div className="w-8 h-8 rounded-full bg-[#10231C]/10 text-[#10231C] flex items-center justify-center flex-shrink-0">
            <Bell className="w-4 h-4" />
          </div>
        );
    }
  };

  return (
    <div className="p-6 md:p-8 max-w-4xl mx-auto space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-[#10231C] tracking-tight">Notifications Center</h2>
          <p className="text-xs text-[#68756F] mt-1">
            Real-time escalation alerts, autonomous AI milestones, and customer events.
          </p>
        </div>

        <button
          onClick={handleMarkAllRead}
          className="inline-flex items-center gap-1.5 text-xs text-[#287A59] font-bold hover:underline"
        >
          <CheckCheck className="w-4 h-4" />
          <span>Mark all as read</span>
        </button>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-1.5 border-b border-[#E2E4DF] pb-2">
        {[
          { id: 'all', label: 'All' },
          { id: 'escalation', label: 'Escalations' },
          { id: 'ai', label: 'AI Actions' },
          { id: 'customer', label: 'Customer Activity' },
          { id: 'system', label: 'System' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setFilter(tab.id as any)}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
              filter === tab.id
                ? 'bg-[#10231C] text-white'
                : 'text-[#68756F] hover:bg-[#F7F6F1] hover:text-[#10231C]'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Notifications List */}
      <div className="bg-white rounded-2xl border border-[#E2E4DF] shadow-2xs divide-y divide-[#E2E4DF] overflow-hidden">
        {filtered.length === 0 ? (
          <div className="p-12 text-center text-xs text-[#68756F]">
            No notifications in this category.
          </div>
        ) : (
          filtered.map((item) => (
            <div
              key={item.id}
              onClick={() => {
                if (item.conversationId && onSelectConversation) {
                  onSelectConversation(item.conversationId);
                  onNavigate('inbox');
                }
              }}
              className={`p-4 flex items-start gap-3.5 transition-colors cursor-pointer ${
                item.unread ? 'bg-[#287A59]/5' : 'hover:bg-[#F7F6F1]'
              }`}
            >
              {getNotificationIcon(item.type)}

              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2">
                  <h4 className={`text-xs ${item.unread ? 'font-bold text-[#10231C]' : 'font-medium text-[#14201B]'}`}>
                    {item.title}
                  </h4>
                  <span className="text-[10px] text-[#68756F] flex-shrink-0 font-medium">
                    {item.time}
                  </span>
                </div>
                <p className="text-xs text-[#68756F] mt-0.5 leading-relaxed">{item.description}</p>
              </div>

              {item.unread && (
                <span className="w-2 h-2 rounded-full bg-[#287A59] mt-2 flex-shrink-0" />
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};
export default NotificationsPage;
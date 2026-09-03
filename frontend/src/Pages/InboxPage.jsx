import React, { useState } from 'react';
import {
  MessageSquare,
  Instagram,
  Mail,
  PhoneCall,
  Search,
  Filter,
  CheckCircle2,
  Sparkles,
  Send,
  Paperclip,
  Smile,
  Mic,
  MoreVertical,
  User,
  Phone,
  MapPin,
  Tag,
  Clock,
  ArrowRight,
  ShieldCheck,
  CheckCheck,
  AlertCircle,
  Edit3,
  ThumbsUp,
  X,
  ExternalLink,
  ChevronRight,
  RefreshCw,
  ShoppingBag
} from 'lucide-react';
import { Conversation, ConversationFilter, ChannelType, PageId, ChatMessage } from '../../types';

interface InboxPageProps {
  conversations: Conversation[];
  selectedConvId: string;
  onSelectConversation: (id: string) => void;
  onNavigate: (page: PageId) => void;
  channelFilter?: ChannelType | null;
}

export const InboxPage: React.FC<InboxPageProps> = ({
  conversations: initialConversations,
  selectedConvId,
  onSelectConversation,
  onNavigate,
  channelFilter,
}) => {
  const [conversations, setConversations] = useState<Conversation[]>(initialConversations);
  const [filter, setFilter] = useState<ConversationFilter>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [messageInput, setMessageInput] = useState('');
  const [isAiTakeover, setIsAiTakeover] = useState(false);
  const [showRightPanel, setShowRightPanel] = useState(true);
  const [activeSuggestedReplyIndex, setActiveSuggestedReplyIndex] = useState<number | null>(null);

  const activeConv = conversations.find((c) => c.id === selectedConvId) || conversations[0];

  // Filtering conversations
  const filteredConversations = conversations.filter((c) => {
    if (channelFilter && c.channel !== channelFilter) return false;

    if (filter === 'unread' && !c.unread) return false;
    if (filter === 'ai-handled' && !c.isAiHandled) return false;
    if (filter === 'needs-attention' && c.status !== 'escalated' && c.status !== 'needs-attention') return false;
    if (filter === 'assigned' && c.assignedAgent !== 'Khamis Mgofi') return false;

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      return (
        c.customerName.toLowerCase().includes(q) ||
        (c.businessName && c.businessName.toLowerCase().includes(q)) ||
        c.lastMessage.toLowerCase().includes(q) ||
        c.location.toLowerCase().includes(q)
      );
    }
    return true;
  });

  const getChannelBadge = (ch: ChannelType) => {
    switch (ch) {
      case 'whatsapp':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-[#25D366] bg-[#25D366]/10 px-2 py-0.5 rounded-full">
            <MessageSquare className="w-3 h-3" />
            <span>WhatsApp</span>
          </span>
        );
      case 'instagram':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-[#E4405F] bg-[#E4405F]/10 px-2 py-0.5 rounded-full">
            <Instagram className="w-3 h-3" />
            <span>Instagram</span>
          </span>
        );
      case 'email':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-[#4285F4] bg-[#4285F4]/10 px-2 py-0.5 rounded-full">
            <Mail className="w-3 h-3" />
            <span>Email</span>
          </span>
        );
      case 'call':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-[#287A59] bg-[#287A59]/10 px-2 py-0.5 rounded-full">
            <PhoneCall className="w-3 h-3" />
            <span>Phone Voice</span>
          </span>
        );
    }
  };

  const handleSendMessage = (textToSend?: string) => {
    const text = textToSend || messageInput;
    if (!text.trim() || !activeConv) return;

    const newMsg: ChatMessage = {
      id: `msg-${Date.now()}`,
      sender: isAiTakeover ? 'agent' : 'ai',
      senderName: isAiTakeover ? 'Khamis Mgofi (Human)' : 'MtejaAI Assistant',
      text: text.trim(),
      timestamp: 'Just now',
      isAiReplied: !isAiTakeover,
      intentDetected: isAiTakeover ? 'Human Agent Override' : 'Automated Smart Reply',
    };

    setConversations((prev) =>
      prev.map((c) => {
        if (c.id === activeConv.id) {
          return {
            ...c,
            unread: false,
            lastMessage: text.trim(),
            timestamp: 'Just now',
            messages: [...c.messages, newMsg],
          };
        }
        return c;
      })
    );

    setMessageInput('');
  };

  const handleApproveSuggested = (replyText: string) => {
    handleSendMessage(replyText);
  };

  const handleEditSuggested = (replyText: string) => {
    setMessageInput(replyText);
  };

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col md:flex-row overflow-hidden bg-[#FFFFFF]">
      {/* COLUMN 1: Conversation List (Left) */}
      <div className="w-full md:w-80 lg:w-96 border-r border-[#E2E4DF] flex flex-col h-full flex-shrink-0 bg-[#FFFFFF]">
        {/* Search & Header */}
        <div className="p-3.5 border-b border-[#E2E4DF] space-y-2.5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold text-[#10231C]">Conversations</h2>
              <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-[#287A59]/10 text-[#287A59]">
                {filteredConversations.length} Active
              </span>
            </div>
            {channelFilter && (
              <span className="text-[10px] font-bold text-[#68756F] bg-[#F7F6F1] px-2 py-0.5 rounded">
                Filtered: {channelFilter}
              </span>
            )}
          </div>

          {/* Search box */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-[#68756F] absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search by customer or business..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 text-xs rounded-lg border border-[#E2E4DF] bg-[#F7F6F1] focus:bg-white focus:outline-none focus:border-[#287A59] transition-colors placeholder-[#68756F]"
            />
          </div>

          {/* Filter Pills */}
          <div className="flex items-center gap-1 overflow-x-auto pb-1 no-scrollbar text-xs">
            {[
              { id: 'all', label: 'All' },
              { id: 'unread', label: 'Unread' },
              { id: 'ai-handled', label: 'AI Handled' },
              { id: 'needs-attention', label: 'Needs Attention' },
              { id: 'assigned', label: 'Assigned to me' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setFilter(tab.id as ConversationFilter)}
                className={`px-2.5 py-1 rounded-md text-[11px] font-semibold whitespace-nowrap transition-colors ${
                  filter === tab.id
                    ? 'bg-[#10231C] text-white'
                    : 'text-[#68756F] hover:bg-[#F7F6F1] hover:text-[#10231C]'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Conversation List Items */}
        <div className="flex-1 overflow-y-auto divide-y divide-[#E2E4DF]">
          {filteredConversations.length === 0 ? (
            <div className="p-8 text-center text-xs text-[#68756F]">
              No conversations match the current filter.
            </div>
          ) : (
            filteredConversations.map((conv) => {
              const isSelected = conv.id === activeConv?.id;
              return (
                <div
                  key={conv.id}
                  onClick={() => onSelectConversation(conv.id)}
                  className={`p-3.5 cursor-pointer transition-colors relative flex items-start gap-3 ${
                    isSelected ? 'bg-[#287A59]/5 border-l-3 border-[#287A59]' : 'hover:bg-[#F7F6F1]'
                  }`}
                >
                  {/* Avatar with unread ring */}
                  <div className="relative flex-shrink-0">
                    <img
                      src={conv.avatar}
                      alt={conv.customerName}
                      className="w-10 h-10 rounded-full object-cover border border-[#E2E4DF]"
                    />
                    {conv.unread && (
                      <span className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 bg-[#287A59] border-2 border-white rounded-full" />
                    )}
                  </div>

                  <div className="min-w-0 flex-1">
                    <div className="flex items-center justify-between gap-1">
                      <div className="flex items-center gap-1.5 truncate">
                        <span className={`text-xs truncate ${conv.unread ? 'font-bold text-[#10231C]' : 'font-medium text-[#14201B]'}`}>
                          {conv.customerName}
                        </span>
                        {conv.businessName && (
                          <span className="text-[11px] text-[#68756F] truncate hidden sm:inline">
                            • {conv.businessName}
                          </span>
                        )}
                      </div>
                      <span className="text-[10px] text-[#68756F] flex-shrink-0 font-medium">
                        {conv.timestamp}
                      </span>
                    </div>

                    <p className={`text-xs truncate mt-0.5 ${conv.unread ? 'font-semibold text-[#10231C]' : 'text-[#68756F]'}`}>
                      {conv.lastMessage}
                    </p>

                    {/* Metadata tags */}
                    <div className="mt-2 flex items-center justify-between">
                      <div className="flex items-center gap-1.5">
                        {getChannelBadge(conv.channel)}
                        {conv.priority === 'high' && (
                          <span className="text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded bg-amber-100 text-amber-800">
                            High Priority
                          </span>
                        )}
                      </div>

                      {conv.isAiHandled && (
                        <span className="text-[10px] text-[#287A59] font-bold flex items-center gap-1">
                          <Sparkles className="w-3 h-3" />
                          <span>AI active</span>
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* COLUMN 2: Active Conversation & Detail (Center) */}
      <div className="flex-1 flex flex-col h-full bg-[#F7F6F1] min-w-0">
        {activeConv ? (
          <>
            {/* Conversation Header */}
            <div className="h-16 px-6 bg-white border-b border-[#E2E4DF] flex items-center justify-between flex-shrink-0">
              <div className="flex items-center gap-3 min-w-0">
                <img
                  src={activeConv.avatar}
                  alt={activeConv.customerName}
                  className="w-10 h-10 rounded-full object-cover border border-[#E2E4DF]"
                />
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <h3 className="text-sm font-bold text-[#10231C] truncate">
                      {activeConv.customerName}
                    </h3>
                    <span className="w-2 h-2 rounded-full bg-[#35D98A]" title="Online" />
                    {activeConv.businessName && (
                      <span className="text-xs text-[#68756F] truncate hidden sm:inline">
                        ({activeConv.businessName})
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-2 text-xs text-[#68756F]">
                    {getChannelBadge(activeConv.channel)}
                    <span>• {activeConv.phone}</span>
                    <span className="hidden md:inline">• {activeConv.location}</span>
                  </div>
                </div>
              </div>

              {/* Header Action Controls */}
              <div className="flex items-center gap-2 flex-shrink-0">
                {/* Take over / AI toggle */}
                <button
                  onClick={() => setIsAiTakeover(!isAiTakeover)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all shadow-2xs ${
                    isAiTakeover
                      ? 'bg-amber-100 text-amber-900 border border-amber-300'
                      : 'bg-[#287A59]/10 text-[#287A59] border border-[#287A59]/20 hover:bg-[#287A59]/20'
                  }`}
                  title="Switch between automated AI responses and human agent mode"
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>{isAiTakeover ? 'Human Agent Mode' : 'AI Autopilot (Active)'}</span>
                </button>

                {/* Toggle Right Panel button */}
                <button
                  onClick={() => setShowRightPanel(!showRightPanel)}
                  className={`p-2 rounded-lg border transition-colors ${
                    showRightPanel ? 'bg-[#F7F6F1] border-[#E2E4DF] text-[#10231C]' : 'border-transparent text-[#68756F]'
                  }`}
                  title="Toggle customer details panel"
                >
                  <User className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Conversation Messages Scroll Area */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {/* Channel Security / Encryption notice */}
              <div className="flex items-center justify-center">
                <span className="inline-flex items-center gap-1 text-[11px] text-[#68756F] bg-white border border-[#E2E4DF] px-3 py-1 rounded-full shadow-2xs">
                  <ShieldCheck className="w-3.5 h-3.5 text-[#287A59]" />
                  <span>MtejaAI verified end-to-end sync with {activeConv.channel}</span>
                </span>
              </div>

              {activeConv.messages.map((msg) => {
                const isCustomer = msg.sender === 'customer';
                const isAi = msg.sender === 'ai';
                const isAgent = msg.sender === 'agent';

                return (
                  <div
                    key={msg.id}
                    className={`flex flex-col ${isCustomer ? 'items-start' : 'items-end'}`}
                  >
                    {/* Sender label & Timestamp */}
                    <div className="flex items-center gap-2 mb-1 px-1 text-[11px] text-[#68756F]">
                      <span className="font-semibold text-[#10231C]">{msg.senderName}</span>
                      <span>• {msg.timestamp}</span>
                      {isAi && (
                        <span className="inline-flex items-center gap-1 text-[10px] font-bold text-[#287A59] bg-[#287A59]/10 px-1.5 py-0.2 rounded">
                          <Sparkles className="w-2.5 h-2.5" />
                          AI replied
                        </span>
                      )}
                      {isAgent && (
                        <span className="inline-flex items-center gap-1 text-[10px] font-bold text-blue-700 bg-blue-100 px-1.5 py-0.2 rounded">
                          Human Agent
                        </span>
                      )}
                    </div>

                    {/* Message Bubble */}
                    <div
                      className={`max-w-lg rounded-2xl p-4 text-xs leading-relaxed shadow-2xs relative ${
                        isCustomer
                          ? 'bg-white text-[#14201B] border border-[#E2E4DF] rounded-tl-sm'
                          : isAi
                          ? 'bg-[#10231C] text-white rounded-tr-sm'
                          : 'bg-[#287A59] text-white rounded-tr-sm'
                      }`}
                    >
                      <p>{msg.text}</p>

                      {/* Attachments if any */}
                      {msg.attachments && msg.attachments.length > 0 && (
                        <div className="mt-3 pt-2 border-t border-white/20 space-y-2">
                          {msg.attachments.map((att, idx) => (
                            <div
                              key={idx}
                              className="flex items-center justify-between p-2 rounded-lg bg-white/10 text-[11px]"
                            >
                              <div className="flex items-center gap-2">
                                <Paperclip className="w-3.5 h-3.5" />
                                <span>{att.name}</span>
                              </div>
                              <span className="text-[#35D98A] font-bold">{att.duration || att.size}</span>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Intent detection metadata */}
                      {msg.intentDetected && (
                        <div className="mt-2.5 pt-2 border-t border-white/15 flex items-center justify-between text-[10px] text-[#D5D8D1]">
                          <span>Intent: <b>{msg.intentDetected}</b></span>
                          <CheckCheck className="w-3.5 h-3.5 text-[#35D98A]" />
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}

              {/* AI Suggested Replies Box (Crucial MtejaAI Feature) */}
              {activeConv.aiSuggestedReplies && activeConv.aiSuggestedReplies.length > 0 && (
                <div className="my-4 p-4 rounded-2xl bg-white border border-[#287A59]/30 shadow-xs space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1.5 text-xs font-bold text-[#10231C]">
                      <Sparkles className="w-4 h-4 text-[#287A59]" />
                      <span>AI Suggested Instant Replies</span>
                      <span className="text-[10px] font-semibold text-[#287A59] bg-[#287A59]/10 px-2 py-0.5 rounded-full">
                        {activeConv.aiConfidence || 95}% confidence
                      </span>
                    </div>
                    <span className="text-[11px] text-[#68756F]">Trained on Swahili & English</span>
                  </div>

                  <div className="space-y-2">
                    {activeConv.aiSuggestedReplies.map((reply, idx) => (
                      <div
                        key={idx}
                        className="p-3 rounded-xl bg-[#F7F6F1] border border-[#E2E4DF] hover:border-[#287A59]/40 transition-colors flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                      >
                        <p className="text-xs text-[#14201B] font-medium leading-relaxed flex-1">
                          "{reply}"
                        </p>

                        <div className="flex items-center gap-1.5 flex-shrink-0">
                          <button
                            type="button"
                            onClick={() => handleApproveSuggested(reply)}
                            className="px-2.5 py-1.5 rounded-lg bg-[#287A59] hover:bg-[#1f5f45] text-white text-[11px] font-bold flex items-center gap-1 shadow-2xs"
                            title="Send reply immediately"
                          >
                            <ThumbsUp className="w-3 h-3" />
                            <span>Approve & Send</span>
                          </button>

                          <button
                            type="button"
                            onClick={() => handleEditSuggested(reply)}
                            className="px-2.5 py-1.5 rounded-lg bg-white border border-[#E2E4DF] hover:bg-[#EAE8E0] text-[#14201B] text-[11px] font-semibold flex items-center gap-1"
                            title="Load into editor to customize"
                          >
                            <Edit3 className="w-3 h-3 text-[#68756F]" />
                            <span>Edit</span>
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Message Composer */}
            <div className="p-4 bg-white border-t border-[#E2E4DF]">
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSendMessage();
                }}
                className="space-y-3"
              >
                <div className="relative">
                  <textarea
                    rows={2}
                    value={messageInput}
                    onChange={(e) => setMessageInput(e.target.value)}
                    placeholder={
                      isAiTakeover
                        ? 'Type human response as Khamis Mgofi (override mode)...'
                        : 'Type message or customize AI response...'
                    }
                    className="w-full p-3 text-xs rounded-xl border border-[#E2E4DF] bg-[#F7F6F1] focus:bg-white focus:outline-none focus:border-[#287A59] transition-colors resize-none placeholder-[#68756F]"
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleSendMessage();
                      }
                    }}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1 text-[#68756F]">
                    <button
                      type="button"
                      className="p-1.5 rounded-lg hover:bg-[#F7F6F1] hover:text-[#10231C]"
                      title="Attach file / image / catalogue link"
                    >
                      <Paperclip className="w-4 h-4" />
                    </button>
                    <button
                      type="button"
                      className="p-1.5 rounded-lg hover:bg-[#F7F6F1] hover:text-[#10231C]"
                      title="Insert emoji"
                    >
                      <Smile className="w-4 h-4" />
                    </button>
                    <button
                      type="button"
                      className="p-1.5 rounded-lg hover:bg-[#F7F6F1] hover:text-[#10231C]"
                      title="Record Swahili/English voice message"
                    >
                      <Mic className="w-4 h-4" />
                    </button>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => setIsAiTakeover(!isAiTakeover)}
                      className="text-xs text-[#287A59] font-bold hover:underline"
                    >
                      {isAiTakeover ? 'Hand back to AI' : 'Take over conversation'}
                    </button>

                    <button
                      type="submit"
                      disabled={!messageInput.trim()}
                      className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#287A59] hover:bg-[#1f5f45] disabled:opacity-50 text-white text-xs font-bold transition-all shadow-2xs"
                    >
                      <span>Send</span>
                      <Send className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </form>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center p-8 text-center text-[#68756F]">
            Select a conversation to begin chatting.
          </div>
        )}
      </div>

      {/* COLUMN 3: Customer Information (Right) */}
      {showRightPanel && activeConv && (
        <div className="w-full md:w-80 lg:w-88 border-l border-[#E2E4DF] bg-white flex flex-col h-full flex-shrink-0 overflow-y-auto">
          {/* Header */}
          <div className="p-4 border-b border-[#E2E4DF] flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-[#10231C]">
              Customer Information
            </h3>
            <button
              onClick={() => onNavigate('customers')}
              className="text-xs text-[#287A59] font-bold hover:underline flex items-center gap-1"
            >
              Full Profile <ExternalLink className="w-3 h-3" />
            </button>
          </div>

          <div className="p-5 space-y-6">
            {/* Customer Profile Card */}
            <div className="text-center space-y-2">
              <img
                src={activeConv.avatar}
                alt={activeConv.customerName}
                className="w-16 h-16 rounded-full mx-auto object-cover border-2 border-[#E2E4DF]"
              />
              <div>
                <h4 className="text-sm font-bold text-[#10231C]">{activeConv.customerName}</h4>
                {activeConv.businessName && (
                  <p className="text-xs text-[#68756F]">{activeConv.businessName}</p>
                )}
              </div>
              <div className="flex justify-center gap-1.5">
                {activeConv.customerTags.map((tag, i) => (
                  <span
                    key={i}
                    className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-[#F7F6F1] border border-[#E2E4DF] text-[#14201B]"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>

            {/* Quick Metrics */}
            <div className="grid grid-cols-2 gap-2.5 p-3 rounded-xl bg-[#F7F6F1] border border-[#E2E4DF]">
              <div>
                <span className="text-[11px] text-[#68756F]">Lifetime Value</span>
                <p className="text-xs font-bold text-[#10231C] mt-0.5">{activeConv.totalValueTzs}</p>
              </div>
              <div>
                <span className="text-[11px] text-[#68756F]">Assigned Agent</span>
                <p className="text-xs font-bold text-[#287A59] mt-0.5">{activeConv.assignedAgent}</p>
              </div>
            </div>

            {/* Contact details */}
            <div className="space-y-3">
              <div className="text-[11px] font-bold uppercase tracking-wider text-[#68756F]">
                Contact Info
              </div>
              <div className="space-y-2 text-xs">
                <div className="flex items-center gap-2.5 text-[#14201B]">
                  <Phone className="w-3.5 h-3.5 text-[#68756F]" />
                  <span>{activeConv.phone}</span>
                </div>
                <div className="flex items-center gap-2.5 text-[#14201B]">
                  <MapPin className="w-3.5 h-3.5 text-[#68756F]" />
                  <span>{activeConv.location}</span>
                </div>
                <div className="flex items-center gap-2.5 text-[#14201B]">
                  <Clock className="w-3.5 h-3.5 text-[#68756F]" />
                  <span>Last active: {activeConv.timestamp}</span>
                </div>
              </div>
            </div>

            {/* AI Customer Memory / Insights */}
            <div className="space-y-2 p-3.5 rounded-xl bg-[#287A59]/5 border border-[#287A59]/20">
              <div className="flex items-center gap-1.5 text-xs font-bold text-[#10231C]">
                <Sparkles className="w-3.5 h-3.5 text-[#287A59]" />
                <span>AI Customer Memory</span>
              </div>
              <p className="text-xs text-[#68756F] leading-relaxed">
                Customer operates in {activeConv.location}. Frequently requests express dispatch via Lipa Namba and responds enthusiastically to product catalog links.
              </p>
            </div>

            {/* Recent Orders / Purchase History */}
            <div className="space-y-2.5">
              <div className="text-[11px] font-bold uppercase tracking-wider text-[#68756F]">
                Recent Inquiries & Orders
              </div>
              <div className="p-2.5 rounded-lg border border-[#E2E4DF] text-xs space-y-1 bg-white">
                <div className="flex items-center justify-between font-semibold text-[#10231C]">
                  <span>Hydrating Rose Toner (12 pcs)</span>
                  <span className="text-[#287A59]">TZS 348,000</span>
                </div>
                <div className="flex justify-between text-[10px] text-[#68756F]">
                  <span>28 Aug 2026</span>
                  <span className="text-emerald-700 font-medium">Delivered (Kinondoni)</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
export default InboxPage;
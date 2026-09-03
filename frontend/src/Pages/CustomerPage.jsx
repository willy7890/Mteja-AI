import React, { useState } from 'react';
import {
  Users,
  Search,
  Filter,
  Plus,
  MessageSquare,
  Instagram,
  Mail,
  PhoneCall,
  MapPin,
  Clock,
  Phone,
  Tag,
  DollarSign,
  Calendar,
  Sparkles,
  ExternalLink,
  ChevronRight,
  X,
  FileText,
  ShoppingBag,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { Customer, PageId, ChannelType } from '../../types';

interface CustomersPageProps {
  customers: Customer[];
  onNavigate: (page: PageId) => void;
  onOpenConversationWithCustomer?: (channel: ChannelType) => void;
}

export const CustomersPage: React.FC<CustomersPageProps> = ({
  customers,
  onNavigate,
  onOpenConversationWithCustomer,
}) => {
  const [filter, setFilter] = useState<'all' | 'new' | 'returning' | 'vip' | 'lead' | 'customers'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(customers[0]);
  const [showAddCustomerModal, setShowAddCustomerModal] = useState(false);

  // New customer form state
  const [newCustName, setNewCustName] = useState('');
  const [newCustPhone, setNewCustPhone] = useState('+255 7');
  const [newCustCompany, setNewCustCompany] = useState('');
  const [newCustLocation, setNewCustLocation] = useState('Dar es Salaam');

  const filteredCustomers = customers.filter((c) => {
    if (filter === 'new' && c.status !== 'new') return false;
    if (filter === 'returning' && c.status !== 'returning') return false;
    if (filter === 'vip' && c.status !== 'vip') return false;
    if (filter === 'lead' && c.status !== 'lead') return false;
    if (filter === 'customers' && (c.status === 'lead' || c.status === 'new')) return false;

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      return (
        c.name.toLowerCase().includes(q) ||
        (c.company && c.company.toLowerCase().includes(q)) ||
        c.phone.toLowerCase().includes(q) ||
        c.email.toLowerCase().includes(q) ||
        c.location.toLowerCase().includes(q)
      );
    }
    return true;
  });

  const getChannelIcon = (ch: ChannelType) => {
    switch (ch) {
      case 'whatsapp': return <MessageSquare className="w-3.5 h-3.5 text-[#25D366]" />;
      case 'instagram': return <Instagram className="w-3.5 h-3.5 text-[#E4405F]" />;
      case 'email': return <Mail className="w-3.5 h-3.5 text-[#4285F4]" />;
      case 'call': return <PhoneCall className="w-3.5 h-3.5 text-[#287A59]" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'vip':
        return <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800">VIP</span>;
      case 'lead':
        return <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-blue-100 text-blue-800">Hot Lead</span>;
      case 'returning':
        return <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">Returning</span>;
      case 'new':
        return <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-purple-100 text-purple-800">New Inbound</span>;
      default:
        return <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-gray-100 text-gray-800">Customer</span>;
    }
  };

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-[#10231C] tracking-tight">Customer CRM</h2>
          <p className="text-xs text-[#68756F] mt-1">
            Track customer contact histories, lifetime values, AI summaries, and channel interactions across Tanzania.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={() => setShowAddCustomerModal(true)}
            className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl bg-[#287A59] hover:bg-[#1f5f45] text-white text-xs font-bold transition-colors shadow-2xs"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Add Customer</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-3 rounded-2xl border border-[#E2E4DF] flex flex-col md:flex-row md:items-center justify-between gap-3 shadow-2xs">
        {/* Search */}
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-[#68756F] absolute left-3.5 top-2.5" />
          <input
            type="text"
            placeholder="Search by name, company, phone (+255), or location..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 text-xs rounded-xl border border-[#E2E4DF] bg-[#F7F6F1] focus:bg-white focus:outline-none focus:border-[#287A59] transition-colors"
          />
        </div>

        {/* Filters */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 md:pb-0">
          {[
            { id: 'all', label: 'All' },
            { id: 'new', label: 'New' },
            { id: 'returning', label: 'Returning' },
            { id: 'vip', label: 'VIP' },
            { id: 'lead', label: 'Leads' },
            { id: 'customers', label: 'Customers' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setFilter(tab.id as any)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-colors ${
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

      {/* CRM Main Layout: Table + Details Slide-over/Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Table View (Cols 7 or 8) */}
        <div className="lg:col-span-7 xl:col-span-8 bg-white rounded-2xl border border-[#E2E4DF] shadow-2xs overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-[#E2E4DF] bg-[#F7F6F1] text-[#68756F] font-semibold">
                  <th className="py-3 px-4">Customer</th>
                  <th className="py-3 px-3">Channel</th>
                  <th className="py-3 px-3">Last Interaction</th>
                  <th className="py-3 px-3">Status</th>
                  <th className="py-3 px-3 hidden md:table-cell">Assigned</th>
                  <th className="py-3 px-4 text-right">Total Value</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E2E4DF]">
                {filteredCustomers.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="py-12 text-center text-xs text-[#68756F]">
                      No customers match your query.
                    </td>
                  </tr>
                ) : (
                  filteredCustomers.map((cust) => {
                    const isSelected = selectedCustomer?.id === cust.id;
                    return (
                      <tr
                        key={cust.id}
                        onClick={() => setSelectedCustomer(cust)}
                        className={`cursor-pointer transition-colors ${
                          isSelected ? 'bg-[#287A59]/10' : 'hover:bg-[#F7F6F1]'
                        }`}
                      >
                        {/* Customer & Company */}
                        <td className="py-3.5 px-4">
                          <div className="font-bold text-[#10231C]">{cust.name}</div>
                          {cust.company && (
                            <div className="text-[11px] text-[#68756F]">{cust.company}</div>
                          )}
                          <div className="text-[10px] text-[#68756F] mt-0.5">{cust.location}</div>
                        </td>

                        {/* Channel */}
                        <td className="py-3.5 px-3">
                          <div className="flex items-center gap-1.5 capitalize text-[#14201B] font-medium">
                            {getChannelIcon(cust.channel)}
                            <span>{cust.channel}</span>
                          </div>
                        </td>

                        {/* Last Interaction */}
                        <td className="py-3.5 px-3 text-[#68756F]">
                          {cust.lastInteraction}
                        </td>

                        {/* Status */}
                        <td className="py-3.5 px-3">
                          {getStatusBadge(cust.status)}
                        </td>

                        {/* Assigned Agent */}
                        <td className="py-3.5 px-3 hidden md:table-cell text-[#14201B]">
                          {cust.assignedAgent}
                        </td>

                        {/* Total Value */}
                        <td className="py-3.5 px-4 text-right font-bold text-[#10231C]">
                          {cust.totalValue}
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Customer Profile Side Panel (Cols 5 or 4) */}
        <div className="lg:col-span-5 xl:col-span-4 bg-white rounded-2xl border border-[#E2E4DF] p-6 shadow-2xs space-y-6 sticky top-20">
          {selectedCustomer ? (
            <>
              {/* Profile Header */}
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-base font-bold text-[#10231C]">{selectedCustomer.name}</h3>
                    {getStatusBadge(selectedCustomer.status)}
                  </div>
                  {selectedCustomer.company && (
                    <p className="text-xs font-medium text-[#68756F] mt-0.5">{selectedCustomer.company}</p>
                  )}
                </div>
                <button
                  onClick={() => onNavigate('inbox')}
                  className="px-2.5 py-1.5 rounded-lg bg-[#287A59] text-white text-xs font-bold hover:bg-[#1f5f45] transition-colors flex items-center gap-1 shadow-2xs"
                >
                  <MessageSquare className="w-3 h-3" />
                  <span>Open Chat</span>
                </button>
              </div>

              {/* Contact Information */}
              <div className="p-3.5 rounded-xl bg-[#F7F6F1] border border-[#E2E4DF] space-y-2 text-xs">
                <div className="flex items-center justify-between text-[#14201B]">
                  <span className="text-[#68756F] flex items-center gap-1.5">
                    <Phone className="w-3.5 h-3.5" /> Phone
                  </span>
                  <span className="font-semibold">{selectedCustomer.phone}</span>
                </div>
                <div className="flex items-center justify-between text-[#14201B]">
                  <span className="text-[#68756F] flex items-center gap-1.5">
                    <Mail className="w-3.5 h-3.5" /> Email
                  </span>
                  <span className="font-semibold">{selectedCustomer.email}</span>
                </div>
                <div className="flex items-center justify-between text-[#14201B]">
                  <span className="text-[#68756F] flex items-center gap-1.5">
                    <MapPin className="w-3.5 h-3.5" /> Location
                  </span>
                  <span className="font-semibold">{selectedCustomer.location}</span>
                </div>
              </div>

              {/* AI Summary Box */}
              <div className="p-4 rounded-xl bg-[#287A59]/5 border border-[#287A59]/20 space-y-2">
                <div className="flex items-center gap-1.5 text-xs font-bold text-[#10231C]">
                  <Sparkles className="w-3.5 h-3.5 text-[#287A59]" />
                  <span>AI Customer Profile Summary</span>
                </div>
                <p className="text-xs text-[#68756F] leading-relaxed">
                  {selectedCustomer.aiSummary}
                </p>
              </div>

              {/* Customer Tags */}
              <div className="space-y-1.5">
                <div className="text-[11px] font-bold text-[#68756F] uppercase tracking-wider">
                  Customer Tags
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {selectedCustomer.tags.map((t, idx) => (
                    <span
                      key={idx}
                      className="text-[10px] font-medium px-2 py-0.5 rounded-md bg-[#F7F6F1] border border-[#E2E4DF] text-[#14201B]"
                    >
                      {t}
                    </span>
                  ))}
                </div>
              </div>

              {/* Purchase History */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-[11px] font-bold text-[#68756F] uppercase tracking-wider">
                  <span>Purchase History</span>
                  <span className="text-[#10231C] font-extrabold">{selectedCustomer.totalValue}</span>
                </div>
                {selectedCustomer.orders.length === 0 ? (
                  <p className="text-xs text-[#68756F] italic">No finalized purchases yet (Active Lead).</p>
                ) : (
                  <div className="space-y-1.5">
                    {selectedCustomer.orders.map((ord) => (
                      <div
                        key={ord.id}
                        className="p-2.5 rounded-lg border border-[#E2E4DF] flex items-center justify-between text-xs"
                      >
                        <div>
                          <p className="font-semibold text-[#10231C]">{ord.item}</p>
                          <span className="text-[10px] text-[#68756F]">{ord.date} • {ord.status}</span>
                        </div>
                        <span className="font-bold text-[#287A59]">{ord.amount}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Notes */}
              <div className="space-y-2">
                <div className="text-[11px] font-bold text-[#68756F] uppercase tracking-wider">
                  Internal Notes
                </div>
                <div className="space-y-1.5">
                  {selectedCustomer.notes.map((note, idx) => (
                    <div
                      key={idx}
                      className="p-2.5 rounded-lg bg-[#F7F6F1] border border-[#E2E4DF] text-xs text-[#14201B]"
                    >
                      {note}
                    </div>
                  ))}
                </div>
              </div>

              {/* Timeline */}
              <div className="space-y-2 pt-2 border-t border-[#E2E4DF]">
                <div className="text-[11px] font-bold text-[#68756F] uppercase tracking-wider">
                  Activity Timeline
                </div>
                <div className="space-y-2.5 text-xs">
                  {selectedCustomer.timeline.map((tl, idx) => (
                    <div key={idx} className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-[#287A59] mt-1.5 flex-shrink-0" />
                      <div>
                        <p className="text-[#10231C] font-medium">{tl.event}</p>
                        <span className="text-[10px] text-[#68756F]">{tl.date}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          ) : (
            <div className="py-12 text-center text-xs text-[#68756F]">
              Select a customer from the table to view their complete profile.
            </div>
          )}
        </div>
      </div>

      {/* Add Customer Modal */}
      {showAddCustomerModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-xs">
          <div className="bg-white w-full max-w-md rounded-2xl border border-[#E2E4DF] p-6 shadow-2xl space-y-4 animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between border-b border-[#E2E4DF] pb-3">
              <h3 className="text-base font-bold text-[#10231C]">Add New Customer</h3>
              <button
                onClick={() => setShowAddCustomerModal(false)}
                className="p-1 rounded-md text-[#68756F] hover:bg-[#F7F6F1]"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-[#14201B] mb-1">Customer Full Name</label>
                <input
                  type="text"
                  placeholder="e.g. Baraka Msuya"
                  value={newCustName}
                  onChange={(e) => setNewCustName(e.target.value)}
                  className="w-full p-2.5 text-xs rounded-xl border border-[#E2E4DF] bg-[#F7F6F1] focus:bg-white focus:outline-none focus:border-[#287A59]"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#14201B] mb-1">Company / Store Name</label>
                <input
                  type="text"
                  placeholder="e.g. Baraka Electronics"
                  value={newCustCompany}
                  onChange={(e) => setNewCustCompany(e.target.value)}
                  className="w-full p-2.5 text-xs rounded-xl border border-[#E2E4DF] bg-[#F7F6F1] focus:bg-white focus:outline-none focus:border-[#287A59]"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#14201B] mb-1">Phone / WhatsApp Number</label>
                <input
                  type="text"
                  placeholder="+255 7XX XXX XXX"
                  value={newCustPhone}
                  onChange={(e) => setNewCustPhone(e.target.value)}
                  className="w-full p-2.5 text-xs rounded-xl border border-[#E2E4DF] bg-[#F7F6F1] focus:bg-white focus:outline-none focus:border-[#287A59]"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#14201B] mb-1">Location in Tanzania</label>
                <input
                  type="text"
                  placeholder="e.g. Kariakoo, Dar es Salaam or Arusha Mjini"
                  value={newCustLocation}
                  onChange={(e) => setNewCustLocation(e.target.value)}
                  className="w-full p-2.5 text-xs rounded-xl border border-[#E2E4DF] bg-[#F7F6F1] focus:bg-white focus:outline-none focus:border-[#287A59]"
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 pt-3 border-t border-[#E2E4DF]">
              <button
                type="button"
                onClick={() => setShowAddCustomerModal(false)}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-[#68756F] hover:bg-[#F7F6F1]"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={() => setShowAddCustomerModal(false)}
                className="px-4 py-2 rounded-xl bg-[#287A59] text-white text-xs font-bold hover:bg-[#1f5f45]"
              >
                Save Customer
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
export default CustomerPage;
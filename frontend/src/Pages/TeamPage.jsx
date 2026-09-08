import React, { useState } from 'react';
import {
  UserCheck,
  Plus,
  Mail,
  Shield,
  Clock,
  MessageSquare,
  MoreVertical,
  X,
  CheckCircle2,
  Trash2,
  Edit2
} from 'lucide-react';
import { TeamMember, PageId } from '../../types';

interface TeamPageProps {
  teamMembers: TeamMember[];
  onNavigate: (page: PageId) => void;
}

export const TeamPage: React.FC<TeamPageProps> = ({
  teamMembers: initialMembers,
  onNavigate,
}) => {
  const [members, setMembers] = useState<TeamMember[]>(initialMembers);
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteName, setInviteName] = useState('');
  const [inviteRole, setInviteRole] = useState<'Owner' | 'Admin' | 'Agent' | 'Viewer'>('Agent');

  const handleInvite = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inviteEmail.trim() || !inviteName.trim()) return;

    const newMember: TeamMember = {
      id: `tm-${Date.now()}`,
      name: inviteName.trim(),
      email: inviteEmail.trim(),
      role: inviteRole,
      status: 'Active',
      lastActive: 'Invited just now',
      conversationsHandled: 0,
      avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=160&q=80'
    };

    setMembers([...members, newMember]);
    setShowInviteModal(false);
    setInviteName('');
    setInviteEmail('');
  };

  const getRoleBadge = (role: string) => {
    switch (role) {
      case 'Owner':
        return <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#10231C] text-white">Owner</span>;
      case 'Admin':
        return <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#287A59] text-white">Admin</span>;
      case 'Agent':
        return <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#287A59]/15 text-[#287A59]">Agent</span>;
      default:
        return <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-gray-100 text-gray-700">Viewer</span>;
    }
  };

  const getStatusIndicator = (status: string) => {
    switch (status) {
      case 'Active':
        return (
          <span className="flex items-center gap-1.5 text-xs text-[#287A59] font-semibold">
            <span className="w-2 h-2 rounded-full bg-[#35D98A]" />
            Active
          </span>
        );
      case 'Away':
        return (
          <span className="flex items-center gap-1.5 text-xs text-amber-700 font-semibold">
            <span className="w-2 h-2 rounded-full bg-amber-400" />
            Away
          </span>
        );
      default:
        return (
          <span className="flex items-center gap-1.5 text-xs text-gray-500 font-medium">
            <span className="w-2 h-2 rounded-full bg-gray-300" />
            Offline
          </span>
        );
    }
  };

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-[#10231C] tracking-tight">Team Members</h2>
          <p className="text-xs text-[#68756F] mt-1">
            Manage agents, permissions, and conversation assignment routing across your business.
          </p>
        </div>

        <button
          onClick={() => setShowInviteModal(true)}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-[#287A59] hover:bg-[#1f5f45] text-white text-xs font-bold transition-colors shadow-2xs"
        >
          <Plus className="w-4 h-4" />
          <span>Invite Team Member</span>
        </button>
      </div>

      {/* Role explanation summary */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-4 rounded-2xl bg-white border border-[#E2E4DF] shadow-2xs text-xs">
        <div>
          <span className="font-bold text-[#10231C]">Owner</span>
          <p className="text-[11px] text-[#68756F] mt-0.5">Full billing, AI model prompt, & team control.</p>
        </div>
        <div>
          <span className="font-bold text-[#10231C]">Admin</span>
          <p className="text-[11px] text-[#68756F] mt-0.5">Knowledge base updates & escalation config.</p>
        </div>
        <div>
          <span className="font-bold text-[#10231C]">Agent</span>
          <p className="text-[11px] text-[#68756F] mt-0.5">Replies to WhatsApp, Instagram & CRM tickets.</p>
        </div>
        <div>
          <span className="font-bold text-[#10231C]">Viewer</span>
          <p className="text-[11px] text-[#68756F] mt-0.5">Read-only analytics and reports.</p>
        </div>
      </div>

      {/* Team Table */}
      <div className="bg-white rounded-2xl border border-[#E2E4DF] shadow-2xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-[#E2E4DF] bg-[#F7F6F1] text-[#68756F] font-semibold">
                <th className="py-3 px-4">Team Member</th>
                <th className="py-3 px-3">Role</th>
                <th className="py-3 px-3">Status</th>
                <th className="py-3 px-3">Last Active</th>
                <th className="py-3 px-4 text-right">Handled Chats</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E2E4DF]">
              {members.map((tm) => (
                <tr key={tm.id} className="hover:bg-[#F7F6F1] transition-colors">
                  <td className="py-3.5 px-4">
                    <div className="flex items-center gap-3">
                      <img
                        src={tm.avatar}
                        alt={tm.name}
                        className="w-9 h-9 rounded-full object-cover border border-[#E2E4DF]"
                      />
                      <div>
                        <div className="font-bold text-[#10231C]">{tm.name}</div>
                        <div className="text-[11px] text-[#68756F]">{tm.email}</div>
                      </div>
                    </div>
                  </td>

                  <td className="py-3.5 px-3">
                    {getRoleBadge(tm.role)}
                  </td>

                  <td className="py-3.5 px-3">
                    {getStatusIndicator(tm.status)}
                  </td>

                  <td className="py-3.5 px-3 text-[#68756F]">
                    {tm.lastActive}
                  </td>

                  <td className="py-3.5 px-4 text-right font-bold text-[#10231C]">
                    {tm.conversationsHandled}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Invite Modal */}
      {showInviteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-xs">
          <div className="bg-white w-full max-w-md rounded-2xl border border-[#E2E4DF] p-6 shadow-2xl space-y-4 animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between border-b border-[#E2E4DF] pb-3">
              <h3 className="text-base font-bold text-[#10231C]">Invite Colleague or Agent</h3>
              <button
                onClick={() => setShowInviteModal(false)}
                className="p-1 rounded-md text-[#68756F] hover:bg-[#F7F6F1]"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleInvite} className="space-y-4 text-xs">
              <div>
                <label className="block font-semibold text-[#14201B] mb-1">Full Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Amina Juma"
                  value={inviteName}
                  onChange={(e) => setInviteName(e.target.value)}
                  className="w-full p-2.5 rounded-xl border border-[#E2E4DF] bg-[#F7F6F1] focus:bg-white focus:outline-none focus:border-[#287A59]"
                />
              </div>

              <div>
                <label className="block font-semibold text-[#14201B] mb-1">Work Email Address</label>
                <input
                  type="email"
                  required
                  placeholder="amina@zawadi.co.tz"
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  className="w-full p-2.5 rounded-xl border border-[#E2E4DF] bg-[#F7F6F1] focus:bg-white focus:outline-none focus:border-[#287A59]"
                />
              </div>

              <div>
                <label className="block font-semibold text-[#14201B] mb-1">System Role & Permissions</label>
                <select
                  value={inviteRole}
                  onChange={(e) => setInviteRole(e.target.value as any)}
                  className="w-full p-2.5 rounded-xl border border-[#E2E4DF] bg-[#F7F6F1] focus:bg-white focus:outline-none focus:border-[#287A59]"
                >
                  <option value="Agent">Agent (Can chat, approve AI replies, edit CRM)</option>
                  <option value="Admin">Admin (Can edit AI knowledge base & channels)</option>
                  <option value="Viewer">Viewer (Read-only analytics & reporting)</option>
                  <option value="Owner">Co-Owner (Full access)</option>
                </select>
              </div>

              <div className="flex items-center justify-end gap-2 pt-3 border-t border-[#E2E4DF]">
                <button
                  type="button"
                  onClick={() => setShowInviteModal(false)}
                  className="px-4 py-2 rounded-xl font-semibold text-[#68756F] hover:bg-[#F7F6F1]"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-[#287A59] text-white font-bold hover:bg-[#1f5f45]"
                >
                  Send Invitation
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
export default TeamPage;
import React, { useState } from 'react';
import {
  Zap,
  Plus,
  ArrowRight,
  Play,
  CheckCircle2,
  Clock,
  MessageSquare,
  Instagram,
  Mail,
  PhoneCall,
  Sliders,
  MoreVertical,
  Trash2,
  Edit2,
  X,
  Bell,
  UserCheck,
  Tag
} from 'lucide-react';
import { AutomationWorkflow, PageId, ChannelType } from '../../types';

interface AutomationsPageProps {
  workflows: AutomationWorkflow[];
  onNavigate: (page: PageId) => void;
}

export const AutomationsPage: React.FC<AutomationsPageProps> = ({
  workflows: initialWorkflows,
  onNavigate,
}) => {
  const [workflows, setWorkflows] = useState<AutomationWorkflow[]>(initialWorkflows);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newFlowName, setNewFlowName] = useState('');
  const [newFlowDesc, setNewFlowDesc] = useState('');
  const [newFlowTrigger, setNewFlowTrigger] = useState('New customer inquiry on WhatsApp');

  const toggleWorkflowStatus = (id: string) => {
    setWorkflows((prev) =>
      prev.map((w) => (w.id === id ? { ...w, status: !w.status } : w))
    );
  };

  const getChannelIcon = (ch: ChannelType) => {
    switch (ch) {
      case 'whatsapp': return <MessageSquare className="w-3.5 h-3.5 text-[#25D366]" />;
      case 'instagram': return <Instagram className="w-3.5 h-3.5 text-[#E4405F]" />;
      case 'email': return <Mail className="w-3.5 h-3.5 text-[#4285F4]" />;
      case 'call': return <PhoneCall className="w-3.5 h-3.5 text-[#287A59]" />;
    }
  };

  const handleCreateWorkflow = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newFlowName.trim()) return;

    const created: AutomationWorkflow = {
      id: `auto-${Date.now()}`,
      name: newFlowName.trim(),
      description: newFlowDesc || 'Automated multi-step customer lifecycle workflow.',
      trigger: newFlowTrigger,
      actions: ['AI responds to customer', 'Evaluate customer interest', 'Assign to sales representative', 'Notify team via WhatsApp'],
      status: true,
      lastRun: 'Just now',
      executionsCount: 1,
      channels: ['whatsapp']
    };

    setWorkflows([created, ...workflows]);
    setShowCreateModal(false);
    setNewFlowName('');
    setNewFlowDesc('');
  };

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-2xl font-bold text-[#10231C] tracking-tight">Automations</h2>
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-[#287A59]/10 text-[#287A59]">
              5 Active Pipelines
            </span>
          </div>
          <p className="text-xs text-[#68756F] mt-1">
            Build event-driven AI customer journeys from initial greeting to closed transaction.
          </p>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-[#287A59] hover:bg-[#1f5f45] text-white text-xs font-bold transition-colors shadow-2xs"
        >
          <Plus className="w-4 h-4" />
          <span>Create Automation</span>
        </button>
      </div>

      {/* Flagship Exemplar Diagram Card (As specified in prompt:
          New customer inquiry ↓ AI responds ↓ Customer interested ↓ Assign to sales ↓ Notify team) */}
      <div className="p-6 rounded-2xl bg-[#10231C] text-white space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-[#35D98A]" />
            <h3 className="text-sm font-bold text-white tracking-tight">
              Standard Intelligent Funnel
            </h3>
          </div>
          <span className="text-[11px] text-[#8E9B95]">Autonomous Workflow</span>
        </div>

        {/* Step Diagram */}
        <div className="grid grid-cols-1 sm:grid-cols-5 gap-3 pt-2">
          {[
            { step: '1', title: 'New customer inquiry', sub: 'WhatsApp / Instagram / Call' },
            { step: '2', title: 'AI responds in < 2s', sub: 'Swahili & English verified' },
            { step: '3', title: 'Customer interested', sub: 'Detected quote or intent' },
            { step: '4', title: 'Assign to sales', sub: 'Khamis Mgofi / Salma' },
            { step: '5', title: 'Notify team', sub: 'Instant SMS & Push alert' },
          ].map((item, idx) => (
            <div
              key={idx}
              className="p-3 rounded-xl bg-white/5 border border-white/10 relative flex flex-col justify-between"
            >
              <div>
                <span className="text-[10px] font-bold text-[#35D98A] bg-[#287A59]/40 px-1.5 py-0.5 rounded">
                  STEP 0{item.step}
                </span>
                <p className="text-xs font-bold text-white mt-2">{item.title}</p>
              </div>
              <p className="text-[10px] text-[#8E9B95] mt-1">{item.sub}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Workflows Listing */}
      <div className="space-y-4">
        <h3 className="text-sm font-bold text-[#10231C]">Active Automation Pipelines</h3>

        <div className="grid grid-cols-1 gap-4">
          {workflows.map((flow) => (
            <div
              key={flow.id}
              className="p-5 rounded-2xl bg-white border border-[#E2E4DF] hover:border-[#287A59]/40 transition-colors shadow-2xs space-y-4"
            >
              {/* Header & Status Toggle */}
              <div className="flex items-start justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2.5">
                    <h4 className="text-sm font-bold text-[#10231C]">{flow.name}</h4>
                    <div className="flex items-center gap-1">
                      {flow.channels.map((ch) => (
                        <span key={ch} className="p-1 rounded bg-[#F7F6F1]" title={ch}>
                          {getChannelIcon(ch)}
                        </span>
                      ))}
                    </div>
                  </div>
                  <p className="text-xs text-[#68756F] max-w-2xl">{flow.description}</p>
                </div>

                <div className="flex items-center gap-3 flex-shrink-0">
                  <span className={`text-xs font-semibold ${flow.status ? 'text-[#287A59]' : 'text-[#68756F]'}`}>
                    {flow.status ? 'Active' : 'Paused'}
                  </span>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={flow.status}
                      onChange={() => toggleWorkflowStatus(flow.id)}
                      className="sr-only peer"
                    />
                    <div className="w-9 h-5 bg-[#E2E4DF] peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-[#287A59]" />
                  </label>
                </div>
              </div>

              {/* Trigger & Actions Sequence */}
              <div className="p-3 rounded-xl bg-[#F7F6F1] border border-[#E2E4DF] text-xs space-y-2">
                <div className="flex items-center gap-2 text-[#10231C]">
                  <span className="font-bold text-[#287A59]">Trigger:</span>
                  <span>{flow.trigger}</span>
                </div>
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="font-bold text-[#68756F]">Actions:</span>
                  {flow.actions.map((act, i) => (
                    <span
                      key={i}
                      className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-white border border-[#E2E4DF] text-[11px] text-[#14201B]"
                    >
                      <span>{act}</span>
                      {i < flow.actions.length - 1 && <ArrowRight className="w-2.5 h-2.5 text-[#68756F]" />}
                    </span>
                  ))}
                </div>
              </div>

              {/* Footer Meta */}
              <div className="flex items-center justify-between text-xs text-[#68756F] pt-2 border-t border-[#E2E4DF]">
                <div className="flex items-center gap-4">
                  <span>Last executed: <b>{flow.lastRun}</b></span>
                  <span>Total runs: <b>{flow.executionsCount.toLocaleString()}</b></span>
                </div>
                <button className="text-[#287A59] font-bold hover:underline">
                  Configure Logic
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Create Automation Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-xs">
          <div className="bg-white w-full max-w-lg rounded-2xl border border-[#E2E4DF] p-6 shadow-2xl space-y-4 animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between border-b border-[#E2E4DF] pb-3">
              <h3 className="text-base font-bold text-[#10231C]">Create New Automation Workflow</h3>
              <button
                onClick={() => setShowCreateModal(false)}
                className="p-1 rounded-md text-[#68756F] hover:bg-[#F7F6F1]"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleCreateWorkflow} className="space-y-4 text-xs">
              <div>
                <label className="block font-semibold text-[#14201B] mb-1">Workflow Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Kariakoo Cement Bulk Quote Alert"
                  value={newFlowName}
                  onChange={(e) => setNewFlowName(e.target.value)}
                  className="w-full p-2.5 rounded-xl border border-[#E2E4DF] bg-[#F7F6F1] focus:bg-white focus:outline-none focus:border-[#287A59]"
                />
              </div>

              <div>
                <label className="block font-semibold text-[#14201B] mb-1">Description</label>
                <textarea
                  rows={2}
                  placeholder="Briefly describe what this automation accomplishes..."
                  value={newFlowDesc}
                  onChange={(e) => setNewFlowDesc(e.target.value)}
                  className="w-full p-2.5 rounded-xl border border-[#E2E4DF] bg-[#F7F6F1] focus:bg-white focus:outline-none focus:border-[#287A59]"
                />
              </div>

              <div>
                <label className="block font-semibold text-[#14201B] mb-1">Select Trigger Event</label>
                <select
                  value={newFlowTrigger}
                  onChange={(e) => setNewFlowTrigger(e.target.value)}
                  className="w-full p-2.5 rounded-xl border border-[#E2E4DF] bg-[#F7F6F1] focus:bg-white focus:outline-none focus:border-[#287A59]"
                >
                  <option value="New customer inquiry on WhatsApp">New customer inquiry on WhatsApp</option>
                  <option value="Instagram story reply or product mention">Instagram story reply or product mention</option>
                  <option value="Missed inbound voice call transcribed">Missed inbound voice call transcribed</option>
                  <option value="Payment verification screenshot received">Payment verification screenshot received</option>
                  <option value="Cart abandonment or slow customer reply">Cart abandonment or slow customer reply</option>
                </select>
              </div>

              <div className="p-3 rounded-xl bg-[#287A59]/10 text-[#10231C] space-y-1">
                <span className="font-bold text-[#287A59]">Automated Actions Sequence:</span>
                <p className="text-[11px] text-[#68756F]">
                  1. MtejaAI evaluates intent in Swahili/English <br />
                  2. Cross-references knowledge base and inventory <br />
                  3. Sends instant personalized reply or alerts sales rep
                </p>
              </div>

              <div className="flex items-center justify-end gap-2 pt-3 border-t border-[#E2E4DF]">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 rounded-xl font-semibold text-[#68756F] hover:bg-[#F7F6F1]"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-[#287A59] text-white font-bold hover:bg-[#1f5f45]"
                >
                  Create & Activate Pipeline
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
export default AutomationsPage;
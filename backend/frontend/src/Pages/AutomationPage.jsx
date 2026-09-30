import { useState } from 'react';
import {
  Zap,
  Plus,
  ArrowRight,
  X,
  MessageSquare,
  Camera,
  Mail,
  PhoneCall,
} from 'lucide-react';

function AutomationsPage() {
  const [workflows, setWorkflows] = useState([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newFlowName, setNewFlowName] = useState('');
  const [newFlowDesc, setNewFlowDesc] = useState('');
  const [newFlowTrigger, setNewFlowTrigger] = useState(
    'New customer inquiry on WhatsApp'
  );

  const toggleWorkflowStatus = (id) => {
    setWorkflows((prev) =>
      prev.map((w) => (w.id === id ? { ...w, status: !w.status } : w))
    );
  };

  const getChannelIcon = (ch) => {
    switch (ch) {
      case 'whatsapp':
        return <MessageSquare className="w-3.5 h-3.5 text-[#25D366]" />;
      case 'instagram':
        return <Camera className="w-3.5 h-3.5 text-[#E4405F]" />;
      case 'email':
        return <Mail className="w-3.5 h-3.5 text-[#4285F4]" />;
      case 'call':
        return <PhoneCall className="w-3.5 h-3.5 text-[#287A59]" />;
      default:
        return <MessageSquare className="w-3.5 h-3.5 text-[#68756F]" />;
    }
  };

  const handleCreateWorkflow = (e) => {
    e.preventDefault();
    if (!newFlowName.trim()) return;

    const created = {
      id: `auto-${Date.now()}`,
      name: newFlowName.trim(),
      description:
        newFlowDesc || 'Automated multi-step customer workflow.',
      trigger: newFlowTrigger,
      actions: [
        'AI responds to customer',
        'Evaluate customer interest',
        'Assign to sales',
        'Notify team',
      ],
      status: true,
      lastRun: 'Just now',
      executionsCount: 0,
      channels: ['whatsapp'],
    };

    setWorkflows([created, ...workflows]);
    setShowCreateModal(false);
    setNewFlowName('');
    setNewFlowDesc('');
  };

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-2xl font-bold text-[#10231C] tracking-tight">
              Automations
            </h2>
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-[#287A59]/10 text-[#287A59]">
              {workflows.filter((w) => w.status).length} Active
            </span>
          </div>
          <p className="text-xs text-[#68756F] mt-1">
            Build event-driven AI customer journeys from greeting to closed deal.
          </p>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-[#287A59] hover:bg-[#1f5f45] text-white text-xs font-bold transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>Create Automation</span>
        </button>
      </div>

      {/* Funnel overview */}
      <div className="p-6 rounded-2xl bg-[#10231C] text-white space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-[#35D98A]" />
            <h3 className="text-sm font-bold tracking-tight">
              Standard Intelligent Funnel
            </h3>
          </div>
          <span className="text-[11px] text-[#8E9B95]">Autonomous Workflow</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-5 gap-3 pt-2">
          {[
            { step: '1', title: 'New customer inquiry', sub: 'Any channel' },
            { step: '2', title: 'AI responds', sub: 'Swahili & English' },
            { step: '3', title: 'Customer interested', sub: 'Intent detected' },
            { step: '4', title: 'Assign to sales', sub: 'Human handoff' },
            { step: '5', title: 'Notify team', sub: 'Alert sent' },
          ].map((item) => (
            <div
              key={item.step}
              className="p-3 rounded-xl bg-white/5 border border-white/10 flex flex-col justify-between"
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

      {/* Workflows list */}
      <div className="space-y-4">
        <h3 className="text-sm font-bold text-[#10231C]">
          Automation Pipelines
        </h3>

        {workflows.length === 0 ? (
          <div className="p-12 rounded-2xl bg-white border border-[#E2E4DF] text-center">
            <Zap className="w-8 h-8 text-[#68756F] mx-auto mb-3" />
            <p className="text-sm font-medium text-[#10231C]">
              No automations yet
            </p>
            <p className="text-xs text-[#68756F] mt-1 max-w-sm mx-auto">
              Create your first workflow to automatically reply, qualify leads,
              and notify your team.
            </p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="mt-4 inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-[#287A59] text-white text-xs font-bold"
            >
              <Plus className="w-4 h-4" />
              Create Automation
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {workflows.map((flow) => (
              <div
                key={flow.id}
                className="p-5 rounded-2xl bg-white border border-[#E2E4DF] hover:border-[#287A59]/40 transition-colors space-y-4"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2.5">
                      <h4 className="text-sm font-bold text-[#10231C]">
                        {flow.name}
                      </h4>
                      <div className="flex items-center gap-1">
                        {(flow.channels || []).map((ch) => (
                          <span
                            key={ch}
                            className="p-1 rounded bg-[#F7F6F1]"
                            title={ch}
                          >
                            {getChannelIcon(ch)}
                          </span>
                        ))}
                      </div>
                    </div>
                    <p className="text-xs text-[#68756F] max-w-2xl">
                      {flow.description}
                    </p>
                  </div>

                  <div className="flex items-center gap-3 flex-shrink-0">
                    <span
                      className={`text-xs font-semibold ${
                        flow.status ? 'text-[#287A59]' : 'text-[#68756F]'
                      }`}
                    >
                      {flow.status ? 'Active' : 'Paused'}
                    </span>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={flow.status}
                        onChange={() => toggleWorkflowStatus(flow.id)}
                        className="sr-only peer"
                      />
                      <div className="w-9 h-5 bg-[#E2E4DF] rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-[#287A59]" />
                    </label>
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-[#F7F6F1] border border-[#E2E4DF] text-xs space-y-2">
                  <div className="flex items-center gap-2 text-[#10231C]">
                    <span className="font-bold text-[#287A59]">Trigger:</span>
                    <span>{flow.trigger}</span>
                  </div>
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-bold text-[#68756F]">Actions:</span>
                    {(flow.actions || []).map((act, i) => (
                      <span
                        key={i}
                        className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-white border border-[#E2E4DF] text-[11px] text-[#14201B]"
                      >
                        <span>{act}</span>
                        {i < flow.actions.length - 1 && (
                          <ArrowRight className="w-2.5 h-2.5 text-[#68756F]" />
                        )}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="flex items-center justify-between text-xs text-[#68756F] pt-2 border-t border-[#E2E4DF]">
                  <div className="flex items-center gap-4">
                    <span>
                      Last run: <b>{flow.lastRun}</b>
                    </span>
                    <span>
                      Runs: <b>{flow.executionsCount}</b>
                    </span>
                  </div>
                  <button className="text-[#287A59] font-bold hover:underline">
                    Configure
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Create modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40">
          <div className="bg-white w-full max-w-lg rounded-2xl border border-[#E2E4DF] p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-[#E2E4DF] pb-3">
              <h3 className="text-base font-bold text-[#10231C]">
                Create New Automation
              </h3>
              <button
                onClick={() => setShowCreateModal(false)}
                className="p-1 rounded-md text-[#68756F] hover:bg-[#F7F6F1]"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleCreateWorkflow} className="space-y-4 text-xs">
              <div>
                <label className="block font-semibold text-[#14201B] mb-1">
                  Workflow Name
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. WhatsApp lead qualification"
                  value={newFlowName}
                  onChange={(e) => setNewFlowName(e.target.value)}
                  className="w-full p-2.5 rounded-xl border border-[#E2E4DF] bg-[#F7F6F1] focus:bg-white focus:outline-none focus:border-[#287A59]"
                />
              </div>

              <div>
                <label className="block font-semibold text-[#14201B] mb-1">
                  Description
                </label>
                <textarea
                  rows={2}
                  placeholder="What does this automation do?"
                  value={newFlowDesc}
                  onChange={(e) => setNewFlowDesc(e.target.value)}
                  className="w-full p-2.5 rounded-xl border border-[#E2E4DF] bg-[#F7F6F1] focus:bg-white focus:outline-none focus:border-[#287A59]"
                />
              </div>

              <div>
                <label className="block font-semibold text-[#14201B] mb-1">
                  Trigger Event
                </label>
                <select
                  value={newFlowTrigger}
                  onChange={(e) => setNewFlowTrigger(e.target.value)}
                  className="w-full p-2.5 rounded-xl border border-[#E2E4DF] bg-[#F7F6F1] focus:bg-white focus:outline-none focus:border-[#287A59]"
                >
                  <option value="New customer inquiry on WhatsApp">
                    New customer inquiry on WhatsApp
                  </option>
                  <option value="New Instagram message">
                    New Instagram message
                  </option>
                  <option value="Missed inbound call">
                    Missed inbound call
                  </option>
                  <option value="Payment screenshot received">
                    Payment screenshot received
                  </option>
                  <option value="Customer slow to reply">
                    Customer slow to reply
                  </option>
                </select>
              </div>

              <div className="p-3 rounded-xl bg-[#287A59]/10 text-[#10231C] space-y-1">
                <span className="font-bold text-[#287A59]">
                  Default actions:
                </span>
                <p className="text-[11px] text-[#68756F]">
                  1. AI evaluates intent · 2. Checks knowledge base · 3. Replies
                  or alerts sales
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
                  Create & Activate
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default AutomationsPage;
import React, { useState } from 'react';
import {
  Settings,
  Building,
  Bot,
  Bell,
  Shield,
  Key,
  Save,
  Check,
  Globe,
  Mail,
  Phone,
  Copy,
  CheckCheck
} from 'lucide-react';
import { PageId } from '../../types';

interface SettingsPageProps {
  onNavigate: (page: PageId) => void;
}

export const SettingsPage: React.FC<SettingsPageProps> = ({ onNavigate }) => {
  const [activeTab, setActiveTab] = useState<'general' | 'business' | 'ai' | 'notifications' | 'security' | 'api'>('general');
  const [saved, setSaved] = useState(false);
  const [copiedKey, setCopiedKey] = useState(false);

  // Settings State
  const [businessName, setBusinessName] = useState('Zawadi Emporium Tanzania');
  const [timezone, setTimezone] = useState('Africa/Dar_es_Salaam (EAT +03:00)');
  const [primaryLanguage, setPrimaryLanguage] = useState('Swahili & English (Adaptive)');
  const [notificationEmail, setNotificationEmail] = useState('alerts@zawadi.co.tz');
  const [hotline, setHotline] = useState('+255 754 892 100');
  const [autoEscalateHighValue, setAutoEscalateHighValue] = useState(true);
  const [twoFactorAuth, setTwoFactorAuth] = useState(true);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const copyApiKey = () => {
    navigator.clipboard.writeText('mtj_live_9f81bc20349a46ea9b5f8910243e');
    setCopiedKey(true);
    setTimeout(() => setCopiedKey(false), 2000);
  };

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-[#10231C] tracking-tight">System Settings</h2>
          <p className="text-xs text-[#68756F] mt-1">
            Configure organization identity, AI behavioral thresholds, security, and developer webhooks.
          </p>
        </div>

        <button
          onClick={handleSave}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-[#287A59] hover:bg-[#1f5f45] text-white text-xs font-bold transition-colors shadow-2xs"
        >
          {saved ? <Check className="w-4 h-4" /> : <Save className="w-4 h-4" />}
          <span>{saved ? 'Settings Saved' : 'Save Changes'}</span>
        </button>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-1 border-b border-[#E2E4DF] overflow-x-auto pb-1">
        {[
          { id: 'general', label: 'General', icon: Settings },
          { id: 'business', label: 'Business Profile', icon: Building },
          { id: 'ai', label: 'AI Preferences', icon: Bot },
          { id: 'notifications', label: 'Notifications', icon: Bell },
          { id: 'security', label: 'Security & 2FA', icon: Shield },
          { id: 'api', label: 'API & Webhooks', icon: Key },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-2.5 text-xs font-bold border-b-2 transition-colors whitespace-nowrap ${
                isActive
                  ? 'border-[#287A59] text-[#287A59]'
                  : 'border-transparent text-[#68756F] hover:text-[#10231C]'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* TAB CONTENT: General */}
      {activeTab === 'general' && (
        <div className="bg-white p-6 rounded-2xl border border-[#E2E4DF] shadow-2xs space-y-5">
          <h3 className="text-sm font-bold text-[#10231C]">Regional & Language Defaults</h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5 text-xs">
            <div>
              <label className="block font-semibold text-[#14201B] mb-1">Timezone</label>
              <input
                type="text"
                disabled
                value={timezone}
                className="w-full p-2.5 rounded-xl border border-[#E2E4DF] bg-[#F7F6F1] text-[#14201B]"
              />
              <p className="text-[11px] text-[#68756F] mt-1">Synchronized with East Africa Time (EAT).</p>
            </div>

            <div>
              <label className="block font-semibold text-[#14201B] mb-1">Primary Operating Currency</label>
              <select className="w-full p-2.5 rounded-xl border border-[#E2E4DF] bg-[#F7F6F1] text-[#14201B]">
                <option value="TZS">TZS (Tanzanian Shilling - Shilingi ya Tanzania)</option>
                <option value="USD">USD ($ United States Dollar)</option>
                <option value="KES">KES (Kenyan Shilling)</option>
              </select>
            </div>

            <div>
              <label className="block font-semibold text-[#14201B] mb-1">Language Processing Mode</label>
              <input
                type="text"
                value={primaryLanguage}
                onChange={(e) => setPrimaryLanguage(e.target.value)}
                className="w-full p-2.5 rounded-xl border border-[#E2E4DF] bg-[#F7F6F1] text-[#14201B]"
              />
              <p className="text-[11px] text-[#68756F] mt-1">
                Auto-switches between conversational Swahili and English.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* TAB CONTENT: Business Profile */}
      {activeTab === 'business' && (
        <div className="bg-white p-6 rounded-2xl border border-[#E2E4DF] shadow-2xs space-y-5 text-xs">
          <h3 className="text-sm font-bold text-[#10231C]">Store & Company Information</h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div>
              <label className="block font-semibold text-[#14201B] mb-1">Registered Business Name</label>
              <input
                type="text"
                value={businessName}
                onChange={(e) => setBusinessName(e.target.value)}
                className="w-full p-2.5 rounded-xl border border-[#E2E4DF] bg-[#F7F6F1]"
              />
            </div>

            <div>
              <label className="block font-semibold text-[#14201B] mb-1">TIN / BRELA Registration ID</label>
              <input
                type="text"
                defaultValue="142-980-321 (TRA Certified)"
                className="w-full p-2.5 rounded-xl border border-[#E2E4DF] bg-[#F7F6F1]"
              />
            </div>

            <div>
              <label className="block font-semibold text-[#14201B] mb-1">Official WhatsApp Hotline</label>
              <input
                type="text"
                value={hotline}
                onChange={(e) => setHotline(e.target.value)}
                className="w-full p-2.5 rounded-xl border border-[#E2E4DF] bg-[#F7F6F1]"
              />
            </div>

            <div>
              <label className="block font-semibold text-[#14201B] mb-1">Store Physical Address</label>
              <input
                type="text"
                defaultValue="Congo Street, Kariakoo, Dar es Salaam"
                className="w-full p-2.5 rounded-xl border border-[#E2E4DF] bg-[#F7F6F1]"
              />
            </div>
          </div>
        </div>
      )}

      {/* TAB CONTENT: AI Preferences */}
      {activeTab === 'ai' && (
        <div className="bg-white p-6 rounded-2xl border border-[#E2E4DF] shadow-2xs space-y-5 text-xs">
          <h3 className="text-sm font-bold text-[#10231C]">AI Engine Parameters</h3>

          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 rounded-xl bg-[#F7F6F1]">
              <div>
                <p className="font-bold text-[#10231C]">Autonomous Reply Confidence Threshold</p>
                <p className="text-[11px] text-[#68756F]">Replies above this score are sent without requiring human approval.</p>
              </div>
              <span className="font-mono font-bold text-[#287A59]">88%</span>
            </div>

            <div className="flex items-center justify-between p-3 rounded-xl bg-[#F7F6F1]">
              <div>
                <p className="font-bold text-[#10231C]">Swahili Slang & Colloquialism Normalization</p>
                <p className="text-[11px] text-[#68756F]">Recognize modern youth and merchant terms (e.g. "mchongo", "kivumbi", "lipa namba").</p>
              </div>
              <input type="checkbox" defaultChecked className="w-4 h-4 text-[#287A59] rounded" />
            </div>

            <div className="flex items-center justify-between p-3 rounded-xl bg-[#F7F6F1]">
              <div>
                <p className="font-bold text-[#10231C]">Auto-Detect Lipa Namba Screenshots</p>
                <p className="text-[11px] text-[#68756F]">Use vision OCR to extract Vodacom/Tigo transaction codes automatically.</p>
              </div>
              <input type="checkbox" defaultChecked className="w-4 h-4 text-[#287A59] rounded" />
            </div>
          </div>
        </div>
      )}

      {/* TAB CONTENT: Notifications */}
      {activeTab === 'notifications' && (
        <div className="bg-white p-6 rounded-2xl border border-[#E2E4DF] shadow-2xs space-y-4 text-xs">
          <h3 className="text-sm font-bold text-[#10231C]">Staff Alert Channels</h3>

          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 rounded-xl border border-[#E2E4DF]">
              <div>
                <p className="font-semibold text-[#10231C]">Escalation Push Notifications</p>
                <p className="text-[11px] text-[#68756F]">Alert on mobile browser when a customer requests a human agent.</p>
              </div>
              <input type="checkbox" defaultChecked className="w-4 h-4 text-[#287A59] rounded" />
            </div>

            <div className="flex items-center justify-between p-3 rounded-xl border border-[#E2E4DF]">
              <div>
                <p className="font-semibold text-[#10231C]">Daily Summary WhatsApp Briefing</p>
                <p className="text-[11px] text-[#68756F]">Receive an 8:00 AM WhatsApp digest of overnight inquiries and revenue.</p>
              </div>
              <input type="checkbox" defaultChecked className="w-4 h-4 text-[#287A59] rounded" />
            </div>
          </div>
        </div>
      )}

      {/* TAB CONTENT: Security */}
      {activeTab === 'security' && (
        <div className="bg-white p-6 rounded-2xl border border-[#E2E4DF] shadow-2xs space-y-4 text-xs">
          <h3 className="text-sm font-bold text-[#10231C]">Account Protection & Session Security</h3>

          <div className="p-4 rounded-xl bg-[#F7F6F1] border border-[#E2E4DF] space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-bold text-[#10231C]">Two-Factor Authentication (SMS / Authenticator)</p>
                <p className="text-[11px] text-[#68756F]">Mandatory verification code sent to +255 754 892 100.</p>
              </div>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">
                Enabled
              </span>
            </div>
          </div>
        </div>
      )}

      {/* TAB CONTENT: API & Webhooks */}
      {activeTab === 'api' && (
        <div className="bg-white p-6 rounded-2xl border border-[#E2E4DF] shadow-2xs space-y-5 text-xs">
          <div>
            <h3 className="text-sm font-bold text-[#10231C]">Developer API Keys & Webhooks</h3>
            <p className="text-[11px] text-[#68756F]">
              Integrate MtejaAI with your internal ERP, POS, or WooCommerce store.
            </p>
          </div>

          <div className="space-y-3">
            <div>
              <label className="block font-semibold text-[#14201B] mb-1">Production Secret API Key</label>
              <div className="flex items-center gap-2">
                <input
                  type="password"
                  disabled
                  value="mtj_live_9f81bc20349a46ea9b5f8910243e"
                  className="flex-1 p-2.5 rounded-xl border border-[#E2E4DF] bg-[#F7F6F1] font-mono"
                />
                <button
                  onClick={copyApiKey}
                  className="px-3.5 py-2.5 rounded-xl bg-[#10231C] text-white font-bold hover:bg-[#287A59] transition-colors flex items-center gap-1.5"
                >
                  {copiedKey ? <CheckCheck className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copiedKey ? 'Copied' : 'Copy Key'}</span>
                </button>
              </div>
            </div>

            <div>
              <label className="block font-semibold text-[#14201B] mb-1">Webhook Endpoint URL</label>
              <input
                type="text"
                defaultValue="https://api.zawadi.co.tz/webhooks/mteja"
                className="w-full p-2.5 rounded-xl border border-[#E2E4DF] bg-[#F7F6F1] font-mono"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
export default SettingsPage;
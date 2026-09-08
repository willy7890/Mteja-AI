import React, { useState } from 'react';
import {
  CreditCard,
  CheckCircle2,
  Sparkles,
  Download,
  AlertCircle,
  Zap,
  Building,
  Smartphone,
  ShieldCheck,
  Check
} from 'lucide-react';
import { BillingInfo, PageId } from '../../types';

interface BillingPageProps {
  billingInfo: BillingInfo;
  onNavigate: (page: PageId) => void;
}

export const BillingPage: React.FC<BillingPageProps> = ({ billingInfo, onNavigate }) => {
  const [selectedPlan, setSelectedPlan] = useState<'starter' | 'pro' | 'business'>('pro');
  const [currencyMode, setCurrencyMode] = useState<'tzs' | 'usd'>('tzs');
  const [showUpgradeSuccess, setShowUpgradeSuccess] = useState(false);

  const plans = [
    {
      id: 'starter',
      name: 'Starter Plan',
      priceUsd: '$19',
      priceTzs: 'TZS 52,000',
      period: '/month',
      desc: 'Essential automation for solo store owners on Instagram & WhatsApp.',
      conversations: '500 conversations / mo',
      aiSpeed: 'Standard 2.5s AI reply',
      features: [
        '1 WhatsApp number',
        'Instagram DM integration',
        'Basic Swahili & English AI model',
        'Standard business hours auto-reply',
        '1 Human agent seat'
      ]
    },
    {
      id: 'pro',
      name: 'Pro Growth (Current)',
      priceUsd: '$49',
      priceTzs: 'TZS 135,000',
      period: '/month',
      desc: 'Intelligent multi-channel scaling for high-traffic Tanzanian brands.',
      conversations: '2,500 conversations / mo',
      aiSpeed: 'Ultra-fast 1.2s AI reply',
      isCurrent: true,
      features: [
        'WhatsApp + Instagram + Email + Phone',
        'Autonomous Swahili intent understanding',
        'Lipa Namba screenshot receipt verification',
        '24/7 Night concierge mode',
        '5 Human agent team seats',
        'Catalog & inventory synchronization'
      ]
    },
    {
      id: 'business',
      name: 'Business Enterprise',
      priceUsd: '$99',
      priceTzs: 'TZS 270,000',
      period: '/month',
      desc: 'Uncapped capacity with dedicated account manager and custom telecom SIP line.',
      conversations: '10,000 conversations / mo',
      aiSpeed: 'Instant < 1s sub-second latency',
      features: [
        'Unlimited WhatsApp & Instagram channels',
        'Custom fine-tuned brand Swahili voice model',
        'Africa’s Talking VoIP phone hotline integration',
        'Unlimited team seats with role permissions',
        'Dedicated SLA & Tanzanian support WhatsApp VIP group'
      ]
    }
  ];

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-8">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-2xl font-bold text-[#10231C] tracking-tight">Billing & Plans</h2>
            <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-[#287A59] text-white">
              Pro Active
            </span>
          </div>
          <p className="text-xs text-[#68756F] mt-1">
            Manage your subscription, local mobile money billing (M-Pesa, Tigo Pesa), and invoices.
          </p>
        </div>

        {/* Currency Switcher */}
        <div className="bg-white border border-[#E2E4DF] rounded-xl p-1 flex items-center shadow-2xs">
          <button
            onClick={() => setCurrencyMode('tzs')}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-colors ${
              currencyMode === 'tzs' ? 'bg-[#10231C] text-white' : 'text-[#68756F]'
            }`}
          >
            TZS (Tanzanian Shilling)
          </button>
          <button
            onClick={() => setCurrencyMode('usd')}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-colors ${
              currencyMode === 'usd' ? 'bg-[#10231C] text-white' : 'text-[#68756F]'
            }`}
          >
            USD ($)
          </button>
        </div>
      </div>

      {/* Usage & Quota Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Conversations Quota */}
        <div className="p-6 rounded-2xl bg-white border border-[#E2E4DF] shadow-2xs space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-[#10231C]">Monthly Conversations Quota</span>
            <span className="text-xs font-bold text-[#287A59]">51.4% Used</span>
          </div>

          <div>
            <div className="flex justify-between text-xs text-[#68756F] mb-1.5">
              <span>{billingInfo.conversationsUsed.toLocaleString()} active inquiries</span>
              <span>{billingInfo.conversationsLimit.toLocaleString()} limit</span>
            </div>
            <div className="w-full h-3 bg-[#F7F6F1] rounded-full overflow-hidden">
              <div
                className="h-full bg-[#287A59] rounded-full"
                style={{ width: `${(billingInfo.conversationsUsed / billingInfo.conversationsLimit) * 100}%` }}
              />
            </div>
          </div>
          <p className="text-[11px] text-[#68756F]">
            Resets on <b>{billingInfo.nextBillingDate}</b>. Extra volume is billed at TZS 40 per conversation.
          </p>
        </div>

        {/* AI Responses Quota */}
        <div className="p-6 rounded-2xl bg-white border border-[#E2E4DF] shadow-2xs space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-[#10231C]">Autonomous AI Replies Generated</span>
            <span className="text-xs font-bold text-[#287A59]">42.3% Used</span>
          </div>

          <div>
            <div className="flex justify-between text-xs text-[#68756F] mb-1.5">
              <span>{billingInfo.aiResponsesUsed.toLocaleString()} replies sent</span>
              <span>{billingInfo.aiResponsesLimit.toLocaleString()} limit</span>
            </div>
            <div className="w-full h-3 bg-[#F7F6F1] rounded-full overflow-hidden">
              <div
                className="h-full bg-[#35D98A] rounded-full"
                style={{ width: `${(billingInfo.aiResponsesUsed / billingInfo.aiResponsesLimit) * 100}%` }}
              />
            </div>
          </div>
          <p className="text-[11px] text-[#68756F]">
            Saved an estimated <b>48 business hours</b> of manual texting this month.
          </p>
        </div>
      </div>

      {/* Subscription Plans */}
      <div className="space-y-4">
        <div>
          <h3 className="text-base font-bold text-[#10231C]">Choose Your Scaling Plan</h3>
          <p className="text-xs text-[#68756F]">Upgrade anytime to unlock higher volume and faster response latency.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {plans.map((p) => {
            const isSelected = selectedPlan === p.id;
            return (
              <div
                key={p.id}
                className={`p-6 rounded-2xl border transition-all flex flex-col justify-between space-y-6 ${
                  p.isCurrent
                    ? 'border-[#287A59] bg-white ring-2 ring-[#287A59]/20 shadow-md relative'
                    : 'border-[#E2E4DF] bg-white hover:border-[#287A59]/40 shadow-2xs'
                }`}
              >
                {p.isCurrent && (
                  <span className="absolute -top-3 left-6 text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-[#287A59] text-white">
                    Current Active Plan
                  </span>
                )}

                <div className="space-y-3">
                  <h4 className="text-base font-bold text-[#10231C]">{p.name}</h4>
                  <div>
                    <span className="text-2xl font-black text-[#10231C]">
                      {currencyMode === 'tzs' ? p.priceTzs : p.priceUsd}
                    </span>
                    <span className="text-xs text-[#68756F] font-semibold">{p.period}</span>
                  </div>
                  <p className="text-xs text-[#68756F] leading-relaxed">{p.desc}</p>

                  <div className="pt-3 border-t border-[#E2E4DF] space-y-2 text-xs">
                    <div className="font-bold text-[#287A59]">{p.conversations}</div>
                    <div className="font-semibold text-[#10231C]">{p.aiSpeed}</div>
                    {p.features.map((feat, idx) => (
                      <div key={idx} className="flex items-center gap-2 text-[#14201B]">
                        <Check className="w-3.5 h-3.5 text-[#287A59] flex-shrink-0" />
                        <span>{feat}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  {p.isCurrent ? (
                    <button
                      disabled
                      className="w-full py-2.5 rounded-xl bg-[#287A59]/15 text-[#287A59] font-bold text-xs cursor-default"
                    >
                      Active Plan
                    </button>
                  ) : (
                    <button
                      onClick={() => {
                        setSelectedPlan(p.id as any);
                        setShowUpgradeSuccess(true);
                        setTimeout(() => setShowUpgradeSuccess(false), 2500);
                      }}
                      className="w-full py-2.5 rounded-xl bg-[#10231C] hover:bg-[#287A59] text-white font-bold text-xs transition-colors shadow-2xs"
                    >
                      Select {p.name}
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Payment Method Section (Emphasizing Tanzanian Mobile Money!) */}
      <div className="bg-white p-6 rounded-2xl border border-[#E2E4DF] shadow-2xs space-y-4">
        <h3 className="text-base font-bold text-[#10231C]">Payment Methods (Tanzania & Cards)</h3>
        <p className="text-xs text-[#68756F]">
          MtejaAI supports local mobile money automated recurring debits and international debit cards.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
          {/* M-Pesa / Tigo Pesa Active */}
          <div className="p-4 rounded-xl border border-[#287A59] bg-[#287A59]/5 space-y-2 relative">
            <span className="absolute top-3 right-3 text-[10px] font-bold text-[#287A59] bg-[#287A59]/15 px-2 py-0.5 rounded-full">
              Primary
            </span>
            <div className="flex items-center gap-2">
              <Smartphone className="w-4 h-4 text-[#287A59]" />
              <h4 className="text-xs font-bold text-[#10231C]">Vodacom M-Pesa Direct</h4>
            </div>
            <p className="text-xs font-semibold text-[#10231C]">+255 754 892 100</p>
            <p className="text-[11px] text-[#68756F]">Next auto-charge: 28 Sep 2026</p>
          </div>

          {/* Bank Card */}
          <div className="p-4 rounded-xl border border-[#E2E4DF] hover:border-[#287A59]/40 space-y-2">
            <div className="flex items-center gap-2">
              <CreditCard className="w-4 h-4 text-[#68756F]" />
              <h4 className="text-xs font-bold text-[#10231C]">CRDB Visa Business</h4>
            </div>
            <p className="text-xs font-semibold text-[#10231C]">•••• •••• •••• 4088</p>
            <p className="text-[11px] text-[#68756F]">Expires 08/28</p>
          </div>

          {/* Add alternative */}
          <div className="p-4 rounded-xl border border-dashed border-[#E2E4DF] flex flex-col items-center justify-center text-center hover:bg-[#F7F6F1] cursor-pointer">
            <span className="text-xs font-bold text-[#287A59]">+ Add Tigo Pesa / Airtel Money</span>
            <span className="text-[10px] text-[#68756F] mt-0.5">Instant activation</span>
          </div>
        </div>
      </div>

      {/* Invoices History Table */}
      <div className="bg-white rounded-2xl border border-[#E2E4DF] shadow-2xs overflow-hidden">
        <div className="p-5 border-b border-[#E2E4DF]">
          <h3 className="text-sm font-bold text-[#10231C]">Invoices & VAT Receipts</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-[#E2E4DF] bg-[#F7F6F1] text-[#68756F] font-semibold">
                <th className="py-3 px-4">Invoice ID</th>
                <th className="py-3 px-3">Date</th>
                <th className="py-3 px-3">Amount</th>
                <th className="py-3 px-3">Status</th>
                <th className="py-3 px-4 text-right">Receipt</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E2E4DF]">
              {billingInfo.invoices.map((inv) => (
                <tr key={inv.id} className="hover:bg-[#F7F6F1]">
                  <td className="py-3.5 px-4 font-mono font-bold text-[#10231C]">{inv.id}</td>
                  <td className="py-3.5 px-3 text-[#68756F]">{inv.date}</td>
                  <td className="py-3.5 px-3 font-bold text-[#10231C]">{inv.amount}</td>
                  <td className="py-3.5 px-3">
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">
                      {inv.status}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-right">
                    <button className="text-[#287A59] font-bold hover:underline inline-flex items-center gap-1">
                      <Download className="w-3 h-3" /> Download PDF
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
export  default BillingPage;
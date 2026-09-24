import { useState } from 'react';
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

export const BillingPage = ({ billingInfo = {}, t }) => {
  const usage = {
    conversationsUsed: 0,
    conversationsLimit: 2500,
    aiResponsesUsed: 0,
    aiResponsesLimit: 2500,
    nextBillingDate: 'the next billing cycle',
    ...billingInfo,
  };
  const [selectedPlan, setSelectedPlan] = useState('pro');
  const [currencyMode, setCurrencyMode] = useState('tzs');
  const [showUpgradeSuccess, setShowUpgradeSuccess] = useState(false);
  const [selectedPayment, setSelectedPayment] = useState(null);
  const [paymentNumber, setPaymentNumber] = useState('');
  const [paymentMessage, setPaymentMessage] = useState('');
  const [paymentMode, setPaymentMode] = useState('mobile');
  const [selectedBank, setSelectedBank] = useState(null);

  const paymentMethods = [
    { id: 'vodacom', name: 'Vodacom M-Pesa', shortName: 'Vodacom', color: '#E60000', prefix: '074, 075, 076' },
    { id: 'halotel', name: 'Halopesa', shortName: 'Halotel', color: '#F58220', prefix: '062' },
    { id: 'tigo', name: 'Tigo Pesa', shortName: 'Tigo', color: '#0066B3', prefix: '065, 067, 071' },
    { id: 'airtel', name: 'Airtel Money', shortName: 'Airtel', color: '#ED1C24', prefix: '068, 069, 078' },
  ];
  const banks = [
    { id: 'crdb', name: 'CRDB Bank', domain: 'crdbbank.co.tz', details: 'Business account transfer' },
    { id: 'nmb', name: 'NMB Bank', domain: 'nmbbank.co.tz', details: 'Business account transfer' },
    { id: 'nbc', name: 'NBC Bank', domain: 'nbc.co.tz', details: 'Business account transfer' },
    { id: 'stanbic', name: 'Stanbic Bank', domain: 'stanbicbank.co.tz', details: 'Business account transfer' },
    { id: 'absa', name: 'Absa Bank Tanzania', domain: 'absa.co.tz', details: 'Business account transfer' },
    { id: 'exim', name: 'Exim Bank Tanzania', domain: 'eximbank.co.tz', details: 'Business account transfer' },
    { id: 'equity', name: 'Equity Bank Tanzania', domain: 'equitybank.co.tz', details: 'Business account transfer' },
    { id: 'dtb', name: 'DTB Bank Tanzania', domain: 'diamondtrust.co.tz', details: 'Business account transfer' },
  ];

  function handlePaymentSubmit(event) {
    event.preventDefault();
    const normalized = paymentNumber.replace(/\D/g, '');
    if (!selectedPayment) {
      setPaymentMessage('Select a mobile-money provider first.');
      return;
    }
    if (!/^0\d{9}$/.test(normalized)) {
      setPaymentMessage('Enter a valid Tanzanian mobile number, for example 0754123456.');
      return;
    }
    setPaymentMessage(`${selectedPayment.name} is selected for ${normalized}. Payment gateway setup is required before a charge can be initiated.`);
  }

  function selectBank(bank) {
    setSelectedBank(bank);
    setPaymentMessage(`${bank.name} selected. Bank account details will appear when the business settlement account is configured.`);
  }

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
    <div className="p-4 sm:p-6 md:p-8 max-w-7xl mx-auto space-y-8" style={{ color: t?.text }}>
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
              <span>{usage.conversationsUsed.toLocaleString()} active inquiries</span>
                <span>{usage.conversationsLimit.toLocaleString()} limit</span>
            </div>
            <div className="w-full h-3 bg-[#F7F6F1] rounded-full overflow-hidden">
              <div
                className="h-full bg-[#287A59] rounded-full"
                style={{ width: `${(usage.conversationsUsed / usage.conversationsLimit) * 100}%` }}
              />
            </div>
          </div>
          <p className="text-[11px] text-[#68756F]">
            Resets on <b>{usage.nextBillingDate}</b>. Extra volume is billed at TZS 40 per conversation.
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
              <span>{usage.aiResponsesUsed.toLocaleString()} replies sent</span>
                <span>{usage.aiResponsesLimit.toLocaleString()} limit</span>
            </div>
            <div className="w-full h-3 bg-[#F7F6F1] rounded-full overflow-hidden">
              <div
                className="h-full bg-[#35D98A] rounded-full"
                style={{ width: `${(usage.aiResponsesUsed / usage.aiResponsesLimit) * 100}%` }}
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
                        setSelectedPlan(p.id);
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
      <div className="p-4 sm:p-6 rounded-2xl space-y-4" style={{ background: t?.card || '#FFFFFF', border: `1px solid ${t?.border || '#E2E4DF'}` }}>
        <h3 className="text-base font-bold text-[#10231C]">Payment Methods (Tanzania & Cards)</h3>
        <p className="text-xs text-[#68756F]">
          Choose a mobile-money provider and save the number used for subscription payments.
        </p>

        <div className="flex flex-wrap gap-2 pt-2">
          <button type="button" onClick={() => setPaymentMode('mobile')} className={`px-3 py-2 rounded-xl text-xs font-bold ${paymentMode === 'mobile' ? 'bg-[#10231C] text-white' : 'border border-[#E2E4DF] text-[#68756F]'}`}>
            Lipa Namba / Mobile money
          </button>
          <button type="button" onClick={() => setPaymentMode('bank')} className={`px-3 py-2 rounded-xl text-xs font-bold ${paymentMode === 'bank' ? 'bg-[#10231C] text-white' : 'border border-[#E2E4DF] text-[#68756F]'}`}>
            Bank transfer
          </button>
        </div>

        {paymentMode === 'mobile' ? <>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 pt-2">
          {paymentMethods.map((method) => {
            const isSelected = selectedPayment?.id === method.id;
            return (
              <button
                type="button"
                key={method.id}
                onClick={() => { setSelectedPayment(method); setPaymentMessage(''); }}
                className="text-left p-4 rounded-xl border transition-colors"
                style={{ borderColor: isSelected ? method.color : (t?.border || '#E2E4DF'), background: isSelected ? `${method.color}12` : 'transparent' }}
              >
                <div className="flex items-center gap-2">
                  <Smartphone className="w-4 h-4" style={{ color: method.color }} />
                  <h4 className="text-xs font-bold" style={{ color: t?.text || '#10231C' }}>{method.shortName}</h4>
                </div>
                <p className="text-[11px] mt-2" style={{ color: t?.muted || '#68756F' }}>{method.name}</p>
                <p className="text-[10px] mt-1" style={{ color: t?.muted || '#68756F' }}>{method.prefix}</p>
              </button>
            );
          })}
        </div>

        <form onSubmit={handlePaymentSubmit} className="grid grid-cols-1 sm:grid-cols-[1fr_auto] gap-3 pt-2">
          <label className="text-xs font-semibold" style={{ color: t?.text || '#10231C' }}>
            Mobile-money number
            <input
              value={paymentNumber}
              onChange={(event) => { setPaymentNumber(event.target.value); setPaymentMessage(''); }}
              inputMode="numeric"
              placeholder="0754123456"
              className="mt-1.5 w-full px-3 py-2.5 rounded-xl text-sm outline-none"
              style={{ background: t?.surface || '#F7F6F1', color: t?.text || '#10231C', border: `1px solid ${t?.border || '#E2E4DF'}` }}
            />
          </label>
          <button type="submit" className="self-end px-5 py-2.5 rounded-xl text-sm font-bold" style={{ background: t?.accent || '#287A59', color: t?.accentText || '#FFFFFF' }}>
            Continue payment
          </button>
        </form>
        <div className="p-4 rounded-xl" style={{ background: t?.surface || '#F7F6F1', border: `1px solid ${t?.border || '#E2E4DF'}` }}>
          <p className="text-xs font-bold" style={{ color: t?.text || '#10231C' }}>Lipa Namba</p>
          <p className="text-sm font-mono mt-1" style={{ color: t?.accent || '#287A59' }}>
            {billingInfo.lipaNumber || 'Not configured yet'}
          </p>
          <p className="text-[11px] mt-1" style={{ color: t?.muted || '#68756F' }}>
            Use this number in your selected mobile-money app. The administrator must configure the real business number before payments are collected.
          </p>
        </div>
        </> : (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
            {banks.map((bank) => (
              <button
                type="button"
                key={bank.id}
                onClick={() => selectBank(bank)}
                className="p-3 rounded-xl border text-left transition-colors"
                style={{ borderColor: selectedBank?.id === bank.id ? (t?.accent || '#287A59') : (t?.border || '#E2E4DF'), background: selectedBank?.id === bank.id ? (t?.surface || '#F7F6F1') : 'transparent' }}
              >
                <img
                  src={`https://logo.clearbit.com/${bank.domain}`}
                  alt={`${bank.name} logo`}
                  className="w-9 h-9 mb-2 rounded-lg object-contain bg-white p-1"
                  onError={(event) => {
                    event.currentTarget.style.display = 'none';
                    event.currentTarget.nextElementSibling?.classList.remove('hidden');
                  }}
                />
                <span
                  className="hidden w-9 h-9 mb-2 rounded-lg items-center justify-center text-xs font-bold"
                  style={{ background: t?.surface || '#F7F6F1', color: t?.accent || '#287A59' }}
                >
                  {bank.name.split(' ').map((word) => word[0]).slice(0, 2).join('')}
                </span>
                <span className="block text-xs font-bold" style={{ color: t?.text || '#10231C' }}>{bank.name}</span>
                <span className="block text-[10px] mt-1" style={{ color: t?.muted || '#68756F' }}>{bank.details}</span>
              </button>
            ))}
          </div>
        )}
        {paymentMode === 'bank' && selectedBank && (
          <div className="p-4 rounded-xl" style={{ background: t?.surface || '#F7F6F1', border: `1px solid ${t?.border || '#E2E4DF'}` }}>
            <p className="text-xs font-bold" style={{ color: t?.text || '#10231C' }}>{selectedBank.name} account details</p>
            <p className="text-sm font-mono mt-1" style={{ color: t?.accent || '#287A59' }}>
              {billingInfo.bankAccounts?.[selectedBank.id] || 'Account number not configured yet'}
            </p>
            <p className="text-[11px] mt-1" style={{ color: t?.muted || '#68756F' }}>
              Configure the official settlement account before publishing payment instructions to customers.
            </p>
          </div>
        )}
        {paymentMessage && <p className="text-xs" style={{ color: paymentMessage.includes('required') || paymentMessage.includes('valid') ? '#B42318' : (t?.accent || '#287A59') }}>{paymentMessage}</p>}
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
              {(billingInfo.invoices || []).map((inv) => (
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
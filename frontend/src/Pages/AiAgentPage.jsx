import React, { useState } from 'react';
import {
  Bot,
  Sparkles,
  CheckCircle2,
  Sliders,
  BookOpen,
  Send,
  MessageSquare,
  Clock,
  Shield,
  HelpCircle,
  Plus,
  Trash2,
  Edit2,
  RefreshCw,
  Save,
  Check,
  AlertTriangle,
  Zap
} from 'lucide-react';
import { PageId } from '../../types';

interface AiAgentPageProps {
  onNavigate: (page: PageId) => void;
}

export const AiAgentPage: React.FC<AiAgentPageProps> = ({ onNavigate }) => {
  const [activeTab, setActiveTab] = useState<'teach' | 'tone' | 'rules' | 'hours' | 'preview'>('teach');

  // Business Information fields (Teach your AI about your business)
  const [businessDesc, setBusinessDesc] = useState(
    'Zawadi Emporium is a premier multi-category retail & wholesale brand based in Dar es Salaam, Tanzania. We supply organic cosmetics, high-grade hardware building materials, and contemporary apparel with rapid delivery across Dar es Salaam, Arusha, and Mwanza.'
  );
  const [productsServices, setProductsServices] = useState(
    '1. Organic Skincare & Cosmetics (Rose hydrating toner TZS 38k, Shea cream TZS 30k)\n2. Building Supplies (Dangote 42.5R cement TZS 18.2k/bag, 12mm Rebar TZS 27.5k)\n3. Fashion & Linen collections (Emerald sets TZS 145k)'
  );
  const [pricingPolicy, setPricingPolicy] = useState(
    'All retail prices are in TZS. Wholesale rates apply for quantities 10+. Payments accepted via Vodacom Lipa Namba (589201), Tigo Pesa, Airtel Money, or CRDB/NMB Bank Transfer.'
  );
  const [deliveryLocations, setDeliveryLocations] = useState(
    'Store Flagship: Kariakoo Congo Street & Masaki Slipway. Same-day delivery inside Dar es Salaam (Kinondoni, Ilala, Temeke) for TZS 3k–5k. Upcountry shipping via Tahmeed, BM Coach, or Shabiby bus services.'
  );
  const [faqItems, setFaqItems] = useState([
    { q: 'Je mnafanya delivery mikocheni au kinondoni?', a: 'Ndio! Tuna dispatch rider anayepeleka Kinondoni na Mikocheni ndani ya masaa 2 kwa gharama nafuu ya TZS 4,000.' },
    { q: 'Can I pay via Lipa Namba?', a: 'Yes, our verified Vodacom Lipa Namba is 589201 (Name: Zawadi Emporium). Once you pay, our AI validates the SMS receipt automatically.' },
    { q: 'What are your working hours?', a: 'Our physical shops are open Monday–Saturday from 8:00 AM to 7:00 PM. However, our MtejaAI Assistant answers your WhatsApp & Instagram 24/7!' }
  ]);
  const [newFaqQ, setNewFaqQ] = useState('');
  const [newFaqA, setNewFaqA] = useState('');

  // Tone of Voice
  const [tone, setTone] = useState<'friendly' | 'professional' | 'energetic'>('friendly');
  const [languageMode, setLanguageMode] = useState<'bilingual' | 'swahili' | 'english'>('bilingual');
  const [savedSuccess, setSavedSuccess] = useState(false);

  // Live Test Simulation Panel
  const [simMessages, setSimMessages] = useState<Array<{ sender: 'user' | 'ai'; text: string; intent?: string; latency?: string }>>([
    {
      sender: 'user',
      text: 'Habari, nataka kujua kama toner ya rose ipo stock na bei yake ni kiasi gani?'
    },
    {
      sender: 'ai',
      text: 'Habari! Karibu sana Zawadi Emporium 🌿 Ndio, Hydrating Rose Toner ipo stock ya kutosha kwa TZS 38,000 (150ml). Je, ungependa tukuwekee oda ya delivery ya leo hapa Dar es Salaam?',
      intent: 'Pricing & Inventory Verification',
      latency: '1.2s'
    }
  ]);
  const [simInput, setSimInput] = useState('');
  const [isSimTyping, setIsSimTyping] = useState(false);

  const handleSimSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!simInput.trim()) return;

    const userText = simInput.trim();
    setSimMessages((prev) => [...prev, { sender: 'user', text: userText }]);
    setSimInput('');
    setIsSimTyping(true);

    // AI Intent simulation based on Tanzanian query terms
    setTimeout(() => {
      let aiReply = 'Habari! Asante kwa kuwasiliana na Zawadi Emporium. Nimerekodi ujumbe wako na nakusaidia sasa hivi.';
      let intent = 'General Customer Inquiry';

      const lower = userText.toLowerCase();
      if (lower.includes('delivery') || lower.includes('wapi') || lower.includes('eneo') || lower.includes('location')) {
        aiReply = 'Maduka yetu yapo Kariakoo (Congo St) na Masaki Slipway. Pia tunafanya delivery maeneo yote ya Dar es Salaam (Kinondoni, Sinza, Masaki, Mikocheni) kwa TZS 3,000 - 5,000!';
        intent = 'Location & Delivery Logistics';
      } else if (lower.includes('bei') || lower.includes('price') || lower.includes('gharama') || lower.includes('how much')) {
        aiReply = 'Bei zetu ni: Rose Toner TZS 38,000; Dangote Cement TZS 18,200/mfuko; Nondo 12mm TZS 27,500; na Linen Fashion sets kuanzia TZS 145,000. Oda za jumla (10+ pcs) zina punguzo maalum!';
        intent = 'Product Pricing Inquiry';
      } else if (lower.includes('lipa') || lower.includes('payment') || lower.includes('mpesa') || lower.includes('tigo')) {
        aiReply = 'Unaweza kulipa kupitia Vodacom Lipa Namba 589201 (Zawadi Emporium) au Airtel Money na Tigo Pesa. Ukishatuma screenshot ya SMS, oda inaanza kupakiwa mara moja!';
        intent = 'Payment Method (Lipa Namba)';
      } else if (lower.includes('cement') || lower.includes('nondo') || lower.includes('juma')) {
        aiReply = 'Stock ya Dangote 42.5R na nondo za mm 12 ipo Kariakoo na Tegeta. Kwa oda ya jumla, nimeiweka kwenye orodha ya Bw. Khamis Mgofi akupigie simu kutoa quotation rasmi!';
        intent = 'High-Value Hardware Quote Escalation';
      } else {
        aiReply = 'Habari ndugu mteja! Asante kwa kuwasiliana na Zawadi Emporium. Tumeipokea oda yako na tunaifanyia kazi kwa haraka zaidi. Je, una swali jingine kuhusu bidhaa zetu?';
        intent = 'Conversational Assistant Response';
      }

      setSimMessages((prev) => [
        ...prev,
        {
          sender: 'ai',
          text: aiReply,
          intent,
          latency: '1.3s'
        }
      ]);
      setIsSimTyping(false);
    }, 800);
  };

  const handleSaveConfig = () => {
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 2500);
  };

  const handleAddFaq = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newFaqQ || !newFaqA) return;
    setFaqItems([...faqItems, { q: newFaqQ, a: newFaqA }]);
    setNewFaqQ('');
    setNewFaqA('');
  };

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-6">
      {/* Top Header Card */}
      <div className="bg-white p-6 rounded-2xl border border-[#E2E4DF] shadow-2xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-[#10231C] text-[#35D98A] flex items-center justify-center font-bold">
              <Bot className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-extrabold text-[#10231C] tracking-tight">Your AI Agent</h2>
                <span className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-[#35D98A]/20 text-[#10231C]">
                  <span className="w-2 h-2 rounded-full bg-[#287A59] animate-pulse" />
                  <span>Online</span>
                </span>
              </div>
              <p className="text-xs text-[#68756F] mt-0.5">
                Configured for Zawadi Emporium (WhatsApp, Instagram, Email, Calls)
              </p>
            </div>
          </div>
        </div>

        {/* Primary Metric Pill */}
        <div className="flex items-center gap-3 p-3 rounded-xl bg-[#287A59]/10 border border-[#287A59]/20">
          <Sparkles className="w-5 h-5 text-[#287A59]" />
          <div>
            <p className="text-xs font-bold text-[#10231C]">
              AI is handling 82% of conversations automatically.
            </p>
            <p className="text-[11px] text-[#68756F]">
              946 autonomous replies • 1.4s average response latency
            </p>
          </div>
        </div>
      </div>

      {/* Tabs Menu */}
      <div className="flex items-center gap-1 border-b border-[#E2E4DF] overflow-x-auto pb-1">
        {[
          { id: 'teach', label: '1. Teach Your AI' },
          { id: 'tone', label: '2. Tone & Languages' },
          { id: 'rules', label: '3. Escalation Rules' },
          { id: 'hours', label: '4. Working Hours' },
          { id: 'preview', label: '5. Live AI Simulator' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`px-4 py-2.5 text-xs font-bold border-b-2 transition-colors whitespace-nowrap ${
              activeTab === tab.id
                ? 'border-[#287A59] text-[#287A59]'
                : 'border-transparent text-[#68756F] hover:text-[#10231C]'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* TAB 1: Teach Your AI About Your Business */}
      {activeTab === 'teach' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-2xl border border-[#E2E4DF] shadow-2xs space-y-6">
            <div className="flex items-center justify-between border-b border-[#E2E4DF] pb-4">
              <div>
                <h3 className="text-base font-bold text-[#10231C]">Teach Your AI About Your Business</h3>
                <p className="text-xs text-[#68756F]">
                  The information provided here powers accurate, brand-aligned Swahili and English replies.
                </p>
              </div>
              <button
                onClick={handleSaveConfig}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-[#287A59] hover:bg-[#1f5f45] text-white text-xs font-bold transition-colors shadow-2xs"
              >
                {savedSuccess ? <Check className="w-3.5 h-3.5" /> : <Save className="w-3.5 h-3.5" />}
                <span>{savedSuccess ? 'Changes Saved!' : 'Save Knowledge'}</span>
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Business Description */}
              <div>
                <label className="block text-xs font-bold text-[#10231C] mb-1.5">
                  Business Description & Core Identity
                </label>
                <textarea
                  rows={4}
                  value={businessDesc}
                  onChange={(e) => setBusinessDesc(e.target.value)}
                  className="w-full p-3 text-xs rounded-xl border border-[#E2E4DF] bg-[#F7F6F1] focus:bg-white focus:outline-none focus:border-[#287A59]"
                />
              </div>

              {/* Products & Services */}
              <div>
                <label className="block text-xs font-bold text-[#10231C] mb-1.5">
                  Products, Inventory & Catalog Details
                </label>
                <textarea
                  rows={4}
                  value={productsServices}
                  onChange={(e) => setProductsServices(e.target.value)}
                  className="w-full p-3 text-xs rounded-xl border border-[#E2E4DF] bg-[#F7F6F1] focus:bg-white focus:outline-none focus:border-[#287A59]"
                />
              </div>

              {/* Pricing & Lipa Namba */}
              <div>
                <label className="block text-xs font-bold text-[#10231C] mb-1.5">
                  Pricing, Wholesale Minimums & Payment (Lipa Namba)
                </label>
                <textarea
                  rows={4}
                  value={pricingPolicy}
                  onChange={(e) => setPricingPolicy(e.target.value)}
                  className="w-full p-3 text-xs rounded-xl border border-[#E2E4DF] bg-[#F7F6F1] focus:bg-white focus:outline-none focus:border-[#287A59]"
                />
              </div>

              {/* Locations & Delivery */}
              <div>
                <label className="block text-xs font-bold text-[#10231C] mb-1.5">
                  Physical Stores, Delivery Zones & Dispatch Rates
                </label>
                <textarea
                  rows={4}
                  value={deliveryLocations}
                  onChange={(e) => setDeliveryLocations(e.target.value)}
                  className="w-full p-3 text-xs rounded-xl border border-[#E2E4DF] bg-[#F7F6F1] focus:bg-white focus:outline-none focus:border-[#287A59]"
                />
              </div>
            </div>
          </div>

          {/* FAQs Knowledge Base */}
          <div className="bg-white p-6 rounded-2xl border border-[#E2E4DF] shadow-2xs space-y-4">
            <h3 className="text-sm font-bold text-[#10231C]">Frequently Asked Customer Questions (FAQs)</h3>
            <p className="text-xs text-[#68756F]">Your AI matches incoming inquiries against these verified answers.</p>

            <div className="space-y-3">
              {faqItems.map((faq, idx) => (
                <div key={idx} className="p-3.5 rounded-xl bg-[#F7F6F1] border border-[#E2E4DF] space-y-1">
                  <div className="flex items-center justify-between text-xs font-bold text-[#10231C]">
                    <span>Q: {faq.q}</span>
                    <button
                      onClick={() => setFaqItems(faqItems.filter((_, i) => i !== idx))}
                      className="text-[#68756F] hover:text-red-600 p-1"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                  <p className="text-xs text-[#68756F]">A: {faq.a}</p>
                </div>
              ))}
            </div>

            {/* Add FAQ form */}
            <form onSubmit={handleAddFaq} className="pt-3 border-t border-[#E2E4DF] space-y-3">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <input
                  type="text"
                  placeholder="New Question (e.g. Mnafungua Jumapili?)"
                  value={newFaqQ}
                  onChange={(e) => setNewFaqQ(e.target.value)}
                  className="p-2.5 text-xs rounded-xl border border-[#E2E4DF] bg-[#F7F6F1] focus:bg-white focus:outline-none"
                />
                <input
                  type="text"
                  placeholder="Official Answer (e.g. Ndio, Slipway shop inafungua 10am - 5pm)"
                  value={newFaqA}
                  onChange={(e) => setNewFaqA(e.target.value)}
                  className="p-2.5 text-xs rounded-xl border border-[#E2E4DF] bg-[#F7F6F1] focus:bg-white focus:outline-none"
                />
              </div>
              <button
                type="submit"
                disabled={!newFaqQ || !newFaqA}
                className="px-4 py-2 rounded-xl bg-[#10231C] text-white text-xs font-bold hover:bg-[#287A59] disabled:opacity-50"
              >
                + Add FAQ to Knowledge Base
              </button>
            </form>
          </div>
        </div>
      )}

      {/* TAB 2: Tone of Voice & Languages */}
      {activeTab === 'tone' && (
        <div className="bg-white p-6 rounded-2xl border border-[#E2E4DF] shadow-2xs space-y-6">
          <div>
            <h3 className="text-base font-bold text-[#10231C]">Tone of Voice & Language Engine</h3>
            <p className="text-xs text-[#68756F]">
              Control how the AI addresses Tanzanian shoppers on WhatsApp and Instagram.
            </p>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-[#10231C] mb-2">Persona Style</label>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {[
                  { id: 'friendly', title: 'Warm & Hospitable', desc: 'Uses courteous Swahili greetings ("Karibu sana", "Habari ya asubuhi") with clean emoji touches.' },
                  { id: 'professional', title: 'Executive & Concise', desc: 'Direct, clear pricing tables, perfect for corporate and high-volume B2B inquiries.' },
                  { id: 'energetic', title: 'Modern & Social', desc: 'Tailored for Instagram fashion and beauty trends, encouraging quick checkout.' },
                ].map((item) => (
                  <div
                    key={item.id}
                    onClick={() => setTone(item.id as any)}
                    className={`p-4 rounded-xl border cursor-pointer transition-all ${
                      tone === item.id
                        ? 'border-[#287A59] bg-[#287A59]/5 ring-1 ring-[#287A59]'
                        : 'border-[#E2E4DF] hover:bg-[#F7F6F1]'
                    }`}
                  >
                    <h4 className="text-xs font-bold text-[#10231C]">{item.title}</h4>
                    <p className="text-[11px] text-[#68756F] mt-1">{item.desc}</p>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-[#10231C] mb-2">Language Handling</label>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {[
                  { id: 'bilingual', title: 'Auto-Detect Swahili & English', desc: 'Replies in whichever language the customer initiated the chat in.' },
                  { id: 'swahili', title: 'Pure Kiswahili First', desc: 'Always prioritizes authentic modern Tanzanian Swahili.' },
                  { id: 'english', title: 'English First', desc: 'Prefers formal English unless customer specifically writes Swahili.' },
                ].map((item) => (
                  <div
                    key={item.id}
                    onClick={() => setLanguageMode(item.id as any)}
                    className={`p-4 rounded-xl border cursor-pointer transition-all ${
                      languageMode === item.id
                        ? 'border-[#287A59] bg-[#287A59]/5 ring-1 ring-[#287A59]'
                        : 'border-[#E2E4DF] hover:bg-[#F7F6F1]'
                    }`}
                  >
                    <h4 className="text-xs font-bold text-[#10231C]">{item.title}</h4>
                    <p className="text-[11px] text-[#68756F] mt-1">{item.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="pt-4 border-t border-[#E2E4DF] flex justify-end">
            <button
              onClick={handleSaveConfig}
              className="px-4 py-2 rounded-xl bg-[#287A59] text-white text-xs font-bold hover:bg-[#1f5f45]"
            >
              Save Tone Settings
            </button>
          </div>
        </div>
      )}

      {/* TAB 3: Escalation Rules */}
      {activeTab === 'rules' && (
        <div className="bg-white p-6 rounded-2xl border border-[#E2E4DF] shadow-2xs space-y-6">
          <div>
            <h3 className="text-base font-bold text-[#10231C]">Human Handoff & Escalation Rules</h3>
            <p className="text-xs text-[#68756F]">
              Determine when the AI should notify human agents instead of answering autonomously.
            </p>
          </div>

          <div className="space-y-3">
            {[
              {
                title: 'High-Value Orders (> TZS 1,000,000)',
                desc: 'When inquiry mentions wholesale cement, container quantities, or high values, draft provisional reply and alert owner.',
                enabled: true
              },
              {
                title: 'Customer Frustration / Negative Sentiment',
                desc: 'If customer expresses delays or frustration, pause AI instantly and assign to Senior Agent (Salma Rashid).',
                enabled: true
              },
              {
                title: 'Payment Discrepancy & Verification',
                desc: 'If customer submits a payment screenshot with unverified transaction ID, flag for manual bank review.',
                enabled: true
              },
              {
                title: 'Custom Product Tailoring / Custom Dimensions',
                desc: 'For non-standard garment sizes or technical solar specifications, request call back.',
                enabled: false
              }
            ].map((rule, idx) => (
              <div
                key={idx}
                className="p-4 rounded-xl border border-[#E2E4DF] flex items-center justify-between gap-4 hover:bg-[#F7F6F1] transition-colors"
              >
                <div>
                  <h4 className="text-xs font-bold text-[#10231C]">{rule.title}</h4>
                  <p className="text-xs text-[#68756F] mt-0.5">{rule.desc}</p>
                </div>
                <input
                  type="checkbox"
                  defaultChecked={rule.enabled}
                  className="w-4 h-4 rounded text-[#287A59] focus:ring-[#287A59]"
                />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 4: Working Hours */}
      {activeTab === 'hours' && (
        <div className="bg-white p-6 rounded-2xl border border-[#E2E4DF] shadow-2xs space-y-6">
          <div>
            <h3 className="text-base font-bold text-[#10231C]">Working Hours & 24/7 Night Coverage</h3>
            <p className="text-xs text-[#68756F]">
              Keep your business open while your competitors are asleep.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-4 rounded-xl bg-[#F7F6F1] border border-[#E2E4DF] space-y-3">
              <h4 className="text-xs font-bold text-[#10231C]">Store Operating Hours</h4>
              <div className="space-y-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-[#68756F]">Monday – Friday</span>
                  <span className="font-semibold text-[#10231C]">08:00 AM – 07:00 PM EAT</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#68756F]">Saturday</span>
                  <span className="font-semibold text-[#10231C]">09:00 AM – 06:00 PM EAT</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#68756F]">Sunday</span>
                  <span className="font-semibold text-[#10231C]">Closed (Physical Store)</span>
                </div>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-[#287A59]/10 border border-[#287A59]/20 space-y-2">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-[#287A59]" />
                <h4 className="text-xs font-bold text-[#10231C]">MtejaAI Night Concierge (Active)</h4>
              </div>
              <p className="text-xs text-[#68756F] leading-relaxed">
                During closed hours (7:00 PM - 8:00 AM), MtejaAI continues answering inquiries, recording orders, and collecting delivery addresses so your store starts every morning with prepaid orders ready to ship.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* TAB 5: AI Preview/Test Panel (Simulate Customer Conversation) */}
      {activeTab === 'preview' && (
        <div className="bg-white rounded-2xl border border-[#E2E4DF] shadow-2xs overflow-hidden flex flex-col md:flex-row h-[600px]">
          {/* Simulation Settings / Controls */}
          <div className="w-full md:w-80 p-5 border-r border-[#E2E4DF] bg-[#F7F6F1] space-y-4">
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-[#10231C]">
                Simulation Sandbox
              </h3>
              <p className="text-[11px] text-[#68756F] mt-0.5">
                Simulate a real Tanzanian customer asking questions in Swahili or English.
              </p>
            </div>

            <div className="p-3 rounded-xl bg-white border border-[#E2E4DF] space-y-2 text-xs">
              <div className="font-bold text-[#10231C]">Sample Quick Prompts:</div>
              <button
                onClick={() => setSimInput('Habari, mnazo cement za Dangote na nondo?')}
                className="w-full text-left p-2 rounded-lg bg-[#F7F6F1] hover:bg-[#EAE8E0] text-[11px] text-[#14201B]"
              >
                "Habari, mnazo cement za Dangote na nondo?"
              </button>
              <button
                onClick={() => setSimInput('Je mnafanya delivery Kinondoni leo na bei ya toner ni ngapi?')}
                className="w-full text-left p-2 rounded-lg bg-[#F7F6F1] hover:bg-[#EAE8E0] text-[11px] text-[#14201B]"
              >
                "Je mnafanya delivery Kinondoni leo na bei ya toner ni ngapi?"
              </button>
              <button
                onClick={() => setSimInput('Naomba namba yenu ya Lipa Namba ya Vodacom.')}
                className="w-full text-left p-2 rounded-lg bg-[#F7F6F1] hover:bg-[#EAE8E0] text-[11px] text-[#14201B]"
              >
                "Naomba namba yenu ya Lipa Namba ya Vodacom."
              </button>
            </div>

            <div className="p-3 rounded-xl bg-[#287A59]/10 border border-[#287A59]/20 text-xs">
              <span className="font-bold text-[#287A59]">Live Telemetry:</span>
              <p className="text-[11px] text-[#68756F] mt-1">Model: Mteja-Agentic-V2</p>
              <p className="text-[11px] text-[#68756F]">Active Knowledge Items: 142</p>
              <p className="text-[11px] text-[#68756F]">Avg Latency: 1.2s</p>
            </div>
          </div>

          {/* Simulation Chat Surface */}
          <div className="flex-1 flex flex-col h-full bg-white">
            <div className="p-3.5 border-b border-[#E2E4DF] flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-[#35D98A] animate-pulse" />
                <span className="text-xs font-bold text-[#10231C]">Live MtejaAI Test Bot</span>
              </div>
              <button
                onClick={() => setSimMessages([])}
                className="text-[11px] text-[#68756F] hover:text-[#10231C] flex items-center gap-1"
              >
                <RefreshCw className="w-3 h-3" /> Clear Chat
              </button>
            </div>

            {/* Chat Messages */}
            <div className="flex-1 p-4 overflow-y-auto space-y-3">
              {simMessages.map((msg, i) => (
                <div
                  key={i}
                  className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}
                >
                  <div
                    className={`max-w-md p-3 rounded-xl text-xs leading-relaxed ${
                      msg.sender === 'user'
                        ? 'bg-[#10231C] text-white rounded-br-none'
                        : 'bg-[#F7F6F1] border border-[#E2E4DF] text-[#14201B] rounded-bl-none'
                    }`}
                  >
                    <p>{msg.text}</p>
                    {msg.intent && (
                      <div className="mt-2 pt-1.5 border-t border-[#E2E4DF] flex items-center justify-between text-[10px] text-[#287A59]">
                        <span>Intent: <b>{msg.intent}</b></span>
                        <span>⚡ {msg.latency}</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {isSimTyping && (
                <div className="flex items-center gap-1.5 text-xs text-[#68756F] p-2">
                  <Sparkles className="w-3.5 h-3.5 text-[#287A59] animate-spin" />
                  <span>MtejaAI is searching store knowledge base...</span>
                </div>
              )}
            </div>

            {/* Simulation Composer */}
            <form onSubmit={handleSimSend} className="p-3 border-t border-[#E2E4DF] flex items-center gap-2">
              <input
                type="text"
                placeholder="Type a test question in Swahili or English..."
                value={simInput}
                onChange={(e) => setSimInput(e.target.value)}
                className="flex-1 p-2.5 text-xs rounded-xl border border-[#E2E4DF] bg-[#F7F6F1] focus:bg-white focus:outline-none focus:border-[#287A59]"
              />
              <button
                type="submit"
                disabled={!simInput.trim() || isSimTyping}
                className="px-4 py-2.5 rounded-xl bg-[#287A59] text-white text-xs font-bold hover:bg-[#1f5f45] disabled:opacity-50 flex items-center gap-1"
              >
                <span>Send</span>
                <Send className="w-3.5 h-3.5" />
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
export default AiAgentPage;
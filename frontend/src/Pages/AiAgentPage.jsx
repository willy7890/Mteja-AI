import { useState } from 'react';
import {
  Bot,
  Sparkles,
  Send,
  Trash2,
  RefreshCw,
  Save,
  Check,
} from 'lucide-react';

function AiAgentPage() {
  const [activeTab, setActiveTab] = useState('teach');

  const [businessDesc, setBusinessDesc] = useState('');
  const [productsServices, setProductsServices] = useState('');
  const [pricingPolicy, setPricingPolicy] = useState('');
  const [deliveryLocations, setDeliveryLocations] = useState('');
  const [faqItems, setFaqItems] = useState([]);
  const [newFaqQ, setNewFaqQ] = useState('');
  const [newFaqA, setNewFaqA] = useState('');

  const [tone, setTone] = useState('friendly');
  const [languageMode, setLanguageMode] = useState('bilingual');
  const [savedSuccess, setSavedSuccess] = useState(false);

  const [simMessages, setSimMessages] = useState([]);
  const [simInput, setSimInput] = useState('');
  const [isSimTyping, setIsSimTyping] = useState(false);

  const handleSimSend = (e) => {
    e.preventDefault();
    if (!simInput.trim()) return;

    const userText = simInput.trim();
    setSimMessages((prev) => [...prev, { sender: 'user', text: userText }]);
    setSimInput('');
    setIsSimTyping(true);

    setTimeout(() => {
      let aiReply =
        'Asante kwa ujumbe wako. Nimerekodi na nitakusaidia sasa hivi.';
      let intent = 'General Inquiry';

      const lower = userText.toLowerCase();
      if (
        lower.includes('delivery') ||
        lower.includes('wapi') ||
        lower.includes('eneo')
      ) {
        aiReply =
          'Tunafanya delivery maeneo mbalimbali. Tafadhali niambie eneo lako ili nikupe gharama sahihi.';
        intent = 'Delivery Inquiry';
      } else if (
        lower.includes('bei') ||
        lower.includes('price') ||
        lower.includes('gharama')
      ) {
        aiReply =
          'Bei zinategemea bidhaa. Niambie bidhaa unayotafuta ili nikupe bei sahihi.';
        intent = 'Pricing Inquiry';
      } else if (
        lower.includes('lipa') ||
        lower.includes('payment') ||
        lower.includes('mpesa')
      ) {
        aiReply =
          'Unaweza kulipa kupitia mobile money au bank transfer. Nitakupa maelezo baada ya kuthibitisha oda.';
        intent = 'Payment Inquiry';
      }

      setSimMessages((prev) => [
        ...prev,
        { sender: 'ai', text: aiReply, intent, latency: '1.2s' },
      ]);
      setIsSimTyping(false);
    }, 800);
  };

  const handleSaveConfig = () => {
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 2500);
    // Baadaye: apiPost('/api/v1/ai-agent/config', { businessDesc, ... })
  };

  const handleAddFaq = (e) => {
    e.preventDefault();
    if (!newFaqQ || !newFaqA) return;
    setFaqItems([...faqItems, { q: newFaqQ, a: newFaqA }]);
    setNewFaqQ('');
    setNewFaqA('');
  };

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-[#E2E4DF] flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-[#10231C] text-[#35D98A] flex items-center justify-center">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xl font-extrabold text-[#10231C]">Your AI Agent</h2>
              <span className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-[#35D98A]/20 text-[#10231C]">
                <span className="w-2 h-2 rounded-full bg-[#287A59] animate-pulse" />
                Online
              </span>
            </div>
            <p className="text-xs text-[#68756F] mt-0.5">
              Configure how your AI replies across WhatsApp, Telegram, Instagram & Email
            </p>
          </div>
        </div>
      </div>

      {/* Tabs */}
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
            onClick={() => setActiveTab(tab.id)}
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

      {/* TAB 1: Teach */}
      {activeTab === 'teach' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-2xl border border-[#E2E4DF] space-y-6">
            <div className="flex items-center justify-between border-b border-[#E2E4DF] pb-4">
              <div>
                <h3 className="text-base font-bold text-[#10231C]">
                  Teach Your AI About Your Business
                </h3>
                <p className="text-xs text-[#68756F]">
                  Information here powers accurate Swahili and English replies.
                </p>
              </div>
              <button
                onClick={handleSaveConfig}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-[#287A59] text-white text-xs font-bold"
              >
                {savedSuccess ? <Check className="w-3.5 h-3.5" /> : <Save className="w-3.5 h-3.5" />}
                {savedSuccess ? 'Saved!' : 'Save Knowledge'}
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-xs font-bold text-[#10231C] mb-1.5">
                  Business Description
                </label>
                <textarea
                  rows={4}
                  value={businessDesc}
                  onChange={(e) => setBusinessDesc(e.target.value)}
                  placeholder="Describe your business..."
                  className="w-full p-3 text-xs rounded-xl border border-[#E2E4DF] bg-[#F7F6F1] focus:bg-white focus:outline-none focus:border-[#287A59]"
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-[#10231C] mb-1.5">
                  Products & Services
                </label>
                <textarea
                  rows={4}
                  value={productsServices}
                  onChange={(e) => setProductsServices(e.target.value)}
                  placeholder="List products, prices, stock..."
                  className="w-full p-3 text-xs rounded-xl border border-[#E2E4DF] bg-[#F7F6F1] focus:bg-white focus:outline-none focus:border-[#287A59]"
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-[#10231C] mb-1.5">
                  Pricing & Payment Methods
                </label>
                <textarea
                  rows={4}
                  value={pricingPolicy}
                  onChange={(e) => setPricingPolicy(e.target.value)}
                  placeholder="Lipa Namba, bank details, wholesale rules..."
                  className="w-full p-3 text-xs rounded-xl border border-[#E2E4DF] bg-[#F7F6F1] focus:bg-white focus:outline-none focus:border-[#287A59]"
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-[#10231C] mb-1.5">
                  Locations & Delivery
                </label>
                <textarea
                  rows={4}
                  value={deliveryLocations}
                  onChange={(e) => setDeliveryLocations(e.target.value)}
                  placeholder="Stores, delivery zones, rates..."
                  className="w-full p-3 text-xs rounded-xl border border-[#E2E4DF] bg-[#F7F6F1] focus:bg-white focus:outline-none focus:border-[#287A59]"
                />
              </div>
            </div>
          </div>

          {/* FAQs */}
          <div className="bg-white p-6 rounded-2xl border border-[#E2E4DF] space-y-4">
            <h3 className="text-sm font-bold text-[#10231C]">FAQs</h3>
            <p className="text-xs text-[#68756F]">
              AI will match customer questions against these answers.
            </p>

            <div className="space-y-3">
              {faqItems.length === 0 && (
                <p className="text-xs text-[#68756F]">No FAQs yet. Add your first one below.</p>
              )}
              {faqItems.map((faq, idx) => (
                <div
                  key={idx}
                  className="p-3.5 rounded-xl bg-[#F7F6F1] border border-[#E2E4DF] space-y-1"
                >
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

            <form onSubmit={handleAddFaq} className="pt-3 border-t border-[#E2E4DF] space-y-3">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <input
                  type="text"
                  placeholder="Question"
                  value={newFaqQ}
                  onChange={(e) => setNewFaqQ(e.target.value)}
                  className="p-2.5 text-xs rounded-xl border border-[#E2E4DF] bg-[#F7F6F1] focus:bg-white focus:outline-none"
                />
                <input
                  type="text"
                  placeholder="Answer"
                  value={newFaqA}
                  onChange={(e) => setNewFaqA(e.target.value)}
                  className="p-2.5 text-xs rounded-xl border border-[#E2E4DF] bg-[#F7F6F1] focus:bg-white focus:outline-none"
                />
              </div>
              <button
                type="submit"
                disabled={!newFaqQ || !newFaqA}
                className="px-4 py-2 rounded-xl bg-[#10231C] text-white text-xs font-bold disabled:opacity-50"
              >
                + Add FAQ
              </button>
            </form>
          </div>
        </div>
      )}

      {/* TAB 2: Tone */}
      {activeTab === 'tone' && (
        <div className="bg-white p-6 rounded-2xl border border-[#E2E4DF] space-y-6">
          <div>
            <h3 className="text-base font-bold text-[#10231C]">Tone & Language</h3>
            <p className="text-xs text-[#68756F]">
              How the AI speaks to customers.
            </p>
          </div>

          <div>
            <label className="block text-xs font-bold text-[#10231C] mb-2">Persona</label>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {[
                { id: 'friendly', title: 'Warm & Friendly' },
                { id: 'professional', title: 'Professional' },
                { id: 'energetic', title: 'Energetic' },
              ].map((item) => (
                <div
                  key={item.id}
                  onClick={() => setTone(item.id)}
                  className={`p-4 rounded-xl border cursor-pointer ${
                    tone === item.id
                      ? 'border-[#287A59] bg-[#287A59]/5'
                      : 'border-[#E2E4DF]'
                  }`}
                >
                  <h4 className="text-xs font-bold text-[#10231C]">{item.title}</h4>
                </div>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-[#10231C] mb-2">Language</label>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {[
                { id: 'bilingual', title: 'Auto Swahili & English' },
                { id: 'swahili', title: 'Kiswahili First' },
                { id: 'english', title: 'English First' },
              ].map((item) => (
                <div
                  key={item.id}
                  onClick={() => setLanguageMode(item.id)}
                  className={`p-4 rounded-xl border cursor-pointer ${
                    languageMode === item.id
                      ? 'border-[#287A59] bg-[#287A59]/5'
                      : 'border-[#E2E4DF]'
                  }`}
                >
                  <h4 className="text-xs font-bold text-[#10231C]">{item.title}</h4>
                </div>
              ))}
            </div>
          </div>

          <div className="pt-4 border-t border-[#E2E4DF] flex justify-end">
            <button
              onClick={handleSaveConfig}
              className="px-4 py-2 rounded-xl bg-[#287A59] text-white text-xs font-bold"
            >
              Save Tone Settings
            </button>
          </div>
        </div>
      )}

      {/* TAB 3: Rules */}
      {activeTab === 'rules' && (
        <div className="bg-white p-6 rounded-2xl border border-[#E2E4DF] space-y-6">
          <div>
            <h3 className="text-base font-bold text-[#10231C]">Escalation Rules</h3>
            <p className="text-xs text-[#68756F]">
              When AI should hand over to a human.
            </p>
          </div>
          <div className="space-y-3">
            {[
              {
                title: 'High-value orders',
                desc: 'Alert owner for large or wholesale inquiries.',
              },
              {
                title: 'Customer frustration',
                desc: 'Pause AI and assign to human agent.',
              },
              {
                title: 'Payment issues',
                desc: 'Flag unverified payments for review.',
              },
            ].map((rule, idx) => (
              <div
                key={idx}
                className="p-4 rounded-xl border border-[#E2E4DF] flex items-center justify-between gap-4"
              >
                <div>
                  <h4 className="text-xs font-bold text-[#10231C]">{rule.title}</h4>
                  <p className="text-xs text-[#68756F] mt-0.5">{rule.desc}</p>
                </div>
                <input type="checkbox" defaultChecked className="w-4 h-4 rounded" />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 4: Hours */}
      {activeTab === 'hours' && (
        <div className="bg-white p-6 rounded-2xl border border-[#E2E4DF] space-y-6">
          <div>
            <h3 className="text-base font-bold text-[#10231C]">Working Hours</h3>
            <p className="text-xs text-[#68756F]">
              AI can still reply outside store hours.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-4 rounded-xl bg-[#F7F6F1] border border-[#E2E4DF] space-y-2 text-xs">
              <h4 className="font-bold text-[#10231C]">Store Hours</h4>
              <div className="flex justify-between">
                <span className="text-[#68756F]">Mon – Fri</span>
                <span className="font-semibold">08:00 – 19:00</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#68756F]">Saturday</span>
                <span className="font-semibold">09:00 – 18:00</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#68756F]">Sunday</span>
                <span className="font-semibold">Closed</span>
              </div>
            </div>
            <div className="p-4 rounded-xl bg-[#287A59]/10 border border-[#287A59]/20">
              <div className="flex items-center gap-2 mb-2">
                <Sparkles className="w-4 h-4 text-[#287A59]" />
                <h4 className="text-xs font-bold text-[#10231C]">24/7 AI Coverage</h4>
              </div>
              <p className="text-xs text-[#68756F]">
                Outside store hours, AI continues answering, taking orders and collecting details.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* TAB 5: Simulator */}
      {activeTab === 'preview' && (
        <div className="bg-white rounded-2xl border border-[#E2E4DF] overflow-hidden flex flex-col md:flex-row h-[min(560px,calc(100dvh-10rem))] min-h-[420px]">
          <div className="w-full md:w-72 p-5 border-r border-[#E2E4DF] bg-[#F7F6F1] space-y-4">
            <div>
              <h3 className="text-xs font-bold uppercase text-[#10231C]">Simulator</h3>
              <p className="text-[11px] text-[#68756F] mt-0.5">
                Test how AI replies before going live.
              </p>
            </div>
            <div className="space-y-2">
              {[
                'Habari, mnazo delivery Kinondoni?',
                'Bei ya bidhaa yenu ni ngapi?',
                'Naomba namba ya Lipa Namba',
              ].map((q) => (
                <button
                  key={q}
                  onClick={() => setSimInput(q)}
                  className="w-full text-left p-2 rounded-lg bg-white border border-[#E2E4DF] text-[11px] text-[#14201B] hover:bg-[#EAE8E0]"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>

          <div className="flex-1 flex flex-col">
            <div className="p-3 border-b border-[#E2E4DF] flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-[#35D98A] animate-pulse" />
                <span className="text-xs font-bold text-[#10231C]">Test Bot</span>
              </div>
              <button
                onClick={() => setSimMessages([])}
                className="text-[11px] text-[#68756F] flex items-center gap-1"
              >
                <RefreshCw className="w-3 h-3" /> Clear
              </button>
            </div>

            <div className="flex-1 p-4 overflow-y-auto space-y-3">
              {simMessages.length === 0 && (
                <p className="text-xs text-center text-[#68756F] mt-10">
                  Type a message to test the AI
                </p>
              )}
              {simMessages.map((msg, i) => (
                <div
                  key={i}
                  className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-md p-3 rounded-xl text-xs ${
                      msg.sender === 'user'
                        ? 'bg-[#10231C] text-white rounded-br-none'
                        : 'bg-[#F7F6F1] border border-[#E2E4DF] text-[#14201B] rounded-bl-none'
                    }`}
                  >
                    <p>{msg.text}</p>
                    {msg.intent && (
                      <div className="mt-2 pt-1.5 border-t border-[#E2E4DF] text-[10px] text-[#287A59]">
                        Intent: <b>{msg.intent}</b> · {msg.latency}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {isSimTyping && (
                <div className="flex items-center gap-1.5 text-xs text-[#68756F]">
                  <Sparkles className="w-3.5 h-3.5 text-[#287A59] animate-spin" />
                  Thinking...
                </div>
              )}
            </div>

            <form
              onSubmit={handleSimSend}
              className="p-3 border-t border-[#E2E4DF] flex items-center gap-2"
            >
              <input
                type="text"
                placeholder="Type a test question..."
                value={simInput}
                onChange={(e) => setSimInput(e.target.value)}
                className="flex-1 p-2.5 text-xs rounded-xl border border-[#E2E4DF] bg-[#F7F6F1] focus:bg-white focus:outline-none"
              />
              <button
                type="submit"
                disabled={!simInput.trim() || isSimTyping}
                className="px-4 py-2.5 rounded-xl bg-[#287A59] text-white text-xs font-bold disabled:opacity-50 flex items-center gap-1"
              >
                Send <Send className="w-3.5 h-3.5" />
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default AiAgentPage;
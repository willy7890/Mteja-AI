import React, { useEffect, useState } from "react";
import { ArrowRight, MessageSquare, Instagram, Video, Mail, CheckCircle } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

// 1. DATA LAYOUT FOR CHANNELS
const CHANNELS = [
  {
    id: "whatsapp",
    name: "WhatsApp",
    color: "#008069",
    activeBg: "#efeae2",
    accent: "bg-[#d9fdd3]",
    icon: MessageSquare,
    tagline: "Instant Messaging AI",
    chats: [
      { id: 1, sender: "customer", text: "Hi! Do you have the classic leather boots size 9 in stock?", time: "10:02 AM" },
      { id: 2, sender: "ai", text: "Checking our live vault... Yes! We have 2 pairs left at our downtown branch. Should I hold them for you?", time: "10:02 AM" },
      { id: 3, sender: "customer", text: "Awesome! Yes please.", time: "10:03 AM" },
    ]
  },
  {
    id: "instagram",
    name: "Instagram",
    color: "#E1306C",
    activeBg: "#ffffff",
    accent: "bg-[#3797EF] text-white",
    icon: Instagram,
    tagline: "Social DM Automator",
    chats: [
      { id: 1, sender: "customer", text: "Hey! Loved your story post. How much is the summer dress?", time: "2:14 PM" },
      { id: 2, sender: "ai", text: "Thanks for reaching out! It is currently $45, and I can auto-apply a 10% discount link right here if you'd like!", time: "2:14 PM" },
      { id: 3, sender: "customer", text: "Send the link! Buying it now.", time: "2:15 PM" },
    ]
  },
  {
    id: "tiktok",
    name: "TikTok",
    color: "#FE2C55",
    activeBg: "#121212",
    accent: "bg-[#25F4EE] text-black",
    icon: Video,
    tagline: "Comment & Lead Trapper",
    chats: [
      { id: 1, sender: "customer", text: "Where can I register for the masterclass showing on your video?", time: "Just now" },
      { id: 2, sender: "ai", text: "Hey there! Tap right here to instantly grab your free seat: mteja.ai/class. Registration closes in 1 hour!", time: "Just now" },
      { id: 3, sender: "customer", text: "Got it, signed up! Thanks for the fast reply 🙌", time: "Just now" },
    ]
  },
  {
    id: "email",
    name: "Email",
    color: "#1A73E8",
    activeBg: "#F1F3F4",
    accent: "bg-white border border-slate-200",
    icon: Mail,
    tagline: "24/7 Desk Ticketing",
    chats: [
      { id: 1, sender: "customer", text: "Subject: Requesting a refund for order #4019. The sizing is incorrect.", time: "Yesterday" },
      { id: 2, sender: "ai", text: "Hello! I have generated your prepaid return shipping label and updated your account portal. Your refund will process as soon as scanned by the courier.", time: "1 min ago" },
      { id: 3, sender: "customer", text: "Wow, that was fast. Thank you for resolving this so cleanly.", time: "Just now" },
    ]
  }
];

export default function App() {
  const [activeTab, setActiveTab] = useState("whatsapp");
  const [visibleMessages, setVisibleMessages] = useState(1);

  const currentChannel = CHANNELS.find((c) => c.id === activeTab) || CHANNELS[0];

  // Message loop timing logic
  useEffect(() => {
    setVisibleMessages(1);
    const interval = setInterval(() => {
      setVisibleMessages((prev) => {
        if (prev < currentChannel.chats.length) return prev + 1;
        return 1; // Restart chat sequence
      });
    }, 2500);

    return () => clearInterval(interval);
  }, [activeTab]);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans antialiased overflow-x-hidden">
      
      {/* 2. NAVIGATION BAR */}
      <header className="sticky top-0 z-50 border-b border-slate-200 bg-white/80 backdrop-blur-md px-6 py-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-emerald-600 rounded-lg flex items-center justify-center text-white font-black">M</div>
            <span className="text-xl font-bold tracking-tight text-slate-900">MtejaAI</span>
          </div>
          <button className="bg-slate-900 text-white text-sm font-semibold py-2.5 px-5 rounded-xl hover:bg-slate-800 transition-all shadow-sm">
            Start free
          </button>
        </div>
      </header>

      {/* 3. HERO CONTENT WRAPPER WITH SCROLL-IN ANIMATION EFFECT */}
      <motion.main 
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="max-w-7xl mx-auto px-6 py-20 grid grid-cols-1 lg:grid-cols-2 gap-16 items-center"
      >
        
        {/* LEFT MARKETING TEXT BLOCK */}
        <div className="flex flex-col gap-6">
          <span className="px-3 py-1 text-xs font-semibold text-emerald-700 bg-emerald-50 rounded-full w-max flex items-center gap-1.5 border border-emerald-200">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            Omnichannel Business Hub
          </span>
          <h1 className="text-5xl lg:text-6xl font-black tracking-tight text-slate-900 leading-tight">
            Every customer deserves an <span className="text-emerald-600">instant reply.</span>
          </h1>
          <p className="text-lg text-slate-600 leading-relaxed max-w-lg">
            MtejaAI automatically deploys intelligent autonomous agent squads across your customer touchpoints. Catch leads, close deals, and handle support flows instantly.
          </p>

          {/* DYNAMIC CARD TOGGLE CONTROLS */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-4">
            {CHANNELS.map((chan) => {
              const Icon = chan.icon;
              const isActive = chan.id === activeTab;
              return (
                <button
                  key={chan.id}
                  onClick={() => setActiveTab(chan.id)}
                  className={`flex flex-col items-center gap-2 p-3 rounded-xl border text-center font-medium transition-all ${
                    isActive 
                      ? "border-slate-900 bg-white shadow-md scale-105" 
                      : "border-slate-200 bg-slate-50 text-slate-500 hover:bg-white hover:text-slate-900"
                  }`}
                >
                  <Icon size={20} style={{ color: isActive ? chan.color : "currentColor" }} />
                  <span className="text-xs">{chan.name}</span>
                </button>
              );
            })}
          </div>

          <div className="flex items-center gap-4 mt-4">
            <button className="bg-slate-900 hover:bg-slate-800 text-white font-medium py-3.5 px-7 rounded-xl transition-all flex items-center gap-2 shadow-md hover:shadow-lg">
              Explore workspace <ArrowRight size={16} />
            </button>
          </div>
        </div>

        {/* RIGHT MULTI-THEMED DEMO WIDGET CANVAS */}
        <div className="flex items-center justify-center p-2 relative">
          
          {/* Decorative ambient background blur glowing based on selected platform color */}
          <div 
            className="absolute -inset-4 rounded-3xl opacity-10 blur-2xl transition-all duration-700" 
            style={{ backgroundColor: currentChannel.color }} 
          />

          <AnimatePresence mode="wait">
            <motion.div
              key={currentChannel.id}
              initial={{ opacity: 0, scale: 0.95, y: 15 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: -15 }}
              transition={{ duration: 0.35 }}
              className="w-full max-w-md bg-white border border-slate-200/80 rounded-2xl shadow-2xl overflow-hidden relative z-10"
            >
              {/* Dynamic Header Box matching current active platform */}
              <div 
                className="text-white p-4 flex items-center justify-between transition-colors duration-500"
                style={{ backgroundColor: currentChannel.color }}
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center font-bold shadow-inner">
                    <currentChannel.icon size={20} />
                  </div>
                  <div>
                    <h3 className="font-bold text-sm m-0 p-0 text-white leading-tight">MtejaAI Bot</h3>
                    <p className="text-xs text-white/80 m-0 p-0">{currentChannel.tagline}</p>
                  </div>
                </div>
                <span className="text-[10px] bg-white/20 px-2 py-0.5 rounded-full font-medium tracking-wide">
                  ACTIVE
                </span>
              </div>

              {/* Dynamic Streaming Message Canvas Surface Area */}
              <div 
                className="p-4 h-[350px] overflow-y-auto flex flex-col gap-3 transition-colors duration-500"
                style={{ 
                  backgroundColor: currentChannel.activeBg,
                  backgroundImage: currentChannel.id === "whatsapp" ? "url('https://githubusercontent.com')" : "none",
                  backgroundRepeat: "repeat"
                }}
              >
                {currentChannel.chats.slice(0, visibleMessages).map((msg, idx) => {
                  const isCustomer = msg.sender === "customer";
                  
                  // Text handling for dark/light themes inside standard or dark configurations
                  const isDarkTheme = currentChannel.id === "tiktok";
                  const textContrastColor = isDarkTheme && isCustomer ? "text-slate-300" : "text-slate-800";

                  return (
                    <motion.div
                      key={msg.id}
                      initial={{ opacity: 0, y: 10, scale: 0.98 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      transition={{ duration: 0.25 }}

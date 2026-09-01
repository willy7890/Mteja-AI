import { useState } from 'react';
import Navbar from './component/Navbar';
import Hero from './component/Hero';

const themes = {
  light: {
    bg: '#F3F1EA',
    text: '#14201A',
    muted: '#5B6B62',
    card: '#FFFFFF',
    accent: '#2F6F4E',
    accentText: '#FFFFFF',
    border: 'rgba(20,32,26,0.10)',
    bubbleAi: '#EEF2ED',
  },
  dark: {
    bgGradient: 'linear-gradient(to bottom, #0B1220 0%, #0F2A3D 55%, #123A3A 100%)',
    text: '#F2F0E8',
    muted: '#93A3AC',
    card: '#141E2B',
    accent: '#4FD1C5',
    accentText: '#0B1220',
    border: 'rgba(242,240,232,0.12)',
    bubbleAi: '#1B2836',
  },
};

function App() {
  const [dark, setDark] = useState(false);
  const t = dark ? themes.dark : themes.light;

  return (
    <div
      className="min-h-screen transition-colors duration-300"
      style={{ background: dark ? t.bgGradient : t.bg }}
    >
      <Navbar t={t} dark={dark} setDark={setDark} />
      <Hero t={t} />
    </div>
  );
}

export default App;
import { useState } from 'react';
import Navbar from './component/Navbar';
import Hero from './component/Hero';

// Builds a repeating doodle-pattern tile as an inline SVG.
// `color` controls the stroke color of the icons so it matches each theme.
function doodlePattern(color) {
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="180" height="180">
      <g fill="none" stroke="${color}" stroke-width="1.4">
        <path d="M20 25 h30 a6 6 0 0 1 6 6 v14 a6 6 0 0 1 -6 6 h-18 l-8 8 v-8 h-4 a6 6 0 0 1 -6 -6 v-14 a6 6 0 0 1 6 -6 z" />
        <path d="M120 20 l3 7 7 1 -5 5 1 7 -6 -3 -6 3 1 -7 -5 -5 7 -1 z" />
        <path d="M40 110 c0 -8 6 -14 14 -14 4 -8 12 -13 20 -13 10 0 18 7 20 16 7 1 12 6 12 13 0 8 -6 14 -14 14 h-38 c-8 0 -14 -6 -14 -16 z" />
        <path d="M140 90 l4 8 8 4 -8 4 -4 8 -4 -8 -8 -4 8 -4 z" />
        <path d="M25 150 l6 6 12 -14" />
        <circle cx="150" cy="150" r="8" />
        <path d="M95 55 l3 7 7 1 -5 5 1 7 -6 -3 -6 3 1 -7 -5 -5 7 -1 z" opacity="0.6" />
      </g>
    </svg>
  `;
  return `url("data:image/svg+xml,${encodeURIComponent(svg)}")`;
}

const themes = {
  light: {
    bg: '#F3F1EA',
    bgPattern: doodlePattern('rgba(20,32,26,0.14)'),
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
    bgPattern: doodlePattern('rgba(79,209,197,0.16)'),
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
      style={{
        background: dark ? t.bgGradient : t.bg,
        backgroundImage: dark
          ? `${t.bgPattern}, ${t.bgGradient}`
          : `${t.bgPattern}`,
        backgroundSize: '180px 180px, cover',
        backgroundRepeat: 'repeat, no-repeat',
      }}
    >
      <Navbar t={t} dark={dark} setDark={setDark} />
      <Hero t={t} />
    </div>
  );
}

export default App;
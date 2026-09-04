import { useState, useMemo } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import PublicLayout from './component/PublicLayout';
import DashboardLayout from './component/DashboardLayout';
import LandingPage from './Pages/LandingPage';
import LoginPage from './Pages/LoginPage';
import TermsOfService from './Pages/TermsOfService';
import PrivacyPolicy from './Pages/PrivacyPolicy';
import DashboardPage from './Pages/DashboardPage';
import ComingSoon from './component/ComingSoon';

const iconTemplates = [
  `<path d="M-15 -10 h30 a6 6 0 0 1 6 6 v14 a6 6 0 0 1 -6 6 h-18 l-8 8 v-8 h-4 a6 6 0 0 1 -6 -6 v-14 a6 6 0 0 1 6 -6 z" />`,
  `<path d="M0 -10 l3 7 7 1 -5 5 1 7 -6 -3 -6 3 1 -7 -5 -5 7 -1 z" />`,
  `<path d="M-10 8 c0 -8 6 -14 14 -14 4 -8 12 -13 20 -13 10 0 18 7 20 16 7 1 12 6 12 13 0 8 -6 14 -14 14 h-38 c-8 0 -14 -6 -14 -16 z" scale="0.4" />`,
  `<path d="M0 -8 l4 8 8 4 -8 4 -4 8 -4 -8 -8 -4 8 -4 z" />`,
  `<path d="M-8 0 l6 6 12 -14" />`,
  `<circle cx="0" cy="0" r="6" />`,
];

function generateDoodleTile(color, size = 500, count = 26) {
  let shapes = '';
  for (let i = 0; i < count; i++) {
    const x = Math.random() * size;
    const y = Math.random() * size;
    const rot = Math.random() * 360;
    const scale = 0.6 + Math.random() * 0.7;
    const icon = iconTemplates[Math.floor(Math.random() * iconTemplates.length)];
    shapes += `<g transform="translate(${x.toFixed(1)},${y.toFixed(1)}) rotate(${rot.toFixed(
      0
    )}) scale(${scale.toFixed(2)})">${icon}</g>`;
  }
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}"><g fill="none" stroke="${color}" stroke-width="1.4">${shapes}</g></svg>`;
  return `url("data:image/svg+xml,${encodeURIComponent(svg)}")`;
}

function App() {
  const [dark, setDark] = useState(false);

  const lightPattern = useMemo(() => generateDoodleTile('rgba(20,32,26,0.14)'), []);
  const darkPattern = useMemo(() => generateDoodleTile('rgba(79,209,197,0.16)'), []);

  const themes = {
    light: {
      bg: '#F3F1EA',
      bgPattern: lightPattern,
      text: '#14201A',
      muted: '#5B6B62',
      card: '#FFFFFF',
      accent: '#2F6F4E',
      accentText: '#FFFFFF',
      border: 'rgba(20,32,26,0.10)',
      bubbleAi: '#EEF2ED',
      sectionTint: 'rgba(20,32,26,0.03)',
      surface: 'rgba(20,32,26,0.035)',
    },
    dark: {
      bg: '#0B1220',
      bgGradient: 'linear-gradient(to bottom, #0B1220 0%, #0F2A3D 55%, #123A3A 100%)',
      bgPattern: darkPattern,
      text: '#F2F0E8',
      muted: '#93A3AC',
      card: '#141E2B',
      accent: '#4FD1C5',
      accentText: '#0B1220',
      border: 'rgba(242,240,232,0.12)',
      bubbleAi: '#1B2836',
      sectionTint: 'rgba(79,209,197,0.05)',
      surface: 'rgba(242,240,232,0.04)',
    },
  };

  const t = dark ? themes.dark : themes.light;

  return (
    <BrowserRouter>
      <Routes>
        {/* Public marketing site — Navbar/Footer live inside PublicLayout,
            not here, so they never leak into the dashboard section. */}
        <Route element={<PublicLayout t={t} dark={dark} setDark={setDark} />}>
          <Route path="/" element={<LandingPage t={t} />} />
          <Route path="/login" element={<LoginPage t={t} />} />
          <Route path="/terms" element={<TermsOfService t={t} />} />
          <Route path="/privacy" element={<PrivacyPolicy t={t} />} />
        </Route>

        {/* Authenticated app — its own chrome (Sidebar/TopHeader) via
            DashboardLayout, completely separate from the site above. */}
        <Route path="/dashboard" element={<DashboardLayout t={t} />}>
          <Route index element={<DashboardPage t={t} />} />
          <Route path="inbox" element={<ComingSoon t={t} title="Inbox" />} />
          <Route path="customers" element={<ComingSoon t={t} title="Customers" />} />
          <Route path="ai-agent" element={<ComingSoon t={t} title="AI Agent" />} />
          <Route path="automations" element={<ComingSoon t={t} title="Automations" />} />
          <Route path="analytics" element={<ComingSoon t={t} title="Analytics" />} />
          <Route path="channels" element={<ComingSoon t={t} title="Channels" />} />
          <Route path="team" element={<ComingSoon t={t} title="Team" />} />
          <Route path="billing" element={<ComingSoon t={t} title="Billing" />} />
          <Route path="settings" element={<ComingSoon t={t} title="Settings" />} />
          <Route path="notifications" element={<ComingSoon t={t} title="Notifications" />} />
          <Route path="profile" element={<ComingSoon t={t} title="Profile" />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
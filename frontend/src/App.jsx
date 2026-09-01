import { useState } from 'react';
import Navbar from './component/Navbar';
import Hero from './component/Hero';

const themes = {
  light: { bg: '#F3F1EA', text: '#14201A', accent: '#2F6F4E' },
  dark: { bg: '#101713', text: '#F2F0E8', accent: '#7FD9A4' },
};

function App() {
  const [dark, setDark] = useState(false);
  const t = dark ? themes.dark : themes.light;

  return (
    <div style={{ background: t.bg }}>
      <Navbar t={t} dark={dark} setDark={setDark} />
      <Hero t={t} />
    </div>
  );
}

export default App;
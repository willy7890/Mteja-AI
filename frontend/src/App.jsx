import { useState, useMemo } from 'react';
import Navbar from './component/Navbar';
import Hero from './component/Hero';
import TrustBar from './component/TrustBar';
import ProblemSection from './component/ProblemSection';
import Testimonial from './component/Testimonial';
import Footer from './component/Footer';

// Small doodle shapes used to create the subtle background pattern.
const iconTemplates = [
  `<path d="M-15 -10 h30 a6 6 0 0 1 6 6 v10 a6 6 0 0 1 -6 6 h-18 l-8 8 v-8 h-4 a6 6 0 0 1 -6 -6 v-10 a6 6 0 0 1 6 -6 z" />`,
  `<path d="M0 -10 l3 7 7 1 -5 5 1 7 -6 -3 -6 3 1 -7 -5 -5 7 -1 z" />`,
  `<path d="M-10 8 c0 -8 6 -14 14 -14 4 -8 12 -13 20 -13 10 0 18 7 20 16 7 1 12 6 12 13 0 8 -6 14 -14 14 h-38 c-8 0 -14 -6 -14 -16 z" scale="0.4" />`,
  `<path d="M0 -8 l4 8 8 4 -8 4 -4 8 -4 -8 -8 -4 8 -4 z" />`,
  `<path d="M-8 0 l6 6 12 -14" />`,
  `<circle cx="0" cy="0" r="6" />`,
];

// Builds one randomized SVG doodle tile.
function generateDoodleTile(color, size = 500, count = 26) {
  let shapes = '';

  for (let i = 0; i < count; i++) {
    const x = Math.random() * size;
    const y = Math.random() * size;
    const rot = Math.random() * 360;
    const scale = 0.6 + Math.random() * 0.7;

    const icon =
      iconTemplates[Math.floor(Math.random() * iconTemplates.length)];

    shapes += `
      <g
        transform="translate(${x.toFixed(1)},${y.toFixed(
          1
        )}) rotate(${rot.toFixed(0)}) scale(${scale.toFixed(2)})"
      >
        ${icon}
      </g>
    `;
  }

  const svg = `
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="${size}"
      height="${size}"
    >
      <g fill="none" stroke="${color}" stroke-width="1.4">
        ${shapes}
      </g>
    </svg>
  `;

  return `url("data:image/svg+xml,${encodeURIComponent(svg)}")`;
}

function App() {
  const [dark, setDark] = useState(false);

  // Generate the background patterns only once.
  const lightPattern = useMemo(
    () => generateDoodleTile('rgba(20,32,26,0.11)'),
    []
  );

  const darkPattern = useMemo(
    () => generateDoodleTile('rgba(79,209,197,0.10)'),
    []
  );

  const themes = {
    light: {
      bg: '#F3F1EA',
      bgPattern: lightPattern,

      // Used for section differentiation.
      section: '#F3F1EA',
      sectionAlt: '#ECEAE1',
      sectionSoft: '#F8F7F2',

      text: '#14201A',
      muted: '#5B6B62',
      card: '#FFFFFF',
      accent: '#2F6F4E',
      accentText: '#FFFFFF',
      border: 'rgba(20,32,26,0.10)',
      bubbleAi: '#EEF2ED',
    },

    dark: {
      bg: '#0B1220',
      bgGradient:
        'linear-gradient(to bottom, #0B1220 0%, #0F2A3D 55%, #123A3A 100%)',
      bgPattern: darkPattern,

      // Used for section differentiation.
      section: '#0B1220',
      sectionAlt: '#0D1A29',
      sectionSoft: '#102431',

      text: '#F2F0E8',
      muted: '#93A3AC',
      card: '#141E2B',
      accent: '#4FD1C5',
      accentText: '#0B1220',
      border: 'rgba(242,240,232,0.12)',
      bubbleAi: '#1B2836',
    },
  };

  const t = dark ? themes.dark : themes.light;

  return (
    <div
      className="min-h-screen transition-colors duration-500"
      style={{
        background: dark ? t.bgGradient : t.bg,
        color: t.text,
      }}
    >
      {/* 
        Global background layer.

        The doodles stay behind the content, but we reduce their visual
        dominance so the page feels more premium and less like wallpaper.
      */}
      <div
        aria-hidden="true"
        className="pointer-events-none fixed inset-0 -z-0 transition-opacity duration-500"
        style={{
          backgroundImage: t.bgPattern,
          backgroundSize: '500px 500px',
          backgroundRepeat: 'repeat',
          opacity: dark ? 0.45 : 0.55,
        }}
      />

      {/* Actual page content */}
      <div className="relative z-10">
        <Navbar t={t} dark={dark} setDark={setDark} />

        {/* HERO */}
        <main>
          <section
            style={{
              background: dark
                ? 'linear-gradient(to bottom, rgba(11,18,32,0.70), rgba(11,18,32,0.38))'
                : 'rgba(243,241,234,0.72)',
            }}
          >
            <Hero t={t} />
          </section>

          {/* TRUST BAR */}
          <section
            style={{
              background: dark
                ? 'rgba(11,18,32,0.58)'
                : 'rgba(248,247,242,0.72)',
              borderTop: `1px solid ${t.border}`,
              borderBottom: `1px solid ${t.border}`,
            }}
          >
            <TrustBar t={t} />
          </section>

          {/* PROBLEM SECTION */}
          <section
            style={{
              background: t.sectionAlt,
            }}
          >
            <ProblemSection t={t} />
          </section>

          {/* TESTIMONIALS */}
          <section
            style={{
              background: t.section,
            }}
          >
            <Testimonial t={t} />
          </section>
        </main>

        {/* FOOTER */}
        <footer
          style={{
            background: dark
              ? 'linear-gradient(to bottom, #102431, #0B1220)'
              : t.sectionAlt,
            borderTop: `1px solid ${t.border}`,
          }}
        >
          <Footer t={t} />
        </footer>
      </div>
    </div>
  );
}

export default App;
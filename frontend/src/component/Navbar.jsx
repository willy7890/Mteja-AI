import { useState } from 'react';
import { Menu, X } from 'lucide-react';
import ThemeToggle from './ThemeToggle';

function Navbar({ t, dark, setDark }) {
  const [isOpen, setIsOpen] = useState(false);

  const Navlinks = [
    { name: 'Home', href: '#HomePage' },
    { name: 'About', href: '#AboutPage' },
    { name: 'Login', href: '#LoginPage' },
    { name: 'Request Demo', href: '#DemoPage' },
  ];

  return (
    <nav
      className="fixed top-0 w-full z-50 backdrop-blur-md border-b"
      style={{ background: t.bg, borderColor: `${t.text}1A` }}
    >
      <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
        <span className="text-lg font-semibold" style={{ color: t.text }}>
          Mteja<span style={{ color: t.accent }}>AI</span>
        </span>

        <div className="hidden md:flex items-center gap-8 text-sm" style={{ color: t.text }}>
          {Navlinks.map((link) => (
            <a key={link.name} href={link.href} className="hover:opacity-70 transition-opacity">
              {link.name}
            </a>
          ))}
          <ThemeToggle dark={dark} setDark={setDark} />
        </div>

        <button
          className="md:hidden"
          style={{ color: t.text }}
          onClick={() => setIsOpen((o) => !o)}
          aria-label="Toggle menu"
        >
          {isOpen ? <X size={22} /> : <Menu size={22} />}
        </button>
      </div>

      {isOpen && (
        <div
          className="md:hidden px-6 pb-5 flex flex-col gap-4 text-sm"
          style={{ background: t.bg, color: t.text }}
        >
          {Navlinks.map((link) => (
            <a key={link.name} href={link.href} onClick={() => setIsOpen(false)}>
              {link.name}
            </a>
          ))}
        </div>
      )}
    </nav>
  );
}

export default Navbar;
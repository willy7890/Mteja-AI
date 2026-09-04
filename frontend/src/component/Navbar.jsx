import { useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import { Menu, X } from 'lucide-react';
import ThemeToggle from './ThemeToggle';

function NavPill({ href, children, t, dark, onClick }) {
  const ref = useRef(null);
  const [isHover, setIsHover] = useState(false);

  const glow = dark
    ? 'radial-gradient(90px circle at var(--x) var(--y), rgba(255,93,162,0.35), transparent 70%)'
    : 'radial-gradient(90px circle at var(--x) var(--y), rgba(225,48,108,0.18), transparent 70%)';

  function handleMouseMove(e) {
    const rect = ref.current.getBoundingClientRect();
    ref.current.style.setProperty('--x', `${e.clientX - rect.left}px`);
    ref.current.style.setProperty('--y', `${e.clientY - rect.top}px`);
  }

  const sharedProps = {
    ref,
    onMouseMove: handleMouseMove,
    onMouseEnter: () => setIsHover(true),
    onMouseLeave: () => setIsHover(false),
    onClick,
    className: 'px-4 py-1.5 rounded-full text-sm transition-colors duration-150',
    style: {
      border: `1px solid ${t.border}`,
      color: t.text,
      backgroundImage: isHover ? glow : 'none',
      '--x': '50%',
      '--y': '50%',
    },
  };

 
  if (href.startsWith('/')) {
    return (
      <Link to={href} {...sharedProps}>
        {children}
      </Link>
    );
  }

  return (
    <a href={href} {...sharedProps}>
      {children}
    </a>
  );
}

function Navbar({ t, dark, setDark }) {
  const [isOpen, setIsOpen] = useState(false);
  const ctaRef = useRef(null);

  const Navlinks = [
    { name: 'Home', href: '#HomePage' },
    { name: 'About', href: '#AboutPage' },
  
    { name: 'Login', href: '/Login' },
    { name: 'Request Demo', href: '#DemoPage' },
  ];

  const ctaGradient = dark
    ? 'radial-gradient(160px circle at var(--x) var(--y), #ff5da2, #4FD1C5)'
    : 'radial-gradient(160px circle at var(--x) var(--y), #e1306c, #c13584)';

  function handleCtaMove(e) {
    const rect = ctaRef.current.getBoundingClientRect();
    ctaRef.current.style.setProperty('--x', `${e.clientX - rect.left}px`);
    ctaRef.current.style.setProperty('--y', `${e.clientY - rect.top}px`);
  }

  return (
    <nav
      className="fixed top-0 w-full z-50 backdrop-blur-md border-b"
      style={{ background: t.bg, borderColor: t.border }}
    >
      <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
        <span className="text-lg font-semibold" style={{ color: t.text }}>
          Mteja<span style={{ color: t.accent }}>AI</span>
        </span>

        <div className="hidden md:flex items-center gap-3 text-sm">
          {Navlinks.map((link) => (
            <NavPill key={link.name} href={link.href} t={t} dark={dark}>
              {link.name}
            </NavPill>
          ))}

          <ThemeToggle t={t} dark={dark} setDark={setDark} />

          <button
            ref={ctaRef}
            onMouseMove={handleCtaMove}
            className="px-5 py-2 rounded-full font-medium text-white transition-[background] duration-150"
            style={{ background: ctaGradient, '--x': '50%', '--y': '50%' }}
          >
            Get started
          </button>
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
          className="md:hidden px-6 pb-5 flex flex-col gap-3 text-sm"
          style={{ background: t.bg, color: t.text }}
        >
          {Navlinks.map((link) => (
            <NavPill key={link.name} href={link.href} t={t} dark={dark} onClick={() => setIsOpen(false)}>
              {link.name}
            </NavPill>
          ))}
        </div>
      )}
    </nav>
  );
}

export default Navbar;
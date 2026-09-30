import { useState, useRef, useEffect } from 'react';
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
    className: 'min-h-11 inline-flex items-center px-4 py-1.5 rounded-full text-sm transition-colors duration-150',
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

  useEffect(() => {
    document.body.style.overflow = isOpen ? 'hidden' : '';
    return () => { document.body.style.overflow = ''; };
  }, [isOpen]);

  const Navlinks = [
    { name: 'Home', href: '/' },
    { name: 'About', href: '/#AboutPage' },
    // THIS was the actual bug — still '#LoginPage', never updated to a
    // real route, so NavPill (even once fixed above) had nothing to
    // detect as "this is a real path."
    { name: 'Login', href: '/login' },
    { name: 'Free trial', href: '/signup' },
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
      style={{ background: t.bg, borderColor: t.border, paddingTop: 'env(safe-area-inset-top)' }}
    >
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-3 sm:py-4 flex justify-between items-center min-h-14 sm:min-h-16">
        <Link to="/" onClick={() => setIsOpen(false)} className="text-lg font-semibold" style={{ color: t.text }}>
          Mteja<span style={{ color: t.accent }}>AI</span>
        </Link>

        <div className="hidden md:flex items-center gap-3 text-sm">
          {Navlinks.map((link) => (
            <NavPill key={link.name} href={link.href} t={t} dark={dark}>
              {link.name}
            </NavPill>
          ))}

          <ThemeToggle t={t} dark={dark} setDark={setDark} />

          <Link
            ref={ctaRef}
            to="/signup"
            onMouseMove={handleCtaMove}
            className="min-h-11 px-5 py-2 rounded-full font-medium text-white transition-[background] duration-150"
            style={{ background: ctaGradient, '--x': '50%', '--y': '50%' }}
          >
            Get started
          </Link>
        </div>

        <button
          className="md:hidden min-h-11 min-w-11 inline-flex items-center justify-center rounded-lg focus-visible:outline focus-visible:outline-2"
          style={{ color: t.text }}
          onClick={() => setIsOpen((o) => !o)}
          aria-label={isOpen ? 'Close navigation menu' : 'Open navigation menu'}
          aria-expanded={isOpen}
          aria-controls="mobile-navigation"
        >
          {isOpen ? <X size={22} /> : <Menu size={22} />}
        </button>
      </div>

      <div
        id="mobile-navigation"
        aria-hidden={!isOpen}
        inert={!isOpen}
        className={`md:hidden overflow-hidden transition-[max-height,opacity] duration-200 ${isOpen ? 'max-h-[80dvh] opacity-100' : 'max-h-0 opacity-0 pointer-events-none'}`}
        style={{ background: t.bg, color: t.text }}
      >
        <div className="px-4 sm:px-6 pb-5 flex flex-col gap-2 text-sm">
          {Navlinks.map((link) => (
            <NavPill key={link.name} href={link.href} t={t} dark={dark} onClick={() => setIsOpen(false)}>
              {link.name}
            </NavPill>
          ))}
          <Link to="/signup" onClick={() => setIsOpen(false)} className="min-h-11 inline-flex items-center justify-center rounded-full font-medium"
            style={{ background: t.accent, color: t.accentText }}>Get started</Link>
          <div className="flex items-center justify-between pt-2 border-t" style={{ borderColor: t.border }}>
            <span style={{ color: t.text }}>Theme</span>
            <ThemeToggle t={t} dark={dark} setDark={setDark} />
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
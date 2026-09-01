import { useState } from 'react';
import { Menu, X } from 'lucide-react';
import ThemeToggle from './ThemeToggle';

function Navbar() {
  const [isOpen, setIsOpen] = useState(false);

  const Navlinks = [
    { name: 'Home', href: '#HomePage' },
    { name: 'About', href: '#AboutPage' },
    { name: 'Login', href: '#LoginPage' },
    { name: 'Request Demo', href: '#DemoPage' },
  ];

  return (
    <nav className="fixed top-0 w-full z-50 bg-[#F6F4EE]/85 backdrop-blur-md border-b border-[#1C2B22]/10">
      <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
        <span className="text-lg font-semibold text-[#1C2B22]">
          Mteja<span className="text-[#2F6F4E]">AI</span>
        </span>

        <div className="hidden md:flex items-center gap-8 text-sm text-[#1C2B22]/70">
          {Navlinks.map((link) => (
            <a key={link.name} href={link.href} className="hover:text-[#1C2B22] transition-colors">
              {link.name}
            </a>
          ))}
          <ThemeToggle />
        </div>

        <button
          className="md:hidden text-[#1C2B22]"
          onClick={() => setIsOpen((o) => !o)}
          aria-label="Toggle menu"
        >
          {isOpen ? <X size={22} /> : <Menu size={22} />}
        </button>
      </div>

      {isOpen && (
        <div className="md:hidden px-6 pb-5 flex flex-col gap-4 text-sm text-[#1C2B22]/80 bg-[#F6F4EE] border-t border-[#1C2B22]/10">
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
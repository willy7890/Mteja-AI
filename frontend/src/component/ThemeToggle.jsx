import { Sun, Moon } from 'lucide-react';

function ThemeToggle({ dark, setDark }) {
  return (
    <button
      type="button"
      onClick={() => setDark(!dark)}
      aria-label="Toggle theme"
      title={dark ? 'Switch to light theme' : 'Switch to dark theme'}
      className="w-9 h-9 rounded-full flex items-center justify-center border transition-colors"
      style={{ color: dark ? '#F2F0E8' : '#14201A', borderColor: dark ? 'rgba(242,240,232,0.2)' : 'rgba(20,32,26,0.15)' }}
    >
      {dark ? <Sun size={16} /> : <Moon size={16} />}
    </button>
  );
}

export default ThemeToggle;
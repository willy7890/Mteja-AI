import { Sun, Moon } from 'lucide-react';

function ThemeToggle({ dark, setDark }) {
  return (
    <button
      onClick={() => setDark(!dark)}
      aria-label="Toggle theme"
      className="w-9 h-9 rounded-full flex items-center justify-center border border-black/10"
    >
      {dark ? <Sun size={16} /> : <Moon size={16} />}
    </button>
  );
}

export default ThemeToggle;
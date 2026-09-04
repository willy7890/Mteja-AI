import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Eye, EyeOff, Mail, Lock, Loader2 } from 'lucide-react';


function isValidEmail(value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

function LoginPage({ t }) {
  const [showPassword, setShowPassword] = useState(false);
  const [focused, setFocused] = useState(null);

  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const inputStyle = (fieldName, hasError) => ({
    background: t.bg,
    border: `1.5px solid ${
      hasError ? '#E5484D' : focused === fieldName ? t.accent : t.border
    }`,
    color: t.text,
  });

  function validate() {
    const next = {};
    if (!email.trim()) next.email = 'Email is required.';
    else if (!isValidEmail(email)) next.email = 'Enter a valid email address.';

    if (!password) next.password = 'Password is required.';
    else if (password.length < 6) next.password = 'Password must be at least 6 characters.';

    return next;
  }

  function handleSubmit(e) {
    e.preventDefault();
    const foundErrors = validate();
    setErrors(foundErrors);
    if (Object.keys(foundErrors).length > 0) return;

    setIsSubmitting(true);
    setSubmitted(false);

    // ── INTEGRATION POINT ──────────────────────────────────────────────
    // This is where the real API call goes once the integration branch
    // is ready. Replace this setTimeout block with something like:
    //
    //   const res = await fetch('https://your-api.com/login', {
    //     method: 'POST',
    //     headers: { 'Content-Type': 'application/json' },
    //     body: JSON.stringify({ email, password }),
    //   });
    //   const data = await res.json();
    //   // store data.token, redirect to dashboard, handle failure, etc.
    //
    // The setTimeout below just fakes a network delay so the loading
    // state is visible and testable right now, before that code exists.
    setTimeout(() => {
      setIsSubmitting(false);
      setSubmitted(true);
      console.log('Login form submitted (no backend wired yet):', { email, password });
    }, 1200);
  }

  return (
    <div className="min-h-screen pt-20 grid lg:grid-cols-2">
      <div
        className="hidden lg:flex flex-col justify-between p-12 relative overflow-hidden"
        style={{ background: t.accent }}
      >
        <div
          className="absolute -bottom-32 -left-20 w-96 h-96 rounded-full"
          style={{ background: t.accentText, opacity: 0.06 }}
        />
        <div
          className="absolute -top-24 -right-16 w-72 h-72 rounded-full"
          style={{ background: t.accentText, opacity: 0.08 }}
        />

        <span className="text-xl font-semibold relative" style={{ color: t.accentText }}>
          MtejaAI
        </span>

        <div className="relative">
          <h2
            className="text-3xl font-semibold tracking-tight leading-tight mb-4"
            style={{ color: t.accentText }}
          >
            Every customer message, answered before they look elsewhere.
          </h2>
          <p className="text-sm opacity-80" style={{ color: t.accentText }}>
            Log in to see your unified inbox across WhatsApp, Instagram, email, and calls.
          </p>
        </div>

        <div className="relative rounded-2xl p-5" style={{ background: `${t.accentText}14` }}>
          <p className="text-sm leading-relaxed" style={{ color: t.accentText }}>
            "I stopped losing customers to slow replies. MtejaAI answers while I'm serving someone in-store."
          </p>
          <p className="mt-3 text-xs font-medium opacity-70" style={{ color: t.accentText }}>
            Amina Hassan · Owner, Amina's Boutique
          </p>
        </div>
      </div>

      <div className="flex items-center justify-center px-6 py-16">
        <div className="w-full max-w-sm">
          <h1 className="text-2xl font-semibold tracking-tight mb-2" style={{ color: t.text }}>
            Welcome back
          </h1>
          <p className="text-sm mb-8" style={{ color: t.muted }}>
            Log in to your MtejaAI account.
          </p>

          {submitted && (
            <div
              className="mb-5 px-4 py-3 rounded-xl text-sm"
              style={{ background: `${t.accent}1A`, color: t.accent }}
            >
              Form validated and submitted — no backend connected yet, so nothing
              actually logged you in. Check the browser console for the captured values.
            </div>
          )}

          <form className="space-y-4" onSubmit={handleSubmit} noValidate>
            <div>
              <label className="text-xs font-medium block mb-1.5" style={{ color: t.muted }}>
                Email address
              </label>
              <div className="relative">
                <Mail
                  size={16}
                  className="absolute left-3.5 top-1/2 -translate-y-1/2"
                  style={{ color: t.muted }}
                />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@business.com"
                  onFocus={() => setFocused('email')}
                  onBlur={() => setFocused(null)}
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl text-sm outline-none transition-colors"
                  style={inputStyle('email', !!errors.email)}
                />
              </div>
              {errors.email && (
                <p className="text-xs mt-1.5" style={{ color: '#E5484D' }}>
                  {errors.email}
                </p>
              )}
            </div>

            <div>
              <div className="flex justify-between items-center mb-1.5">
                <label className="text-xs font-medium" style={{ color: t.muted }}>
                  Password
                </label>
                <a href="#" className="text-xs font-medium hover:opacity-70" style={{ color: t.accent }}>
                  Forgot password?
                </a>
              </div>
              <div className="relative">
                <Lock
                  size={16}
                  className="absolute left-3.5 top-1/2 -translate-y-1/2"
                  style={{ color: t.muted }}
                />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  onFocus={() => setFocused('password')}
                  onBlur={() => setFocused(null)}
                  className="w-full pl-10 pr-10 py-2.5 rounded-xl text-sm outline-none transition-colors"
                  style={inputStyle('password', !!errors.password)}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((s) => !s)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2"
                  style={{ color: t.muted }}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
              {errors.password && (
                <p className="text-xs mt-1.5" style={{ color: '#E5484D' }}>
                  {errors.password}
                </p>
              )}
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full py-3 rounded-xl font-medium transition-transform hover:scale-[1.01] flex items-center justify-center gap-2 disabled:opacity-70 disabled:hover:scale-100"
              style={{ background: t.accent, color: t.accentText }}
            >
              {isSubmitting && <Loader2 size={16} className="animate-spin" />}
              {isSubmitting ? 'Logging in…' : 'Log in'}
            </button>
          </form>

          <div className="flex items-center gap-3 my-6">
            <div className="flex-1 h-px" style={{ background: t.border }} />
            <span className="text-xs" style={{ color: t.muted }}>
              or continue with
            </span>
            <div className="flex-1 h-px" style={{ background: t.border }} />
          </div>

          <button
            className="w-full py-2.5 rounded-xl font-medium text-sm flex items-center justify-center gap-2 transition-colors"
            style={{ border: `1px solid ${t.border}`, color: t.text }}
          >
            <svg width="16" height="16" viewBox="0 0 48 48">
              <path fill="#EA4335" d="M24 9.5c3.5 0 6.6 1.2 9.1 3.6l6.8-6.8C35.9 2.4 30.4 0 24 0 14.6 0 6.5 5.4 2.5 13.2l7.9 6.1C12.3 13.1 17.7 9.5 24 9.5z"/>
              <path fill="#4285F4" d="M46.5 24.5c0-1.6-.1-3.1-.4-4.5H24v9h12.6c-.5 3-2.2 5.5-4.7 7.2l7.3 5.7c4.3-4 6.8-9.8 6.8-17.4z"/>
              <path fill="#FBBC05" d="M10.4 28.3A14.4 14.4 0 0 1 9.6 24c0-1.5.3-3 .7-4.3l-7.9-6.1A24 24 0 0 0 0 24c0 3.9.9 7.5 2.5 10.7l7.9-6.4z"/>
              <path fill="#34A853" d="M24 48c6.5 0 11.9-2.1 15.9-5.8l-7.3-5.7c-2 1.4-4.7 2.3-8.6 2.3-6.3 0-11.7-3.6-13.6-8.8l-7.9 6.4C6.5 42.6 14.6 48 24 48z"/>
            </svg>
            Continue with Google
          </button>

          <p className="text-center text-sm mt-8" style={{ color: t.muted }}>
            Don't have an account?{' '}
            <Link to="/signup" className="font-medium" style={{ color: t.accent }}>
              Sign up free
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;
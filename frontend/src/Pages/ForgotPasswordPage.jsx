import { useEffect, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Eye, EyeOff, Mail, Lock } from 'lucide-react';
import { apiPost } from '../api/Client';

function isValidEmail(value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

function ForgotPasswordPage({ t }) {
  const location = useLocation();
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [email, setEmail] = useState(location.state?.email || '');
  const [code, setCode] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [resendSeconds, setResendSeconds] = useState(0);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (resendSeconds <= 0) return undefined;
    const timer = window.setTimeout(() => setResendSeconds((seconds) => seconds - 1), 1000);
    return () => window.clearTimeout(timer);
  }, [resendSeconds]);

  async function requestCode(event) {
    event.preventDefault();
    setError('');
    if (!isValidEmail(email)) {
      setError('Enter a valid email address.');
      return;
    }
    setBusy(true);
    try {
      await apiPost('/api/v1/auth/forgot-password', { email });
      setStep(2);
      setResendSeconds(60);
    } catch (err) {
      setError(err.message || 'Could not request a password reset code.');
    } finally {
      setBusy(false);
    }
  }

  async function resendCode() {
    setError('');
    setBusy(true);
    try {
      await apiPost('/api/v1/auth/resend-password-reset', { email });
      setResendSeconds(60);
    } catch (err) {
      setError(err.message || 'Could not resend the code.');
    } finally {
      setBusy(false);
    }
  }

  async function updatePassword(event) {
    event.preventDefault();
    setError('');
    if (!/^\d{6}$/.test(code)) {
      setError('Enter the 6-digit code.');
      return;
    }
    if (password.length < 8) {
      setError('Password must be at least 8 characters.');
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    setBusy(true);
    try {
      await apiPost('/api/v1/auth/reset-password', {
        email,
        code,
        new_password: password,
      });
      setStep(3);
      window.setTimeout(() => navigate('/login', { replace: true, state: { notice: 'Password updated. Please log in.' } }), 1500);
    } catch (err) {
      setError(err.message || 'Could not update the password.');
    } finally {
      setBusy(false);
    }
  }

  const inputClass = 'w-full min-h-11 pl-10 pr-4 py-2.5 rounded-xl text-base sm:text-sm outline-none focus-visible:ring-2';
  const inputStyle = { background: t.bg, border: `1px solid ${t.border}`, color: t.text };

  return (
    <main className="min-h-[100dvh] pt-[calc(4.3125rem+env(safe-area-inset-top))] sm:pt-[calc(4.8125rem+env(safe-area-inset-top))] flex items-center justify-center px-4 sm:px-6 py-6 sm:py-12">
      <section className="w-full max-w-md" aria-live="polite">
        <h1 className="text-2xl font-semibold mb-2" style={{ color: t.text }}>
          {step === 1 ? 'Reset your password' : step === 2 ? 'Choose a new password' : 'Password updated'}
        </h1>
        <p className="text-sm mb-6" style={{ color: t.muted }}>
          {step === 1 && 'Enter your account email and we will send a reset code if it exists.'}
          {step === 2 && `Enter the code sent to ${email}, then choose a new password.`}
          {step === 3 && 'Password updated. Please log in.'}
        </p>

        {error && <div className="mb-5 px-4 py-3 rounded-xl text-sm" role="alert" style={{ background: 'rgba(229,72,77,0.1)', color: '#E5484D' }}>{error}</div>}

        {step === 1 && (
          <form className="space-y-4" onSubmit={requestCode} noValidate>
            <label htmlFor="reset-email" className="text-xs font-medium block" style={{ color: t.muted }}>Email address</label>
            <div className="relative">
              <Mail size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2" style={{ color: t.muted }} />
              <input id="reset-email" type="email" inputMode="email" autoComplete="email" autoCapitalize="none" spellCheck={false}
                value={email} onChange={(event) => setEmail(event.target.value)} className={inputClass} style={inputStyle} />
            </div>
            <button disabled={busy} className="w-full min-h-11 py-3 rounded-xl font-medium disabled:opacity-60 focus-visible:outline focus-visible:outline-2"
              style={{ background: t.accent, color: t.accentText }}>{busy ? 'Sending…' : 'Send reset code'}</button>
          </form>
        )}

        {step === 2 && (
          <form className="space-y-4" onSubmit={updatePassword} noValidate>
            <label htmlFor="reset-code" className="text-xs font-medium block" style={{ color: t.muted }}>6-digit code</label>
            <input id="reset-code" type="text" inputMode="numeric" autoComplete="one-time-code" maxLength={6}
              value={code} onChange={(event) => setCode(event.target.value.replace(/\D/g, ''))}
              className="w-full min-h-12 px-4 py-3 rounded-xl text-base tracking-[0.35em] text-center outline-none" style={inputStyle} />
            <label htmlFor="reset-password" className="text-xs font-medium block" style={{ color: t.muted }}>New password</label>
            <div className="relative">
              <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2" style={{ color: t.muted }} />
              <input id="reset-password" type={showPassword ? 'text' : 'password'} autoComplete="new-password" autoCapitalize="none" spellCheck={false}
                value={password} onChange={(event) => setPassword(event.target.value)} className={`${inputClass} pr-12`} style={inputStyle} />
              <button type="button" onClick={() => setShowPassword((shown) => !shown)} className="absolute right-1 top-1/2 -translate-y-1/2 min-h-11 min-w-11 flex items-center justify-center"
                style={{ color: t.muted }} aria-label={showPassword ? 'Hide password' : 'Show password'}>{showPassword ? <EyeOff size={18} /> : <Eye size={18} />}</button>
            </div>
            <label htmlFor="confirm-reset-password" className="text-xs font-medium block" style={{ color: t.muted }}>Confirm new password</label>
            <input id="confirm-reset-password" type={showPassword ? 'text' : 'password'} autoComplete="new-password" autoCapitalize="none" spellCheck={false}
              value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} className={inputClass} style={inputStyle} />
            <button disabled={busy} className="w-full min-h-11 py-3 rounded-xl font-medium disabled:opacity-60 focus-visible:outline focus-visible:outline-2"
              style={{ background: t.accent, color: t.accentText }}>{busy ? 'Updating…' : 'Update password'}</button>
            <button type="button" disabled={busy || resendSeconds > 0} onClick={resendCode} className="w-full min-h-11 text-sm font-medium disabled:opacity-60" style={{ color: t.accent }}>
              {resendSeconds > 0 ? `Resend code in ${resendSeconds}s` : 'Resend code'}
            </button>
          </form>
        )}

        {step === 3 && <div className="px-4 py-3 rounded-xl text-sm" style={{ background: `${t.accent}18`, color: t.accent }}>Password updated. Please log in.</div>}
        <p className="text-center text-sm mt-6" style={{ color: t.muted }}>Remembered it? <Link to="/login" className="font-medium" style={{ color: t.accent }}>Back to login</Link></p>
      </section>
    </main>
  );
}

export default ForgotPasswordPage;

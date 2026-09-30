import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Eye, EyeOff, Mail, Lock, User, Building2, Loader2 } from 'lucide-react';
import { apiPost } from '../api/Client';

function isValidEmail(value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

function SignupPage({ t }) {
  const [showPassword, setShowPassword] = useState(false);
  const [focused, setFocused] = useState(null);

  const [name, setName] = useState('');
  const [organizationName, setOrganizationName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [agreed, setAgreed] = useState(false);

  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState('');
  const [verifyEmail, setVerifyEmail] = useState(false);
  const [verificationCode, setVerificationCode] = useState('');
  const [resendSeconds, setResendSeconds] = useState(0);

  useEffect(() => {
    if (resendSeconds <= 0) return undefined;
    const timer = window.setTimeout(() => setResendSeconds((seconds) => seconds - 1), 1000);
    return () => window.clearTimeout(timer);
  }, [resendSeconds]);

  const inputStyle = (fieldName, hasError) => ({
    background: t.bg,
    border: `1.5px solid ${
      hasError ? '#E5484D' : focused === fieldName ? t.accent : t.border
    }`,
    color: t.text,
  });

  function validate() {
    const next = {};
    if (!name.trim()) next.name = 'Name is required.';
    if (!organizationName.trim()) next.organizationName = 'Business name is required.';

    if (!email.trim()) next.email = 'Email is required.';
    else if (!isValidEmail(email)) next.email = 'Enter a valid email address.';

    if (!password) next.password = 'Password is required.';
    else if (password.length < 8) next.password = 'Password must be at least 8 characters.';

    if (confirmPassword !== password) next.confirmPassword = 'Passwords do not match.';

    if (!agreed) next.agreed = 'You must agree to the terms to continue.';

    return next;
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitError('');

    const foundErrors = validate();
    setErrors(foundErrors);
    if (Object.keys(foundErrors).length > 0) return;

    setIsSubmitting(true);

    try {
     
      await apiPost('/api/v1/auth/register', {
        email,
        full_name: name,
        password,
        organization_name: organizationName,
      });

      setVerifyEmail(true);
      setResendSeconds(60);
    } catch (err) {
      setSubmitError(err.message || 'Something went wrong. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleVerifyEmail(event) {
    event.preventDefault();
    setSubmitError('');
    if (!/^\d{6}$/.test(verificationCode)) {
      setSubmitError('Enter the 6-digit verification code.');
      return;
    }
    setIsSubmitting(true);
    try {
      const tokens = await apiPost('/api/v1/auth/verify-email', { email, code: verificationCode });
      localStorage.setItem('access_token', tokens.access_token);
      localStorage.setItem('refresh_token', tokens.refresh_token);
      window.location.replace('/dashboard');
    } catch (err) {
      setSubmitError(err.message || 'The code could not be verified.');
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleResendCode() {
    setSubmitError('');
    try {
      await apiPost('/api/v1/auth/resend-verification', { email });
      setResendSeconds(60);
    } catch (err) {
      setSubmitError(err.message || 'Could not resend the code.');
    }
  }

  return (
    <div>
      <div className="min-h-[100dvh] pt-[calc(4.3125rem+env(safe-area-inset-top))] sm:pt-[calc(4.8125rem+env(safe-area-inset-top))] flex items-center justify-center px-4 sm:px-6 py-6 sm:py-12">
        <div className="w-full max-w-sm">
          <h1 className="text-2xl font-semibold tracking-tight mb-2" style={{ color: t.text }}>
            {verifyEmail ? 'Verify your email' : 'Create your account'}
          </h1>
          <p className="text-sm mb-8" style={{ color: t.muted }}>
            {verifyEmail ? `Enter the 6-digit code sent to ${email}.` : 'Start your free 14-day trial. No credit card required.'}
          </p>

          {submitError && (
            <div
              className="mb-5 px-4 py-3 rounded-xl text-sm"
              style={{ background: 'rgba(229,72,77,0.1)', color: '#E5484D' }}
            >
              {submitError}
            </div>
          )}

          {verifyEmail ? (
            <form className="space-y-4" onSubmit={handleVerifyEmail} noValidate>
              <label htmlFor="signup-verification-code" className="text-xs font-medium block" style={{ color: t.muted }}>Verification code</label>
              <input id="signup-verification-code" type="text" inputMode="numeric" autoComplete="one-time-code" maxLength={6}
                value={verificationCode} onChange={(event) => setVerificationCode(event.target.value.replace(/\D/g, ''))}
                className="w-full min-h-12 px-4 py-3 rounded-xl text-base tracking-[0.35em] text-center outline-none"
                style={inputStyle('verificationCode', !!submitError)} />
              <button type="submit" disabled={isSubmitting} className="w-full min-h-11 py-3 rounded-xl font-medium disabled:opacity-60 focus-visible:outline focus-visible:outline-2"
                style={{ background: t.accent, color: t.accentText }}>
                {isSubmitting ? 'Verifying…' : 'Verify email'}
              </button>
              <button type="button" disabled={resendSeconds > 0} onClick={handleResendCode}
                className="w-full min-h-11 text-sm font-medium disabled:opacity-60" style={{ color: t.accent }}>
                {resendSeconds > 0 ? `Resend code in ${resendSeconds}s` : 'Resend code'}
              </button>
            </form>
          ) : (
          <form className="space-y-4" onSubmit={handleSubmit} noValidate>
            <div>
              <label htmlFor="signup-name" className="text-xs font-medium block mb-1.5" style={{ color: t.muted }}>
                Full name
              </label>
              <div className="relative">
                <User size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2" style={{ color: t.muted }} />
                <input
                  type="text"
                  id="signup-name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Amina Hassan"
                  onFocus={() => setFocused('name')}
                  onBlur={() => setFocused(null)}
                  className="w-full min-h-11 pl-10 pr-4 py-2.5 rounded-xl text-base sm:text-sm outline-none transition-colors"
                  style={inputStyle('name', !!errors.name)}
                />
              </div>
              {errors.name && <p className="text-xs mt-1.5" style={{ color: '#E5484D' }}>{errors.name}</p>}
            </div>

            <div>
              <label htmlFor="signup-organization" className="text-xs font-medium block mb-1.5" style={{ color: t.muted }}>
                Business name
              </label>
              <div className="relative">
                <Building2 size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2" style={{ color: t.muted }} />
                <input
                  type="text"
                  id="signup-organization"
                  value={organizationName}
                  onChange={(e) => setOrganizationName(e.target.value)}
                  placeholder="Amina's Boutique"
                  onFocus={() => setFocused('organizationName')}
                  onBlur={() => setFocused(null)}
                  className="w-full min-h-11 pl-10 pr-4 py-2.5 rounded-xl text-base sm:text-sm outline-none transition-colors"
                  style={inputStyle('organizationName', !!errors.organizationName)}
                />
              </div>
              {errors.organizationName && <p className="text-xs mt-1.5" style={{ color: '#E5484D' }}>{errors.organizationName}</p>}
            </div>

            <div>
              <label htmlFor="signup-email" className="text-xs font-medium block mb-1.5" style={{ color: t.muted }}>
                Email address
              </label>
              <div className="relative">
                <Mail size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2" style={{ color: t.muted }} />
                <input
                  type="email"
                  id="signup-email"
                  inputMode="email"
                  autoComplete="email"
                  autoCapitalize="none"
                  spellCheck={false}
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@business.com"
                  onFocus={() => setFocused('email')}
                  onBlur={() => setFocused(null)}
                  className="w-full min-h-11 pl-10 pr-4 py-2.5 rounded-xl text-base sm:text-sm outline-none transition-colors"
                  style={inputStyle('email', !!errors.email)}
                />
              </div>
              {errors.email && <p className="text-xs mt-1.5" style={{ color: '#E5484D' }}>{errors.email}</p>}
            </div>

            <div>
              <label htmlFor="signup-password" className="text-xs font-medium block mb-1.5" style={{ color: t.muted }}>
                Password
              </label>
              <div className="relative">
                <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2" style={{ color: t.muted }} />
                <input
                  type={showPassword ? 'text' : 'password'}
                  id="signup-password"
                  autoComplete="new-password"
                  autoCapitalize="none"
                  spellCheck={false}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  onFocus={() => setFocused('password')}
                  onBlur={() => setFocused(null)}
                  className="w-full min-h-11 pl-10 pr-10 py-2.5 rounded-xl text-base sm:text-sm outline-none transition-colors"
                  style={inputStyle('password', !!errors.password)}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((s) => !s)}
                  className="absolute right-1 top-1/2 -translate-y-1/2 min-h-11 min-w-11 flex items-center justify-center"
                  style={{ color: t.muted }}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
              {errors.password && <p className="text-xs mt-1.5" style={{ color: '#E5484D' }}>{errors.password}</p>}
            </div>

            <div>
              <label htmlFor="signup-confirm-password" className="text-xs font-medium block mb-1.5" style={{ color: t.muted }}>
                Confirm password
              </label>
              <div className="relative">
                <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2" style={{ color: t.muted }} />
                <input
                  type={showPassword ? 'text' : 'password'}
                  id="signup-confirm-password"
                  autoComplete="new-password"
                  autoCapitalize="none"
                  spellCheck={false}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="••••••••"
                  onFocus={() => setFocused('confirmPassword')}
                  onBlur={() => setFocused(null)}
                  className="w-full min-h-11 pl-10 pr-4 py-2.5 rounded-xl text-base sm:text-sm outline-none transition-colors"
                  style={inputStyle('confirmPassword', !!errors.confirmPassword)}
                />
              </div>
              {errors.confirmPassword && <p className="text-xs mt-1.5" style={{ color: '#E5484D' }}>{errors.confirmPassword}</p>}
            </div>

            <div>
              <label className="flex items-start gap-2.5 cursor-pointer">
                <input
                  type="checkbox"
                  checked={agreed}
                  onChange={(e) => setAgreed(e.target.checked)}
                  className="mt-0.5"
                  style={{ accentColor: t.accent }}
                />
                <span className="text-xs leading-relaxed" style={{ color: t.muted }}>
                  I agree to the{' '}
                  <Link to="/terms" className="font-medium hover:opacity-70" style={{ color: t.accent }}>
                    Terms of Service
                  </Link>{' '}
                  and{' '}
                  <Link to="/privacy" className="font-medium hover:opacity-70" style={{ color: t.accent }}>
                    Privacy Policy
                  </Link>
                </span>
              </label>
              {errors.agreed && <p className="text-xs mt-1.5" style={{ color: '#E5484D' }}>{errors.agreed}</p>}
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full min-h-11 py-3 rounded-xl font-medium focus-visible:outline focus-visible:outline-2 flex items-center justify-center gap-2 disabled:opacity-70"
              style={{ background: t.accent, color: t.accentText }}
            >
              {isSubmitting && <Loader2 size={16} className="animate-spin" />}
              {isSubmitting ? 'Creating account…' : 'Create account'}
            </button>
          </form>
          )}

          <p className="text-center text-sm mt-8" style={{ color: t.muted }}>
            Already have an account?{' '}
            <Link to="/login" className="font-medium" style={{ color: t.accent }}>
              Log in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

export default SignupPage;
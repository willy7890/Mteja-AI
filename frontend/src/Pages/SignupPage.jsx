import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff, Mail, Lock, User, Building2, Loader2, Check } from 'lucide-react';
import { apiPost } from '../api/client';

function isValidEmail(value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

function SignupPage({ t }) {
  const navigate = useNavigate();
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
    else if (password.length < 6) next.password = 'Password must be at least 6 characters.';

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
      // The register endpoint returns the created user record, NOT an
      // auth token — so there's no auto-login here. The user has to log
      // in separately right after, which is why we redirect to /login
      // instead of a dashboard.
      await apiPost('/api/v1/auth/register', {
        email,
        full_name: name,
        password,
        organization_name: organizationName,
      });

      navigate('/login', { state: { justSignedUp: true } });
    } catch (err) {
      setSubmitError(err.message || 'Something went wrong. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
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
            Set up your unified inbox in under five minutes.
          </h2>
          <p className="text-sm opacity-80" style={{ color: t.accentText }}>
            Connect WhatsApp, Instagram, email, and calls — MtejaAI starts
            replying to customers the moment you're done.
          </p>
        </div>

        <div className="relative space-y-3">
          {['No credit card required', '14-day free trial', 'Cancel anytime'].map((item) => (
            <div key={item} className="flex items-center gap-2.5">
              <div
                className="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0"
                style={{ background: `${t.accentText}26` }}
              >
                <Check size={12} color={t.accentText} strokeWidth={3} />
              </div>
              <span className="text-sm" style={{ color: t.accentText }}>{item}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="flex items-center justify-center px-6 py-16">
        <div className="w-full max-w-sm">
          <h1 className="text-2xl font-semibold tracking-tight mb-2" style={{ color: t.text }}>
            Create your account
          </h1>
          <p className="text-sm mb-8" style={{ color: t.muted }}>
            Start your free 14-day trial. No credit card required.
          </p>

          {submitError && (
            <div
              className="mb-5 px-4 py-3 rounded-xl text-sm"
              style={{ background: 'rgba(229,72,77,0.1)', color: '#E5484D' }}
            >
              {submitError}
            </div>
          )}

          <form className="space-y-4" onSubmit={handleSubmit} noValidate>
            <div>
              <label className="text-xs font-medium block mb-1.5" style={{ color: t.muted }}>
                Full name
              </label>
              <div className="relative">
                <User size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2" style={{ color: t.muted }} />
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Amina Hassan"
                  onFocus={() => setFocused('name')}
                  onBlur={() => setFocused(null)}
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl text-sm outline-none transition-colors"
                  style={inputStyle('name', !!errors.name)}
                />
              </div>
              {errors.name && <p className="text-xs mt-1.5" style={{ color: '#E5484D' }}>{errors.name}</p>}
            </div>

            <div>
              <label className="text-xs font-medium block mb-1.5" style={{ color: t.muted }}>
                Business name
              </label>
              <div className="relative">
                <Building2 size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2" style={{ color: t.muted }} />
                <input
                  type="text"
                  value={organizationName}
                  onChange={(e) => setOrganizationName(e.target.value)}
                  placeholder="Amina's Boutique"
                  onFocus={() => setFocused('organizationName')}
                  onBlur={() => setFocused(null)}
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl text-sm outline-none transition-colors"
                  style={inputStyle('organizationName', !!errors.organizationName)}
                />
              </div>
              {errors.organizationName && <p className="text-xs mt-1.5" style={{ color: '#E5484D' }}>{errors.organizationName}</p>}
            </div>

            <div>
              <label className="text-xs font-medium block mb-1.5" style={{ color: t.muted }}>
                Email address
              </label>
              <div className="relative">
                <Mail size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2" style={{ color: t.muted }} />
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
              {errors.email && <p className="text-xs mt-1.5" style={{ color: '#E5484D' }}>{errors.email}</p>}
            </div>

            <div>
              <label className="text-xs font-medium block mb-1.5" style={{ color: t.muted }}>
                Password
              </label>
              <div className="relative">
                <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2" style={{ color: t.muted }} />
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
              {errors.password && <p className="text-xs mt-1.5" style={{ color: '#E5484D' }}>{errors.password}</p>}
            </div>

            <div>
              <label className="text-xs font-medium block mb-1.5" style={{ color: t.muted }}>
                Confirm password
              </label>
              <div className="relative">
                <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2" style={{ color: t.muted }} />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="••••••••"
                  onFocus={() => setFocused('confirmPassword')}
                  onBlur={() => setFocused(null)}
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl text-sm outline-none transition-colors"
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
              className="w-full py-3 rounded-xl font-medium transition-transform hover:scale-[1.01] flex items-center justify-center gap-2 disabled:opacity-70 disabled:hover:scale-100"
              style={{ background: t.accent, color: t.accentText }}
            >
              {isSubmitting && <Loader2 size={16} className="animate-spin" />}
              {isSubmitting ? 'Creating account…' : 'Create account'}
            </button>
          </form>

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
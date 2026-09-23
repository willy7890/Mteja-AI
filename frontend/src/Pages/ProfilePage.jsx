import { useEffect, useRef, useState } from 'react';
import { apiGet } from '../api/Client';
import {
  User,
  Mail,
  Phone,
  Building,
  Shield,
  Camera,
  Check,
  Save,
  Lock,
  Smartphone,
  Globe
} from 'lucide-react';

export const ProfilePage = ({ user: initialUser }) => {
  const [user, setUser] = useState(initialUser);
  const [name, setName] = useState(initialUser.name);
  const [email, setEmail] = useState(initialUser.email);
  const [phone, setPhone] = useState(initialUser.phone);
  const [company, setCompany] = useState(initialUser.company);
  const [origin, setOrigin] = useState(() => localStorage.getItem('mteja_profile_origin') || 'Dar es Salaam, Tanzania');
  const [avatar, setAvatar] = useState(() => localStorage.getItem('mteja_profile_avatar') || initialUser.avatar);
  const [language, setLanguage] = useState(() => localStorage.getItem('mteja_language') || 'sw-en');
  const avatarInput = useRef(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    apiGet('/api/v1/auth/me').then((data) => {
      setUser(data);
      setName(data.full_name || initialUser.name);
      setEmail(data.email || initialUser.email);
    }).catch(() => {});
  }, [initialUser.email, initialUser.name]);

  const handleAvatar = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    const nextAvatar = URL.createObjectURL(file);
    setAvatar(nextAvatar);
    localStorage.setItem('mteja_profile_avatar', nextAvatar);
  };

  const handleSave = (e) => {
    e.preventDefault();
    localStorage.setItem('mteja_profile_origin', origin);
    localStorage.setItem('mteja_language', language);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="p-6 md:p-8 max-w-4xl mx-auto space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-[#10231C] tracking-tight">User Profile</h2>
        <p className="text-xs text-[#68756F] mt-1">
          Manage your personal account credentials, security access, and display preferences.
        </p>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* Avatar & Core Bio */}
        <div className="p-6 rounded-2xl bg-white border border-[#E2E4DF] shadow-2xs flex flex-col sm:flex-row items-center gap-6">
          <div className="relative">
            <img
              src={avatar}
              alt={name}
              className="w-20 h-20 rounded-full object-cover border-2 border-[#287A59]"
            />
            <button
              type="button"
              onClick={() => avatarInput.current?.click()}
              className="absolute bottom-0 right-0 p-1.5 rounded-full bg-[#10231C] text-white hover:bg-[#287A59] transition-colors shadow-xs"
              title="Upload new photo"
            >
              <Camera className="w-3.5 h-3.5" />
            </button>
            <input ref={avatarInput} type="file" accept="image/*" className="hidden" onChange={handleAvatar} />
          </div>

          <div className="text-center sm:text-left space-y-1">
            <div className="flex items-center justify-center sm:justify-start gap-2">
              <h3 className="text-base font-bold text-[#10231C]">{name}</h3>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#287A59]/15 text-[#287A59]">
                {user.role}
              </span>
            </div>
            <p className="text-xs text-[#68756F]">{company} • {origin}</p>
            <p className="text-[11px] text-[#68756F]">Primary contact for Vodacom & Meta Business Cloud API webhooks.</p>
          </div>
        </div>

        {/* Contact Details Card */}
        <div className="p-6 rounded-2xl bg-white border border-[#E2E4DF] shadow-2xs space-y-4 text-xs">
          <h4 className="text-sm font-bold text-[#10231C]">Personal Details</h4>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block font-semibold text-[#14201B] mb-1">Full Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full p-2.5 rounded-xl border border-[#E2E4DF] bg-[#F7F6F1] focus:bg-white focus:outline-none focus:border-[#287A59]"
              />
            </div>

            <div>
              <label className="block font-semibold text-[#14201B] mb-1">Email Address</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full p-2.5 rounded-xl border border-[#E2E4DF] bg-[#F7F6F1] focus:bg-white focus:outline-none focus:border-[#287A59]"
              />
            </div>

            <div>
              <label className="block font-semibold text-[#14201B] mb-1">Mobile Phone (Tanzania)</label>
              <input
                type="text"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                className="w-full p-2.5 rounded-xl border border-[#E2E4DF] bg-[#F7F6F1] focus:bg-white focus:outline-none focus:border-[#287A59]"
              />
            </div>

            <div>
              <label className="block font-semibold text-[#14201B] mb-1">Business Organization</label>
              <input
                type="text"
                value={company}
                onChange={(e) => setCompany(e.target.value)}
                className="w-full p-2.5 rounded-xl border border-[#E2E4DF] bg-[#F7F6F1] focus:bg-white focus:outline-none focus:border-[#287A59]"
              />
            </div>

            <div>
              <label className="block font-semibold text-[#14201B] mb-1">Origin / Location</label>
              <input
                type="text"
                value={origin}
                onChange={(e) => setOrigin(e.target.value)}
                className="w-full p-2.5 rounded-xl border border-[#E2E4DF] bg-[#F7F6F1] focus:bg-white focus:outline-none focus:border-[#287A59]"
              />
            </div>

            <div>
              <label className="block font-semibold text-[#14201B] mb-1">Preferred Language</label>
              <select value={language} onChange={(e) => setLanguage(e.target.value)} className="w-full p-2.5 rounded-xl border border-[#E2E4DF] bg-[#F7F6F1]">
                <option value="sw-en">Swahili and English</option>
                <option value="sw">Swahili</option>
                <option value="en">English</option>
              </select>
            </div>
          </div>
        </div>

        {/* Password & Security Card */}
        <div className="p-6 rounded-2xl bg-white border border-[#E2E4DF] shadow-2xs space-y-4 text-xs">
          <h4 className="text-sm font-bold text-[#10231C]">Password & Authentication</h4>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block font-semibold text-[#14201B] mb-1">Current Password</label>
              <input
                type="password"
                defaultValue="••••••••••••"
                className="w-full p-2.5 rounded-xl border border-[#E2E4DF] bg-[#F7F6F1]"
              />
            </div>

            <div>
              <label className="block font-semibold text-[#14201B] mb-1">New Password</label>
              <input
                type="password"
                placeholder="Leave blank to keep current"
                className="w-full p-2.5 rounded-xl border border-[#E2E4DF] bg-[#F7F6F1]"
              />
            </div>
          </div>
        </div>

        <div className="flex justify-end gap-3">
          <button
            type="submit"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#287A59] hover:bg-[#1f5f45] text-white text-xs font-bold transition-colors shadow-2xs"
          >
            {saved ? <Check className="w-4 h-4" /> : <Save className="w-4 h-4" />}
            <span>{saved ? 'Changes Saved' : 'Save Profile'}</span>
          </button>
        </div>
      </form>
    </div>
  );
};
export default ProfilePage;
import React, { useState } from 'react';
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
import { UserProfile, PageId } from '../../types';

interface ProfilePageProps {
  user: UserProfile;
  onNavigate: (page: PageId) => void;
}

export const ProfilePage: React.FC<ProfilePageProps> = ({ user, onNavigate }) => {
  const [name, setName] = useState(user.name);
  const [email, setEmail] = useState(user.email);
  const [phone, setPhone] = useState(user.phone);
  const [company, setCompany] = useState(user.company);
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
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
              src={user.avatar}
              alt={name}
              className="w-20 h-20 rounded-full object-cover border-2 border-[#287A59]"
            />
            <button
              type="button"
              className="absolute bottom-0 right-0 p-1.5 rounded-full bg-[#10231C] text-white hover:bg-[#287A59] transition-colors shadow-xs"
              title="Upload new photo"
            >
              <Camera className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="text-center sm:text-left space-y-1">
            <div className="flex items-center justify-center sm:justify-start gap-2">
              <h3 className="text-base font-bold text-[#10231C]">{name}</h3>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#287A59]/15 text-[#287A59]">
                {user.role}
              </span>
            </div>
            <p className="text-xs text-[#68756F]">{company} • Dar es Salaam, Tanzania</p>
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
import { useEffect, useState } from 'react';
import { Check, ShieldCheck, Loader2 } from 'lucide-react';
import { apiAuthPost, apiGet } from '../api/Client';

function AdminPage({ t }) {
  const [pendingUsers, setPendingUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeId, setActiveId] = useState(null);
  const [error, setError] = useState('');

  async function loadPendingUsers() {
    try {
      setError('');
      const users = await apiGet('/api/v1/admin/pending-verifications');
      setPendingUsers(Array.isArray(users) ? users : []);
    } catch (err) {
      setError(err.message || 'Unable to load pending verifications.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadPendingUsers();
  }, []);

  async function verifyUser(userId) {
    setActiveId(userId);
    try {
      await apiAuthPost(`/api/v1/admin/users/${userId}/verify`, {});
      setPendingUsers((users) => users.filter((user) => user.id !== userId));
    } catch (err) {
      setError(err.message || 'Unable to verify this user.');
    } finally {
      setActiveId(null);
    }
  }

  return (
    <div className="p-4 sm:p-8 max-w-5xl mx-auto">
      <div className="flex items-start justify-between gap-4 mb-8">
        <div>
          <p className="text-xs font-bold uppercase tracking-widest mb-2" style={{ color: t.accent }}>
            Super admin
          </p>
          <h2 className="text-2xl font-semibold" style={{ color: t.text }}>Account verification</h2>
          <p className="mt-2 text-sm" style={{ color: t.muted }}>
            Verify admin accounts before they can access the workspace.
          </p>
        </div>
        <ShieldCheck size={28} style={{ color: t.accent }} />
      </div>

      {error && (
        <div className="mb-5 px-4 py-3 rounded-xl text-sm" style={{ background: 'rgba(229,72,77,0.1)', color: '#E5484D' }}>
          {error}
        </div>
      )}

      <section className="rounded-2xl p-4 sm:p-6" style={{ background: t.card, border: `1px solid ${t.border}` }}>
        <h3 className="font-semibold" style={{ color: t.text }}>Pending verification</h3>
        {loading ? (
          <div className="py-10 flex justify-center" style={{ color: t.muted }}><Loader2 className="animate-spin" /></div>
        ) : pendingUsers.length === 0 ? (
          <p className="py-10 text-sm" style={{ color: t.muted }}>No accounts are waiting for verification.</p>
        ) : (
          <div className="mt-4 space-y-3">
            {pendingUsers.map((user) => (
              <div key={user.id} className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-xl" style={{ background: t.surface }}>
                <div>
                  <p className="font-medium" style={{ color: t.text }}>{user.full_name}</p>
                  <p className="text-sm" style={{ color: t.muted }}>{user.email}</p>
                  <p className="text-xs mt-1" style={{ color: t.muted }}>Role: {user.role}</p>
                </div>
                <button
                  type="button"
                  disabled={activeId === user.id}
                  onClick={() => verifyUser(user.id)}
                  className="px-4 py-2.5 rounded-full inline-flex items-center justify-center gap-2 text-sm font-medium disabled:opacity-70"
                  style={{ background: t.accent, color: t.accentText }}
                >
                  {activeId === user.id ? <Loader2 size={15} className="animate-spin" /> : <Check size={15} />}
                  Verify account
                </button>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

export default AdminPage;
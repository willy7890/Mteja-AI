import { useState, useEffect } from 'react';
import { useNavigate, useLocation, Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import TopHeader from './TopHeader';
import { apiGet } from '../api/Client';

const TOP_LEVEL_PAGES = ['login'];

function DashboardLayout({ t }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [channelFilter, setChannelFilter] = useState(null);
  const [user, setUser] = useState(null);
  const [loadingUser, setLoadingUser] = useState(true);

  const pathParts = location.pathname.split('/').filter(Boolean);
  const currentPage = pathParts[1] || 'dashboard';

  
  useEffect(() => {
    async function loadUser() {
      const token = localStorage.getItem('access_token');
      if (!token) {
        navigate('/login');
        return;
      }
      try {
        const data = await apiGet('/api/v1/auth/me');
        setUser(data);
      } catch {
        navigate('/login');
      } finally {
        setLoadingUser(false);
      }
    }
    loadUser();
  }, [navigate]);

  function handleNavigate(pageId) {
    if (TOP_LEVEL_PAGES.includes(pageId)) {
      navigate(`/${pageId}`);
    } else if (pageId === 'dashboard') {
      navigate('/dashboard');
    } else {
      navigate(`/dashboard/${pageId}`);
    }
  }

  function handleLogout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    navigate('/login');
  }

  // Avoids a flash of the dashboard shell (with stale/placeholder user
  // info) before we've confirmed the token is actually valid.
  if (loadingUser) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: t.bg, color: t.muted }}>
        Loading…
      </div>
    );
  }

  return (
    <div className="flex min-h-screen" style={{ background: t.bg }}>
      <Sidebar
        t={t}
        user={user}
        currentPage={currentPage}
        onNavigate={handleNavigate}
        onCloseMobile={() => setMobileOpen(false)}
        mobileOpen={mobileOpen}
        activeChannelFilter={channelFilter}
        onSelectChannelFilter={setChannelFilter}
        unreadInboxCount={3}
      />

      <div className="flex-1 flex flex-col min-w-0">
        <TopHeader
          t={t}
          user={user}
          currentPage={currentPage}
          onNavigate={handleNavigate}
          onLogout={handleLogout}
          onToggleMobileMenu={() => setMobileOpen((o) => !o)}
          onOpenCommandPalette={() => {
            console.log('Command palette not wired yet.');
          }}
          unreadCount={2}
        />

        <main className="flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export default DashboardLayout;
import { useState, useEffect } from 'react';
import { useNavigate, useLocation, Outlet } from 'react-router-dom';
import { ChannelsPage } from "./ChannelsPage";
import Sidebar from './Sidebar';
import TopHeader from './TopHeader';
import { apiGet } from '../api/Client';
import { useTelegramMessages } from '../hooks/useTelegramMessages'; 

const TOP_LEVEL_PAGES = ['login'];

function DashboardLayout({ t }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [channelFilter, setChannelFilter] = useState(null);
  const [user, setUser] = useState(null);
  const [loadingUser, setLoadingUser] = useState(true);

  const { messages, isConnected } = useTelegramMessages();

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
        // 3. Tunapitisha idadi halisi ya jumbe mpya kutoka kwenye WebSocket badala ya '3'
        unreadInboxCount={messages.length} 
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
          // 4. Mfano wa kuonyesha status ya WebSocket (kama iko Connected au la)
          unreadCount={messages.length}
        />

        <main className="flex-1 overflow-y-auto">
          {/* 5. Tunapitisha jumbe zote na status ya connection kwenda kwenye kurasa za ndani (Inbox/Dashboard) */}
          <Outlet context={{ messages, isConnected }} />
        </main>
      </div>
    </div>
  );
}

export default DashboardLayout;
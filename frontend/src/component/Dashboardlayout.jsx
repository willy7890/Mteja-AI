import { useState } from 'react';
import { useNavigate, useLocation, Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import TopHeader from './TopHeader';


const TOP_LEVEL_PAGES = ['login'];

function DashboardLayout({ t }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [channelFilter, setChannelFilter] = useState(null);

  
  const pathParts = location.pathname.split('/').filter(Boolean); // e.g. ['dashboard','inbox']
  const currentPage = pathParts[1] || 'dashboard';

  
  function handleNavigate(pageId) {
    if (TOP_LEVEL_PAGES.includes(pageId)) {
      navigate(`/${pageId}`);
    } else if (pageId === 'dashboard') {
      navigate('/dashboard');
    } else {
      navigate(`/dashboard/${pageId}`);
    }
  }

  return (
    <div className="flex min-h-screen" style={{ background: t.bg }}>
      <Sidebar
        t={t}
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
          currentPage={currentPage}
          onNavigate={handleNavigate}
          onToggleMobileMenu={() => setMobileOpen((o) => !o)}
          onOpenCommandPalette={() => {
            
            console.log('Command palette not wired yet.');
          }}
          unreadCount={2}
        />

        {}
        <main className="flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export default DashboardLayout;
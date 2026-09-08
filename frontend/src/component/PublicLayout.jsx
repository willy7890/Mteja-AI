import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';
import Footer from './Footer';

function PublicLayout({ t, dark, setDark }) {
  return (
    <div
      className="min-h-screen transition-colors duration-300"
      style={{
        background: dark ? t.bgGradient : t.bg,
        backgroundImage: dark ? `${t.bgPattern}, ${t.bgGradient}` : `${t.bgPattern}`,
        backgroundSize: '500px 500px, cover',
        backgroundRepeat: 'repeat, no-repeat',
      }}
    >
      <Navbar t={t} dark={dark} setDark={setDark} />
      <Outlet />
      <Footer t={t} />
    </div>
  );
}

export default PublicLayout;
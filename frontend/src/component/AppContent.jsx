function AppContent({ t, dark, setDark }) {
  const location = useLocation();

  const isDashboard = location.pathname.startsWith('/dashboard');

  return (
    <div
      className="min-h-screen transition-colors duration-300"
      style={{
        background: dark ? t.bgGradient : t.bg,
        backgroundImage: dark
          ? `${t.bgPattern}, ${t.bgGradient}`
          : `${t.bgPattern}`,
        backgroundSize: '500px 500px, cover',
        backgroundRepeat: 'repeat, no-repeat',
      }}
    >
      {!isDashboard && (
        <Navbar
          t={t}
          dark={dark}
          setDark={setDark}
        />
      )}

      <Routes>
        <Route path="/" element={<LandingPage t={t} />} />

        <Route path="/login" element={<LoginPage t={t} />} />

        <Route path="/terms" element={<TermsOfService t={t} />} />

        <Route path="/privacy" element={<PrivacyPolicy t={t} />} />

        <Route path="/dashboard" element={<DashboardLayout t={t} />}>
          <Route index element={<DashboardPage t={t} />} />

          <Route
            path="inbox"
            element={<ComingSoon t={t} title="Inbox" />}
          />

          <Route
            path="customers"
            element={<ComingSoon t={t} title="Customers" />}
          />

          <Route
            path="ai-agent"
            element={<ComingSoon t={t} title="AI Agent" />}
          />

          <Route
            path="automations"
            element={<ComingSoon t={t} title="Automations" />}
          />

          <Route
            path="analytics"
            element={<ComingSoon t={t} title="Analytics" />}
          />

          <Route
            path="channels"
            element={<ComingSoon t={t} title="Channels" />}
          />

          <Route
            path="team"
            element={<ComingSoon t={t} title="Team" />}
          />

          <Route
            path="billing"
            element={<ComingSoon t={t} title="Billing" />}
          />

          <Route
            path="settings"
            element={<ComingSoon t={t} title="Settings" />}
          />

          <Route
            path="notifications"
            element={<ComingSoon t={t} title="Notifications" />}
          />

          <Route
            path="profile"
            element={<ComingSoon t={t} title="Profile" />}
          />
        </Route>
      </Routes>

      {!isDashboard && <Footer t={t} />}
    </div>
  );
}
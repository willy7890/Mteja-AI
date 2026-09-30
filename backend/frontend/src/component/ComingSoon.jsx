function ComingSoon({ t, title }) {
  return (
    <div className="p-10 flex flex-col items-center justify-center text-center" style={{ minHeight: '60vh' }}>
      <h2 className="text-xl font-semibold mb-2" style={{ color: t.text }}>{title}</h2>
      <p className="text-sm" style={{ color: t.muted }}>
        Coming Soon
      </p>
    </div>
  );
}

export default ComingSoon;
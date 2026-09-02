
const companies = ['SigniAI'];

function TrustBar({ t }) {
  return (
    <div className="px-6 pb-16">
      <div className="max-w-4xl mx-auto text-center">
        <p className="text-xs uppercase tracking-wider mb-6" style={{ color: t.muted }}>
          Trusted by fast-growing businesses
        </p>
        <div className="flex flex-wrap justify-center items-center gap-x-10 gap-y-4">
          {companies.map((name) => (
            <span
              key={name}
              className="text-lg font-semibold opacity-50 hover:opacity-80 transition-opacity"
              style={{ color: t.text }}
            >
              {name}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}

export default TrustBar;
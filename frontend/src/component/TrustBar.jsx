
const companies = [
  { type: 'image', src: '/signi-ai.png', name: 'SigniAI' },
  { type: 'text', name: 'Blue Harbor' },
  { type: 'text', name: 'Vertex Retail' },
  { type: 'text', name: 'Cedarline' },
  { type: 'text', name: 'Meridian Co.' },
];

function TrustBar({ t }) {
  return (
    <div className="px-6 pb-16">
      <div className="max-w-4xl mx-auto text-center">
        <p className="text-xs uppercase tracking-wider mb-6" style={{ color: t.muted }}>
          Trusted by fast-growing businesses
        </p>
        <div className="flex flex-wrap justify-center items-center gap-x-10 gap-y-6">
          {companies.map((c) =>
            c.type === 'image' ? (
              
              <img
                key={c.name}
                src={c.src}
                alt={c.name}
                className="h-8 w-auto object-contain transition-transform hover:scale-105"
              />
            ) : (
              <span
                key={c.name}
                className="text-lg font-semibold opacity-50 hover:opacity-80 transition-opacity"
                style={{ color: t.text }}
              >
                {c.name}
              </span>
            )
          )}
        </div>
      </div>
    </div>
  );
}

export default TrustBar;
import { Link } from "react-router-dom";
import ScrollReveal from "./ScrollReveal";


const columns = [
  {
    title: "Product",
    links: [
      { label: "Features", to: "#" },
      { label: "Pricing", to: "#" },
      { label: "Request Demo", to: "#" },
    ],
  },
  {
    title: "Company",
    links: [
      { label: "About", to: "#" },
      { label: "Careers", to: "#" },
      { label: "Contact", to: "#" },
    ],
  },
  {
    title: "Legal",
    links: [
      { label: "Privacy Policy", to: "/privacy" },
      { label: "Terms of Service", to: "/terms" },
    ],
  },
];

function Footer({ t }) {
  // Computed once at render time, so the copyright year never needs
  // manual updating — always reflects whatever year the page is viewed in.
  const year = new Date().getFullYear();

  return (
    <footer className="px-6 pt-16 pb-8" style={{ borderTop: `1px solid ${t.border}` }}>
      {}
      <ScrollReveal y={16}>
        <div className="max-w-6xl mx-auto grid sm:grid-cols-4 gap-10">
          <div>
            <span className="text-lg font-semibold" style={{ color: t.text }}>
              Mteja<span style={{ color: t.accent }}>AI</span>
            </span>
            <p className="mt-3 text-sm max-w-[220px]" style={{ color: t.muted }}>
              Every customer message, answered across every channel you use.
            </p>
          </div>

          {columns.map((col) => (
            <div key={col.title}>
              <div className="text-sm font-semibold mb-3" style={{ color: t.text }}>
                {col.title}
              </div>
              <ul className="space-y-2">
                {col.links.map((link) => (
                  <li key={link.label}>
                    {link.to.startsWith("/") ? (
                     
                      <Link
                        to={link.to}
                        className="text-sm hover:opacity-70 transition-opacity"
                        style={{ color: t.muted }}
                      >
                        {link.label}
                      </Link>
                    ) : (
                      <a
                        href={link.to}
                        className="text-sm hover:opacity-70 transition-opacity"
                        style={{ color: t.muted }}
                      >
                        {link.label}
                      </a>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div
          className="max-w-6xl mx-auto mt-12 pt-6 text-xs"
          style={{ borderTop: `1px solid ${t.border}`, color: t.muted }}
        >
          © {year} MtejaAI. All rights reserved.
        </div>
      </ScrollReveal>
    </footer>
  );
}

export default Footer;
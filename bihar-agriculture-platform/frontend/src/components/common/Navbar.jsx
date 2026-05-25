import { useState } from "react";
import { Link, NavLink } from "react-router-dom";
import { HelpCircle, Menu, X, FileText } from "lucide-react";

import LanguageSwitcher from "./LanguageSwitcher.jsx";
import { useLanguage } from "../../context/LanguageContext.jsx";

const NAV = [
  { to: "/", key: "nav.home" },
  { to: "/market", key: "nav.market" },
  { to: "/pest-warning", key: "nav.pest" },
  { to: "/crop-recommendation", key: "nav.crop" },
  { to: "/analytics", key: "nav.analytics" }
];

export default function Navbar() {
  const { t } = useLanguage();
  const [mobileOpen, setMobileOpen] = useState(false);

  const navClass = ({ isActive }) =>
    `hover:text-gov-primary transition ${
      isActive ? "text-gov-primary border-b-2 border-gov-saffron pb-1" : ""
    }`;

  return (
    <header className="sticky top-0 z-40 border-b border-gov-border bg-white/85 backdrop-blur supports-[backdrop-filter]:bg-white/70">
      <div className="mx-auto max-w-7xl px-4 py-3 flex items-center justify-between gap-4">
        <Link to="/" className="flex items-center gap-3">
          <div className="h-9 w-1 rounded-full bg-gov-saffron" />
          <div className="leading-tight">
            <div className="font-extrabold text-gov-primary">{t("home.hero.title")}</div>
            <div className="text-xs text-slate-600">{t("home.hero.subtitle")}</div>
          </div>
        </Link>

        <nav className="hidden md:flex items-center gap-5 text-sm font-semibold text-slate-700">
          {NAV.map((it) => (
            <NavLink key={it.to} to={it.to} className={navClass}>
              {t(it.key)}
            </NavLink>
          ))}
        </nav>

        <div className="flex items-center gap-2">
          <Link
            to="/terms"
            className="hidden lg:inline-flex items-center gap-1.5 rounded-xl border border-gov-border bg-white px-3 py-2 text-sm font-semibold shadow-soft hover:shadow transition"
            title="Terms & Conditions"
          >
            <FileText className="h-4 w-4 text-gov-primary" />
            {t("nav.terms")}
          </Link>
          <Link
            to="/support"
            className="hidden sm:inline-flex items-center gap-2 rounded-xl border border-gov-border bg-white px-3 py-2 text-sm font-semibold shadow-soft hover:shadow transition"
          >
            <HelpCircle className="h-4 w-4 text-gov-primary" />
            {t("nav.support")}
          </Link>
          <LanguageSwitcher />
          <button
            type="button"
            className="md:hidden inline-flex h-9 w-9 items-center justify-center rounded-lg border border-gov-border bg-white"
            aria-label="Toggle navigation"
            onClick={() => setMobileOpen((v) => !v)}
          >
            {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </div>

      {mobileOpen && (
        <div className="md:hidden border-t border-gov-border bg-white">
          <nav className="px-4 py-3 grid gap-1 text-sm font-semibold text-slate-700">
            {NAV.map((it) => (
              <NavLink
                key={it.to}
                to={it.to}
                onClick={() => setMobileOpen(false)}
                className={({ isActive }) =>
                  `rounded-lg px-3 py-2 ${isActive ? "bg-blue-50 text-gov-primary" : "hover:bg-slate-50"}`
                }
              >
                {t(it.key)}
              </NavLink>
            ))}
            <NavLink to="/support" onClick={() => setMobileOpen(false)} className="rounded-lg px-3 py-2 hover:bg-slate-50">{t("nav.support")}</NavLink>
            <NavLink to="/terms"   onClick={() => setMobileOpen(false)} className="rounded-lg px-3 py-2 hover:bg-slate-50">{t("nav.terms")}</NavLink>
          </nav>
        </div>
      )}
    </header>
  );
}

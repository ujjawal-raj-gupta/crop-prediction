import { NavLink } from "react-router-dom";
import {
  BarChart3, Bell, Bug, FileText, HelpCircle, Home, Settings, Sprout,
  TrendingUp, Activity, Layers, ScrollText
} from "lucide-react";
import { useLanguage } from "../../context/LanguageContext.jsx";

const items = [
  { to: "/", icon: Home, key: "nav.home" },
  { to: "/market", icon: TrendingUp, key: "nav.market" },
  { to: "/pest-warning", icon: Bug, key: "nav.pest" },
  { to: "/crop-recommendation", icon: Sprout, key: "nav.crop" },
  { to: "/analytics", icon: BarChart3, key: "nav.analytics" },
  { to: "/reports", icon: FileText, key: "nav.reports" },
  { to: "/monitoring", icon: Activity, key: "nav.monitoring" },
  { to: "/services", icon: Layers, key: "nav.services" },
  { to: "/alerts", icon: Bell, key: "nav.alerts" },
  { to: "/support", icon: HelpCircle, key: "nav.support" },
  { to: "/settings", icon: Settings, key: "nav.settings" },
  { to: "/terms", icon: ScrollText, key: "nav.terms" }
];

export default function Sidebar() {
  const { t } = useLanguage();

  return (
    <div className="rounded-xl2 bg-white shadow-soft border border-gov-border overflow-hidden">
      <div className="px-4 py-4 border-b border-gov-border">
        <div className="text-sm font-bold text-gov-primary">Navigation</div>
        <div className="text-xs text-slate-600">Citizen portal sections</div>
      </div>
      <nav className="p-2">
        {items.map((it) => (
          <NavLink
            key={it.to}
            to={it.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-semibold transition ${
                isActive ? "bg-blue-50 text-gov-primary" : "text-slate-700 hover:bg-slate-50"
              }`
            }
          >
            <it.icon className="h-4 w-4" />
            {t(it.key)}
          </NavLink>
        ))}
      </nav>
    </div>
  );
}


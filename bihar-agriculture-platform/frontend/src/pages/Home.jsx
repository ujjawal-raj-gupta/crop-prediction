import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";
import { BarChart3, Bug, TrendingUp } from "lucide-react";
import toast from "react-hot-toast";

import { useLanguage } from "../context/LanguageContext.jsx";
import { marketApi } from "../services/api.js";

function Metric({ label, value }) {
  return (
    <div className="rounded-xl2 bg-white/95 border border-gov-border shadow-soft p-5 card-hover">
      <div className="text-[11px] font-bold tracking-wide text-slate-500 uppercase">{label}</div>
      <div className="mt-2 text-3xl font-extrabold text-gov-primary">{value}</div>
    </div>
  );
}

export default function Home() {
  const { t } = useLanguage();

  const { data: crops } = useQuery({
    queryKey: ["crops"],
    queryFn: () => marketApi.crops(),
    staleTime: 60 * 60 * 1000
  });

  return (
    <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
      <section className="rounded-xl2 bg-gradient-to-br from-gov-primary to-gov-navy text-white shadow-soft overflow-hidden">
        <div className="px-6 py-8 md:px-10 md:py-10">
          <div className="inline-flex items-center gap-2 rounded-full bg-white/15 px-3 py-1 text-xs font-semibold">
            Government-grade citizen service portal
          </div>
          <h1 className="mt-3 text-3xl md:text-4xl font-extrabold tracking-tight">{t("home.hero.title")}</h1>
          <p className="mt-2 text-white/90 text-lg">{t("home.hero.subtitle")}</p>
          <p className="mt-2 text-white/80 text-sm font-semibold">
            Hindi rendering: <span className="font-sans">नोटो सैन्स देवनागरी</span>
          </p>

          <div className="mt-6 flex flex-wrap gap-3">
            <button
              className="rounded-xl bg-gov-saffron px-5 py-3 text-slate-900 font-bold shadow-soft hover:brightness-95 transition"
              onClick={() => toast.success("Welcome — portal ready.")}
              type="button"
            >
              Get Started
            </button>
            <button
              className="rounded-xl border border-white/35 bg-white/10 px-5 py-3 font-bold hover:bg-white/15 transition"
              type="button"
            >
              Watch demo
            </button>
          </div>

          <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Metric label="Predictions made" value="10,000+" />
            <Metric label="Farmers served" value="9,500+" />
            <Metric label="Avg. savings" value="₹ 2.5 Cr" />
            <Metric label="Success rate" value="95%" />
          </div>
        </div>
      </section>

      <section className="mt-6 grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Feature
          title={t("nav.market")}
          desc="Price outlooks, mandi comparisons, selling windows."
          icon={<TrendingUp className="h-6 w-6" />}
          href="/market"
        />
        <Feature
          title={t("nav.pest")}
          desc="Early risk detection, weather fusion, advisory treatments."
          icon={<Bug className="h-6 w-6" />}
          href="/pest-warning"
        />
        <Feature
          title={t("nav.analytics")}
          desc="Trends, performance, usage dashboards, exportable insights."
          icon={<BarChart3 className="h-6 w-6" />}
          href="/analytics"
        />
      </section>

      <section className="mt-6 rounded-xl2 bg-white border border-gov-border shadow-soft p-6">
        <div className="font-bold text-slate-900">Platform catalogs</div>
        <div className="text-sm text-slate-600 mt-1">Example: available crops from API</div>
        <div className="mt-4 flex flex-wrap gap-2">
          {(crops?.crops || []).map((c) => (
            <span key={c} className="rounded-full bg-blue-50 text-gov-primary px-3 py-1 text-xs font-bold">
              {c}
            </span>
          ))}
        </div>
      </section>
    </motion.div>
  );
}

function Feature({ title, desc, icon, href }) {
  return (
    <a href={href} className="group rounded-xl2 bg-white border border-gov-border shadow-soft p-6 card-hover block">
      <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-blue-50 to-white text-gov-primary border border-gov-border flex items-center justify-center group-hover:scale-105 transition">{icon}</div>
      <div className="mt-3 font-extrabold text-slate-900">{title}</div>
      <div className="mt-1 text-sm text-slate-600">{desc}</div>
      <div className="mt-4 text-sm font-bold text-gov-primary inline-flex items-center gap-1">
        Open <span aria-hidden="true" className="transition group-hover:translate-x-1">→</span>
      </div>
    </a>
  );
}


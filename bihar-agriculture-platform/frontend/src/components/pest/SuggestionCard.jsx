import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  ChevronDown,
  Eye,
  Shield,
  Leaf,
  FlaskConical,
  Droplets,
  Siren,
  AlertTriangle
} from "lucide-react";

/* ---------- Section metadata (icon + label + urgency flag) -------------- */
const SECTION_META = {
  emergency_actions:   { label: "Emergency action",   Icon: Siren,         urgent: true  },
  symptoms_list:       { label: "Symptoms",           Icon: Eye,           urgent: false },
  prevention:          { label: "Prevention",         Icon: Shield,        urgent: false },
  organic_solutions:   { label: "Organic solutions",  Icon: Leaf,          urgent: false },
  chemical_treatments: { label: "Chemical treatment", Icon: FlaskConical,  urgent: false },
  irrigation_advice:   { label: "Irrigation advice",  Icon: Droplets,      urgent: false }
};

const SEVERITY_STYLES = {
  LOW:    { bar: "bg-emerald-500", pill: "bg-emerald-50 text-emerald-800 border-emerald-200", border: "border-l-emerald-500", track: "bg-emerald-100" },
  MEDIUM: { bar: "bg-amber-500",   pill: "bg-amber-50 text-amber-800 border-amber-200",       border: "border-l-amber-500",   track: "bg-amber-100" },
  HIGH:   { bar: "bg-rose-600",    pill: "bg-rose-50 text-rose-800 border-rose-200",          border: "border-l-rose-600",    track: "bg-rose-100" }
};

/**
 * Reusable expandable pest suggestion card.
 *
 * Props:
 *   - threat: backend threat payload (pest_name, risk_score, risk_level, suggestions, factors, ...)
 *   - sectionsToShow: array of section keys (driven by overall recommendation_set)
 *   - defaultOpen: whether to start expanded (the first card is usually opened by default)
 */
export default function SuggestionCard({ threat, sectionsToShow, defaultOpen = false }) {
  const [open, setOpen] = useState(defaultOpen);
  const sev = SEVERITY_STYLES[threat?.risk_level] || SEVERITY_STYLES.LOW;
  const suggestions = threat?.suggestions || {};
  const factors = threat?.factors || {};

  const visibleSections = (sectionsToShow || Object.keys(SECTION_META)).filter(
    (key) => Array.isArray(suggestions[key]) && suggestions[key].length
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className={`rounded-xl2 bg-white border border-gov-border shadow-soft overflow-hidden border-l-4 ${sev.border}`}
    >
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center gap-3 p-4 md:p-5 text-left hover:bg-gov-bg/60 transition"
        aria-expanded={open}
      >
        <div className="text-2xl leading-none" aria-hidden="true">{threat?.icon || "🐛"}</div>
        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <div className="font-extrabold text-slate-900 truncate">{threat?.pest_name || threat?.pest_key || "Pest"}</div>
            <span className={`rounded-full px-2 py-0.5 text-[11px] font-bold uppercase tracking-wide border ${sev.pill}`}>
              {threat?.risk_level || "—"}
            </span>
            {visibleSections.includes("emergency_actions") && (
              <span className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-bold uppercase bg-rose-100 text-rose-800 border border-rose-200">
                <AlertTriangle className="h-3 w-3" /> Act now
              </span>
            )}
          </div>
          <div className="mt-1 text-xs text-slate-600 truncate">
            {threat?.category && <span className="font-semibold">{threat.category}</span>}
            {threat?.category && threat?.summary ? " · " : ""}
            {threat?.summary}
          </div>
          <div className={`mt-2 h-1.5 rounded-full ${sev.track} overflow-hidden`}>
            <div className={`h-full ${sev.bar}`} style={{ width: `${Math.min(100, threat?.risk_score || 0)}%`, transition: "width .8s cubic-bezier(.2,.8,.2,1)" }} />
          </div>
        </div>
        <div className="text-right">
          <div className="font-extrabold text-slate-900">{threat?.risk_score ?? "—"}</div>
          <div className="text-[10px] tracking-wide text-slate-500 font-semibold">/ 100</div>
        </div>
        <ChevronDown className={`h-5 w-5 text-slate-400 shrink-0 transition-transform ${open ? "rotate-180" : ""}`} />
      </button>

      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            key="body"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25, ease: "easeOut" }}
            className="border-t border-gov-border"
          >
            <div className="p-4 md:p-5 space-y-4">
              <FactorChips factors={factors} />
              {visibleSections.length === 0 ? (
                <div className="text-sm text-slate-600">No additional advisory sections for this pest.</div>
              ) : (
                visibleSections.map((key) => (
                  <Section key={key} sectionKey={key} items={suggestions[key]} severity={threat?.risk_level} />
                ))
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

function Section({ sectionKey, items, severity }) {
  const meta = SECTION_META[sectionKey] || { label: sectionKey, Icon: AlertTriangle, urgent: false };
  const sev = SEVERITY_STYLES[severity] || SEVERITY_STYLES.LOW;
  return (
    <div>
      <div className="flex items-center gap-2 text-[12px] font-extrabold uppercase tracking-wide text-slate-500">
        <meta.Icon className="h-4 w-4" />
        <span>{meta.label}</span>
        {meta.urgent && (
          <span className="ml-1 inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] bg-rose-100 text-rose-800 border border-rose-200 font-bold">
            EMERGENCY
          </span>
        )}
      </div>
      <ul className="mt-2 grid gap-2">
        {items.map((it, idx) => (
          <li key={idx} className="relative rounded-lg bg-slate-50 px-3 py-2 text-sm text-slate-800 leading-snug pl-7">
            <span className={`absolute left-3 top-3 h-2 w-2 rounded-full ${sev.bar}`} aria-hidden="true" />
            {it}
          </li>
        ))}
      </ul>
    </div>
  );
}

function FactorChips({ factors }) {
  const chips = [];
  if (factors?.growth_stage_vulnerable !== undefined) {
    chips.push({ label: `Stage vulnerable: ${factors.growth_stage_vulnerable ? "yes" : "no"}`, active: !!factors.growth_stage_vulnerable });
  }
  if (factors?.humidity_trigger_met !== undefined) {
    chips.push({ label: `Humidity trigger: ${factors.humidity_trigger_met ? "met" : "no"}`, active: !!factors.humidity_trigger_met });
  }
  if (factors?.temp_trigger_met !== undefined) {
    chips.push({ label: `Temp trigger: ${factors.temp_trigger_met ? "met" : "no"}`, active: !!factors.temp_trigger_met });
  }
  if (!chips.length) return null;
  return (
    <div className="flex flex-wrap gap-2">
      {chips.map((c, i) => (
        <span
          key={i}
          className={`text-[11px] font-semibold rounded-full px-2 py-1 border ${
            c.active ? "bg-rose-50 text-rose-800 border-rose-200" : "bg-slate-100 text-slate-700 border-slate-200"
          }`}
        >
          {c.label}
        </span>
      ))}
    </div>
  );
}

import { useMemo, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { motion } from "framer-motion";
import toast from "react-hot-toast";
import Chart from "react-apexcharts";
import { AlertTriangle, Thermometer, Droplets, Bug, Compass } from "lucide-react";

import { pestApi } from "../services/api.js";
import SuggestionCard from "../components/pest/SuggestionCard.jsx";
import TermsGate, { requireTermsOrToast } from "../components/common/TermsGate.jsx";
import { useTermsAcceptance } from "../hooks/useTermsAcceptance.js";

/* ---------- Severity styling tokens (kept local to this page) ----------- */
const TIER_STYLES = {
  LOW:    { bg: "bg-emerald-50",  text: "text-emerald-800", border: "border-emerald-200", color: "#138808" },
  MEDIUM: { bg: "bg-amber-50",    text: "text-amber-800",   border: "border-amber-200",   color: "#FFA500" },
  HIGH:   { bg: "bg-rose-50",     text: "text-rose-800",    border: "border-rose-200",    color: "#DC3545" }
};

const TIER_HEADLINE = {
  LOW:    "Stay watchful; preventive care only",
  MEDIUM: "Plan preventive + curative steps",
  HIGH:   "Immediate action required"
};

const TIER_SUB = {
  LOW:    "Routine scouting is enough — no urgent threats detected.",
  MEDIUM: "Combine prevention with selective organic or chemical control.",
  HIGH:   "Apply highlighted emergency actions within 24-48 hours and coordinate with the helpdesk."
};

export default function PestWarning() {
  const [latitude, setLatitude] = useState(25.5941);
  const [longitude, setLongitude] = useState(85.1376);
  const [crop, setCrop] = useState("rice");
  const [growthStage, setGrowthStage] = useState("tillering");

  const { isAccepted } = useTermsAcceptance();

  const mutation = useMutation({
    mutationFn: () => pestApi.checkRisk({ latitude, longitude, crop, growth_stage: growthStage }),
    onSuccess: () => toast.success("Risk assessed"),
    onError: (e) => toast.error(e.message)
  });

  const data = mutation.data;
  const v = data?.overall_risk ?? 0;
  const tier = data?.risk_level || "LOW";
  const tierStyle = TIER_STYLES[tier] || TIER_STYLES.LOW;
  const threats = data?.threats || [];
  const recommendationSet = data?.recommendation_set || [];

  const submit = () => {
    if (!requireTermsOrToast(isAccepted)) return;
    mutation.mutate();
  };

  const gaugeOptions = useMemo(() => ({
    chart: { type: "radialBar", animations: { enabled: true, speed: 800 } },
    plotOptions: {
      radialBar: {
        startAngle: -135, endAngle: 135,
        hollow: { size: "65%" },
        track: { background: "#F1F5F9", strokeWidth: "100%" },
        dataLabels: {
          name: { fontSize: "13px", color: "#475569" },
          value: { fontSize: "30px", fontWeight: 800, color: "#0F172A" }
        }
      }
    },
    fill: { type: "gradient", gradient: { gradientToColors: [tierStyle.color], stops: [0, 100] } },
    colors: [tierStyle.color],
    labels: ["Overall risk"]
  }), [tierStyle.color]);

  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="grid grid-cols-1 lg:grid-cols-[360px_1fr] gap-6">
      {/* -------- Left rail: form -------- */}
      <aside className="rounded-xl2 bg-white border border-gov-border shadow-soft p-6 self-start lg:sticky lg:top-20">
        <div className="flex items-center gap-2 text-xs font-bold tracking-wide text-slate-500 uppercase">
          <Bug className="h-4 w-4" /> Advisory module
        </div>
        <div className="mt-1 text-xl font-extrabold text-slate-900">Pest warning</div>
        <div className="text-sm text-slate-600 mt-1">Early detection &amp; KB-driven treatment advisory.</div>

        <div className="mt-5 grid grid-cols-2 gap-3">
          <Field label="Latitude">
            <input
              className="w-full rounded-xl border border-gov-border bg-white px-3 py-2 focus:border-gov-primary focus:ring-2 focus:ring-gov-primary/30 outline-none"
              type="number" step="0.0001"
              value={latitude} onChange={(e) => setLatitude(+e.target.value)}
            />
          </Field>
          <Field label="Longitude">
            <input
              className="w-full rounded-xl border border-gov-border bg-white px-3 py-2 focus:border-gov-primary focus:ring-2 focus:ring-gov-primary/30 outline-none"
              type="number" step="0.0001"
              value={longitude} onChange={(e) => setLongitude(+e.target.value)}
            />
          </Field>
        </div>

        <div className="mt-3">
          <Field label="Crop">
            <select className="w-full rounded-xl border border-gov-border px-3 py-2" value={crop} onChange={(e) => setCrop(e.target.value)}>
              <option value="rice">Rice</option>
              <option value="wheat">Wheat</option>
              <option value="mustard">Mustard</option>
              <option value="maize">Maize</option>
              <option value="lentil">Lentil</option>
              <option value="chickpea">Chickpea</option>
              <option value="pigeonpeas">Pigeonpeas</option>
            </select>
          </Field>
        </div>
        <div className="mt-3">
          <Field label="Growth stage">
            <select className="w-full rounded-xl border border-gov-border px-3 py-2" value={growthStage} onChange={(e) => setGrowthStage(e.target.value)}>
              <option value="seedling">Seedling</option>
              <option value="vegetative">Vegetative</option>
              <option value="tillering">Tillering</option>
              <option value="flowering">Flowering</option>
              <option value="panicle_initiation">Panicle initiation</option>
              <option value="pod_formation">Pod formation</option>
              <option value="maturity">Maturity</option>
            </select>
          </Field>
        </div>

        <TermsGate id="pest-terms-gate" />

        <button
          type="button"
          onClick={submit}
          className="mt-4 w-full rounded-xl bg-gov-danger text-white px-4 py-3 font-bold shadow-soft hover:brightness-110 transition disabled:opacity-60"
          disabled={mutation.isPending}
        >
          {mutation.isPending ? "Assessing…" : "Check pest risk"}
        </button>
        <p className="mt-2 text-[11px] text-slate-500 leading-snug">
          Advisory only. For severe outbreaks, contact your nearest Krishi Vigyan Kendra.
        </p>
      </aside>

      {/* -------- Right column: results -------- */}
      <section className="space-y-6 min-w-0">
        {/* Headline result + gauge + weather summary */}
        <div className="rounded-xl2 bg-white border border-gov-border shadow-soft p-6">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <div className="text-xs font-bold tracking-wide text-slate-500 uppercase">Result</div>
              <div className="mt-1 text-xl md:text-2xl font-extrabold text-slate-900">
                {data ? TIER_HEADLINE[tier] : "Run a check to assess risk"}
              </div>
              <div className="text-sm text-slate-600 mt-1">{data ? TIER_SUB[tier] : "Low risk shows preventive tips only. High risk surfaces emergency actions."}</div>
            </div>
            <div className="flex items-center gap-2">
              <span className={`rounded-full px-3 py-1 text-xs font-extrabold border ${tierStyle.bg} ${tierStyle.text} ${tierStyle.border}`}>
                {data?.risk_level || "—"}
              </span>
              <span className="text-sm font-bold text-slate-700">{data ? `${v}/100` : "— / 100"}</span>
            </div>
          </div>

          <div className="mt-4 grid md:grid-cols-[260px_1fr] gap-6 items-center">
            <div>
              <Chart options={gaugeOptions} series={[v]} type="radialBar" height={260} />
            </div>
            <div className="grid gap-3">
              <WeatherTile
                icon={<Thermometer className="h-5 w-5" />}
                label="Avg temperature (3 days)"
                value={data?.weather_forecast?.temp_avg_next_3_days != null ? `${Number(data.weather_forecast.temp_avg_next_3_days).toFixed(1)} °C` : "—"}
              />
              <WeatherTile
                icon={<Droplets className="h-5 w-5" />}
                label="Avg humidity (3 days)"
                value={data?.weather_forecast?.humidity_avg_next_3_days != null ? `${Number(data.weather_forecast.humidity_avg_next_3_days).toFixed(0)} %` : "—"}
              />
              <WeatherTile
                icon={<Compass className="h-5 w-5" />}
                label="Location"
                value={`${latitude.toFixed(3)}, ${longitude.toFixed(3)}`}
              />
            </div>
          </div>

          {data && (
            <div className={`mt-4 rounded-xl border ${tierStyle.border} ${tierStyle.bg} p-4 flex items-start gap-3`}>
              <span className={`mt-1 inline-block h-3 w-3 rounded-full ${tier === "HIGH" ? "bg-rose-500 animate-pulse" : tier === "MEDIUM" ? "bg-amber-500" : "bg-emerald-500"}`} />
              <div>
                <div className={`font-extrabold ${tierStyle.text}`}>{TIER_HEADLINE[tier]}</div>
                <div className="text-sm text-slate-700">{TIER_SUB[tier]}</div>
              </div>
            </div>
          )}
        </div>

        {/* Emergency banner only at HIGH */}
        {tier === "HIGH" && data && (
          <div className="rounded-xl2 border border-rose-200 bg-rose-50 p-5 flex items-start gap-3">
            <AlertTriangle className="h-6 w-6 text-rose-600 mt-0.5" />
            <div className="flex-1">
              <div className="font-extrabold text-rose-900">URGENT — high pest pressure detected</div>
              <div className="text-sm text-rose-800 mt-1">
                Follow the highlighted emergency actions in the cards below within 24-48 hours. Coordinate with neighbours for area-wide effectiveness.
              </div>
            </div>
            <a
              href="tel:+911800XXXXXXXX"
              className="shrink-0 inline-flex items-center justify-center rounded-xl bg-rose-600 text-white px-4 py-2 font-bold shadow-soft hover:brightness-110 transition"
            >
              Call helpdesk
            </a>
          </div>
        )}

        {/* Suggestion cards */}
        <div className="rounded-xl2 bg-white border border-gov-border shadow-soft p-6">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <div>
              <div className="font-extrabold text-slate-900">Recommended actions per pest</div>
              <div className="text-sm text-slate-600 mt-1">Cards expand for full guidance. Severity drives which sections appear.</div>
            </div>
            <div className="text-xs font-semibold text-slate-500">
              {data ? `Risk tier: ${tier} · ${recommendationSet.length} sections shown` : ""}
            </div>
          </div>

          <div className="mt-5 grid gap-3">
            {mutation.isPending && (
              <>
                <SkeletonCard />
                <SkeletonCard />
              </>
            )}
            {!mutation.isPending && !data && (
              <div className="rounded-xl border border-dashed border-gov-border bg-gov-bg p-6 text-center">
                <div className="text-3xl">🌾</div>
                <div className="mt-2 font-extrabold text-slate-900">Awaiting your first check</div>
                <div className="text-sm text-slate-600">Submit the form on the left to see KB-driven suggestions.</div>
              </div>
            )}
            {!mutation.isPending && data && threats.length === 0 && (
              <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-6 text-center">
                <div className="text-3xl">✅</div>
                <div className="mt-2 font-extrabold text-emerald-900">No matched threats</div>
                <div className="text-sm text-emerald-800">No pests in the knowledge base flagged this crop + stage combination.</div>
              </div>
            )}
            {!mutation.isPending && threats.map((threat, i) => (
              <SuggestionCard
                key={threat.pest_key || threat.pest_name || i}
                threat={threat}
                sectionsToShow={recommendationSet}
                defaultOpen={i === 0}
              />
            ))}
          </div>
        </div>

        {/* Sticky mobile action bar */}
        <div className="sticky bottom-0 lg:hidden -mx-4 px-4 py-3 bg-white/90 backdrop-blur border-t border-gov-border flex gap-2">
          <button
            type="button"
            onClick={submit}
            disabled={mutation.isPending}
            className="flex-1 rounded-xl bg-gov-danger text-white px-4 py-3 font-bold shadow-soft disabled:opacity-60"
          >
            {mutation.isPending ? "Assessing…" : "Run risk check"}
          </button>
          <a href="tel:+911800XXXXXXXX" className="rounded-xl border border-gov-border bg-white px-4 py-3 font-bold">Help</a>
        </div>
      </section>
    </motion.div>
  );
}

function Field({ label, children }) {
  return (
    <label className="block">
      <div className="text-xs font-semibold text-slate-600 mb-1">{label}</div>
      {children}
    </label>
  );
}

function WeatherTile({ icon, label, value }) {
  return (
    <div className="rounded-xl border border-gov-border bg-gov-bg p-3 flex items-center gap-3">
      <div className="h-9 w-9 rounded-lg bg-white text-gov-primary border border-gov-border flex items-center justify-center">{icon}</div>
      <div>
        <div className="text-[11px] font-bold tracking-wide text-slate-500 uppercase">{label}</div>
        <div className="font-extrabold text-slate-900">{value}</div>
      </div>
    </div>
  );
}

function SkeletonCard() {
  return (
    <div className="rounded-xl2 bg-white border border-gov-border shadow-soft p-5">
      <div className="h-4 w-32 rounded bg-slate-200 animate-pulse" />
      <div className="mt-3 h-2 w-full rounded bg-slate-200 animate-pulse" />
      <div className="mt-2 h-2 w-2/3 rounded bg-slate-200 animate-pulse" />
    </div>
  );
}

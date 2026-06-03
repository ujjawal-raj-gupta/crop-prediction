import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from "recharts";

import { cropApi } from "../services/api.js";
import TermsGate, { requireTermsOrToast } from "../components/common/TermsGate.jsx";
import { useTermsAcceptance } from "../hooks/useTermsAcceptance.js";

export default function CropRecommendation() {
  const { isAccepted } = useTermsAcceptance();
  const [latitude, setLatitude] = useState(25.5941);
  const [longitude, setLongitude] = useState(85.1376);
  const [n, setN] = useState(90);
  const [p, setP] = useState(42);
  const [k, setK] = useState(43);
  const [ph, setPh] = useState(6.8);
  const [soilType, setSoilType] = useState("alluvial");
  const [season, setSeason] = useState("rabi");

  const mutation = useMutation({
    mutationFn: () =>
      cropApi.recommend({
        latitude,
        longitude,
        soil_npk: { n, p, k },
        soil_type: soilType,
        ph,
        season
      }),
    onSuccess: () => toast.success("Recommendations generated"),
    onError: (e) => toast.error(e.message)
  });

  const recommendations = mutation.data?.recommendations || [];
  const rows = recommendations.map((r) => ({
    name: r.crop,
    confidence: r.confidence
  }));
  const sellable = recommendations.filter((r) => r.market && (r.market.buyer_type || r.market.buyer_location));

  const upgrades = mutation.data?.upgrade_suggestions || [];
  const warnings = mutation.data?.warnings || [];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-[360px_1fr] gap-6">
      <aside className="rounded-xl2 bg-white border border-gov-border shadow-soft p-6">
        <div className="font-bold text-slate-900">Crop recommendation</div>
        <div className="text-sm text-slate-600 mt-1">Soil & zone aligned decision support</div>

        <div className="mt-5 space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <Field label="Lat">
              <input className="w-full rounded-xl border border-gov-border px-3 py-2" value={latitude} onChange={(e) => setLatitude(+e.target.value)} />
            </Field>
            <Field label="Lon">
              <input className="w-full rounded-xl border border-gov-border px-3 py-2" value={longitude} onChange={(e) => setLongitude(+e.target.value)} />
            </Field>
          </div>

          <Field label="Nitrogen (N)">
            <input className="w-full" type="range" min="0" max="200" value={n} onChange={(e) => setN(+e.target.value)} />
            <div className="text-xs text-slate-600 font-semibold mt-1">{n} kg/ha</div>
          </Field>
          <Field label="Phosphorus (P)">
            <input className="w-full" type="range" min="0" max="120" value={p} onChange={(e) => setP(+e.target.value)} />
            <div className="text-xs text-slate-600 font-semibold mt-1">{p} kg/ha</div>
          </Field>
          <Field label="Potassium (K)">
            <input className="w-full" type="range" min="0" max="120" value={k} onChange={(e) => setK(+e.target.value)} />
            <div className="text-xs text-slate-600 font-semibold mt-1">{k} kg/ha</div>
          </Field>

          <Field label="pH">
            <input className="w-full rounded-xl border border-gov-border px-3 py-2" type="number" step="0.1" value={ph} onChange={(e) => setPh(+e.target.value)} />
          </Field>

          <Field label="Soil type">
            <select className="w-full rounded-xl border border-gov-border px-3 py-2" value={soilType} onChange={(e) => setSoilType(e.target.value)}>
              <option value="alluvial">Alluvial</option>
              <option value="loamy">Loamy</option>
              <option value="clay">Clay</option>
              <option value="sandy">Sandy</option>
            </select>
          </Field>

          <Field label="Season">
            <select className="w-full rounded-xl border border-gov-border px-3 py-2" value={season} onChange={(e) => setSeason(e.target.value)}>
              <option value="rabi">Rabi</option>
              <option value="kharif">Kharif</option>
              <option value="zaid">Zaid</option>
            </select>
          </Field>

          <TermsGate id="crop-terms-gate" />

          <button
            type="button"
            onClick={() => {
              if (!requireTermsOrToast(isAccepted)) return;
              mutation.mutate();
            }}
            className="w-full rounded-xl bg-gov-success text-white px-4 py-3 font-bold shadow-soft hover:brightness-110 transition disabled:opacity-60"
            disabled={mutation.isPending}
          >
            {mutation.isPending ? "Analyzing…" : "Get Recommendations"}
          </button>
        </div>
      </aside>

      <section className="space-y-6">
        <div className="rounded-xl2 bg-white border border-gov-border shadow-soft p-6">
          <div className="font-bold text-slate-900">Zone & characteristics</div>
          <div className="text-sm text-slate-600 mt-1">
            {mutation.data?.zone ? (
              <>
                Zone: <span className="font-bold text-gov-primary">{mutation.data.zone}</span> · Flood risk:{" "}
                <span className="font-bold">{mutation.data.zone_characteristics?.flood_risk}</span>
              </>
            ) : (
              "Run recommendations to detect zone."
            )}
          </div>
        </div>

        {warnings.length > 0 && (
          <div className="rounded-xl2 bg-amber-50 border border-amber-300 shadow-soft p-6">
            <div className="font-bold text-amber-800">Please check your soil values</div>
            <ul className="mt-2 text-sm text-amber-900 list-disc pl-5 space-y-1">
              {warnings.map((w, i) => (
                <li key={i}>{w}</li>
              ))}
            </ul>
          </div>
        )}

        <div className="rounded-xl2 bg-white border border-gov-border shadow-soft p-6">
          <div className="font-bold text-slate-900">Suitability scores</div>
          <div className="text-sm text-slate-600 mt-1">Top crops by confidence</div>
          <div className="mt-4 h-[340px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={rows} layout="vertical" margin={{ left: 24 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis type="number" domain={[0, 100]} tick={{ fill: "#64748b", fontSize: 12 }} />
                <YAxis type="category" dataKey="name" tick={{ fill: "#64748b", fontSize: 12 }} width={110} />
                <Tooltip formatter={(v) => `${v}%`} />
                <Bar dataKey="confidence" fill="#138808" radius={[8, 8, 8, 8]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {sellable.length > 0 && (
          <div className="rounded-xl2 bg-white border border-gov-border shadow-soft p-6">
            <div className="font-bold text-slate-900">Where to sell your produce</div>
            <div className="text-sm text-slate-600 mt-1">
              Suggested buyers and markets for each recommended crop.
            </div>
            <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-3">
              {sellable.map((r) => (
                <div key={r.crop} className="rounded-xl border border-gov-border p-4">
                  <div className="flex items-center justify-between">
                    <div className="font-bold text-slate-900 capitalize">{r.crop}</div>
                    <DemandBadge level={r.market.demand_level} />
                  </div>
                  <div className="text-xs font-bold tracking-wide text-emerald-700 uppercase mt-3">Where to sell</div>
                  <div className="text-sm font-semibold text-slate-800 mt-1">{r.market.buyer_type || "Local buyers"}</div>
                  <div className="text-sm text-slate-600">{r.market.buyer_location}</div>
                  {r.market.price_per_kg && (
                    <div className="text-xs text-slate-600 mt-2 flex justify-between">
                      <span>Price/kg</span>
                      <span className="font-semibold text-slate-800">Rs {r.market.price_per_kg}</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {upgrades.length > 0 && (
          <div className="rounded-xl2 bg-white border border-gov-border shadow-soft p-6">
            <div className="font-bold text-slate-900">Unlock more crops by improving your soil</div>
            <div className="text-sm text-slate-600 mt-1">
              High-value crops your soil is almost ready for - each is short by just one fixable factor.
            </div>
            <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-3">
              {upgrades.map((s) => (
                <div key={s.crop} className="rounded-xl border border-gov-border p-4">
                  <div className="flex items-center justify-between">
                    <div className="font-bold text-slate-900 capitalize">{s.crop}</div>
                    <DemandBadge level={s.demand_level} />
                  </div>
                  <div className="text-xs text-slate-600 mt-2 flex justify-between">
                    <span>Price/kg</span>
                    <span className="font-semibold text-slate-800">{s.price_per_kg}</span>
                  </div>
                  <div className="text-xs text-slate-600 mt-1 flex justify-between">
                    <span>{s.blocking_param} now</span>
                    <span className="font-semibold text-slate-800">
                      {s.current_value} → target ~{s.target_value}
                    </span>
                  </div>
                  <div className="text-sm text-slate-700 mt-2">{s.action_text}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </section>
    </div>
  );
}

function DemandBadge({ level }) {
  const l = String(level || "").toLowerCase();
  const cls =
    l === "high"
      ? "bg-green-100 text-green-700"
      : l === "medium"
      ? "bg-amber-100 text-amber-700"
      : l === "low"
      ? "bg-red-100 text-red-700"
      : "bg-slate-100 text-slate-600";
  return (
    <span className={`text-xs font-semibold px-2 py-1 rounded-full ${cls}`}>
      {level || "N/A"} demand
    </span>
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


import { useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { ResponsiveContainer, LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, Area } from "recharts";

import { marketApi } from "../services/api.js";
import { useLanguage } from "../context/LanguageContext.jsx";

export default function MarketIntelligence() {
  const { t } = useLanguage();
  const [crop, setCrop] = useState("Wheat");
  const [mandi, setMandi] = useState("Patna");
  const [quantity, setQuantity] = useState(12);

  const { data: crops } = useQuery({ queryKey: ["market", "crops"], queryFn: () => marketApi.crops() });
  const { data: mandis } = useQuery({ queryKey: ["market", "mandis"], queryFn: () => marketApi.mandis() });

  const mutation = useMutation({
    mutationFn: () => marketApi.predict({ crop, mandi, quantity }),
    onSuccess: () => toast.success("Forecast generated"),
    onError: (e) => toast.error(e.message)
  });

  const chartData = useMemo(() => mutation.data?.predicted_prices || [], [mutation.data]);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-[360px_1fr] gap-6">
      <aside className="rounded-xl2 bg-white border border-gov-border shadow-soft p-6">
        <div className="font-bold text-slate-900">{t("nav.market")}</div>
        <div className="text-sm text-slate-600 mt-1">Price outlook & selling recommendation</div>

        <div className="mt-5 space-y-4">
          <Field label="Crop">
            <select className="w-full rounded-xl border border-gov-border px-3 py-2" value={crop} onChange={(e) => setCrop(e.target.value)}>
              {(crops?.crops || []).map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Mandi">
            <select className="w-full rounded-xl border border-gov-border px-3 py-2" value={mandi} onChange={(e) => setMandi(e.target.value)}>
              {(mandis?.mandis || []).map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Quantity (quintals)">
            <input className="w-full rounded-xl border border-gov-border px-3 py-2" type="number" value={quantity} onChange={(e) => setQuantity(+e.target.value)} />
          </Field>
          <button
            type="button"
            onClick={() => mutation.mutate()}
            className="w-full rounded-xl bg-gov-primary text-white px-4 py-3 font-bold shadow-soft hover:brightness-110 transition"
            disabled={mutation.isPending}
          >
            {mutation.isPending ? "Analyzing…" : "Get Price Prediction"}
          </button>
        </div>
      </aside>

      <section className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Kpi label="Current Price" value={mutation.data ? `₹ ${mutation.data.current_price}` : "—"} />
          <Kpi label="Predicted (30 days)" value={mutation.data ? `₹ ${chartData.at(-1)?.price ?? "—"}` : "—"} />
          <Kpi label="Best selling window" value={mutation.data ? mutation.data.recommendation?.optimal_date ?? "—" : "—"} />
          <Kpi label="Expected gain" value={mutation.data ? `${mutation.data.recommendation?.expected_gain_percent ?? "—"}%` : "—"} />
        </div>

        <div className="rounded-xl2 bg-white border border-gov-border shadow-soft p-6">
          <div className="font-bold text-slate-900">30-day price forecast</div>
          <div className="text-sm text-slate-600 mt-1">Line + confidence band (demo)</div>
          <div className="mt-4 h-[340px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis dataKey="date" tick={{ fontSize: 12, fill: "#64748b" }} />
                <YAxis tick={{ fontSize: 12, fill: "#64748b" }} />
                <Tooltip formatter={(v) => `₹${Number(v).toLocaleString("en-IN")}`} />
                <Area dataKey="confidence_high" stroke="transparent" fill="rgba(19,136,8,0.12)" />
                <Line type="monotone" dataKey="price" stroke="#003087" strokeWidth={3} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>
    </div>
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

function Kpi({ label, value }) {
  return (
    <div className="rounded-xl2 bg-white border border-gov-border shadow-soft p-5">
      <div className="text-xs font-semibold text-slate-600">{label}</div>
      <div className="mt-2 text-xl font-extrabold text-gov-primary">{value}</div>
    </div>
  );
}


import { motion } from "framer-motion";
import toast from "react-hot-toast";
import { CheckCircle, RotateCcw, FileText } from "lucide-react";

import { useTermsAcceptance } from "../hooks/useTermsAcceptance.js";

const SECTIONS = [
  {
    title: "1. Platform usage disclaimer",
    body: 'Bihar Agriculture 4.0 ("the platform") is a citizen advisory portal operated by the Government of Bihar Agriculture Department. The platform may be modified, suspended, or discontinued without prior notice. Use of any feature constitutes acceptance of these terms.'
  },
  {
    title: "2. Agricultural advisory limitation",
    body: "Crop recommendations, pest warnings, irrigation suggestions, and market forecasts are indicative only and based on user-supplied data plus public feeds. Field conditions vary widely — always validate with your local Krishi Vigyan Kendra (KVK) or block agriculture officer before acting at scale."
  },
  {
    title: "3. Weather data disclaimer",
    body: "Weather information is sourced from third-party providers (Open-Meteo). Forecasts beyond 72 hours are inherently uncertain. The platform makes no guarantee about temperature, humidity, or rainfall accuracy and is not liable for crop losses attributable to weather deviation."
  },
  {
    title: "4. Market prediction disclaimer",
    body: "Mandi price forecasts are estimated from historical Agmarknet data and demonstration models. Actual market prices depend on national policy, MSP, weather, transport costs and demand cycles. Forecasts must not be treated as investment advice or selling guarantees."
  },
  {
    title: "5. Pest prediction disclaimer",
    body: "Pest risk scores combine knowledge-base triggers with weather signals. The platform may produce false-positives or false-negatives. Final treatment decisions — especially chemical pesticide use — must follow label directions, withholding periods, and the advice of registered agronomists."
  },
  {
    title: "6. User responsibility",
    list: [
      "Provide accurate information about location, crop, and growth stage.",
      "Verify chemical product names and dosages with local dealers before purchase.",
      "Follow safety protocols (PPE, spray timing, water sources) during pest treatment.",
      "Do not use the platform for commercial resale of advisory content without written approval."
    ]
  },
  {
    title: "7. Data & privacy notice",
    body: "The platform records anonymised usage metrics, support tickets, and pest alert events to improve the service. Personal information (phone, email) provided in support tickets is used only to respond to your request and is not shared with third parties outside the Agriculture Department workflow."
  },
  {
    title: "8. Support limitation",
    body: "The helpdesk operates Monday–Saturday, 10:00–17:00 IST (excluding public holidays). Tickets are acknowledged within 24 office hours. Critical issues should additionally be reported by phone (1800-XXX-XXXX)."
  },
  {
    title: "9. Third-party API disclaimer",
    body: "The platform integrates with public APIs (data.gov.in Agmarknet, Open-Meteo). Outages, rate limits, or changes in those services may impair platform functionality. The platform takes no responsibility for third-party data accuracy."
  },
  {
    title: "10. Limitation of liability",
    body: "To the maximum extent permitted by law, the Government of Bihar, the Agriculture Department, and their officers shall not be liable for any direct, indirect, incidental, or consequential damages arising from the use of, or reliance on, the platform's advisories."
  },
  {
    title: "11. Changes to these terms",
    body: 'These terms may be updated periodically. Material changes will be announced on the homepage and via a fresh acceptance prompt. The "last updated" date below indicates the current revision.'
  }
];

export default function Terms() {
  const { isAccepted, acceptedAt, accept, reset } = useTermsAcceptance();

  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="max-w-4xl">
      <div className="text-xs font-bold tracking-wide text-slate-500 uppercase flex items-center gap-2">
        <FileText className="h-4 w-4" /> Legal & policy
      </div>
      <h1 className="mt-1 text-3xl md:text-4xl font-extrabold text-slate-900">Terms &amp; Conditions</h1>
      <p className="mt-2 text-slate-600 max-w-3xl">
        Please read these terms before using Bihar Agriculture 4.0 services. The platform is intended as
        <strong className="text-slate-900"> advisory only</strong> and does not replace professional or government extension services.
      </p>

      <div className="mt-6 rounded-xl2 bg-white border border-gov-border shadow-soft p-6 md:p-8">
        <article className="space-y-5">
          {SECTIONS.map((s) => (
            <section key={s.title}>
              <h2 className="text-base font-extrabold text-slate-900">{s.title}</h2>
              {s.body && <p className="mt-1 text-slate-700 leading-relaxed">{s.body}</p>}
              {s.list && (
                <ul className="mt-2 list-disc pl-5 space-y-1 text-slate-700">
                  {s.list.map((it) => (
                    <li key={it}>{it}</li>
                  ))}
                </ul>
              )}
            </section>
          ))}
          <div className="text-sm text-slate-600 pt-3 border-t border-gov-border">
            <strong className="text-slate-900">Last updated:</strong> 21 May 2026 &middot; <strong>Version:</strong> 1.0
          </div>
        </article>
      </div>

      <div className="mt-6 rounded-xl2 bg-white border border-gov-border shadow-soft p-6">
        <div className="font-bold text-slate-900">Acceptance</div>
        <div className="text-sm text-slate-600 mt-1">
          Acceptance is recorded on this device only. Click reset if you change your mind.
        </div>

        <div className="mt-4 flex items-center gap-3 flex-wrap">
          {isAccepted ? (
            <span className="inline-flex items-center gap-2 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200 px-3 py-1 text-sm font-bold">
              <CheckCircle className="h-4 w-4" /> Accepted{acceptedAt ? ` · ${new Date(acceptedAt).toLocaleString()}` : ""}
            </span>
          ) : (
            <span className="inline-flex items-center gap-2 rounded-full bg-amber-50 text-amber-800 border border-amber-200 px-3 py-1 text-sm font-bold">
              Not accepted
            </span>
          )}

          {!isAccepted && (
            <button
              type="button"
              onClick={() => {
                accept();
                toast.success("Acceptance saved on this device");
              }}
              className="rounded-xl bg-gov-primary text-white px-4 py-2 font-bold shadow-soft hover:brightness-110 transition"
            >
              I agree
            </button>
          )}
          {isAccepted && (
            <button
              type="button"
              onClick={() => {
                reset();
                toast("Acceptance cleared");
              }}
              className="inline-flex items-center gap-2 rounded-xl border border-gov-border bg-white px-4 py-2 font-bold hover:bg-gov-bg transition"
            >
              <RotateCcw className="h-4 w-4" /> Reset
            </button>
          )}
        </div>
      </div>
    </motion.div>
  );
}

import { Link } from "react-router-dom";
import toast from "react-hot-toast";
import { CheckCircle, AlertCircle, FileText, Languages, Bell, MapPin } from "lucide-react";

import { useLanguage } from "../context/LanguageContext.jsx";
import { useTermsAcceptance } from "../hooks/useTermsAcceptance.js";

export default function Settings() {
  const { language, toggleLanguage } = useLanguage();
  const { isAccepted, acceptedAt, reset } = useTermsAcceptance();

  return (
    <div className="space-y-6">
      <div className="rounded-xl2 bg-white border border-gov-border shadow-soft p-6">
        <div className="text-xs font-bold tracking-wide text-slate-500 uppercase">Profile &amp; preferences</div>
        <h1 className="mt-1 text-2xl md:text-3xl font-extrabold text-slate-900">Settings</h1>
        <p className="mt-1 text-sm text-slate-600">Manage language, notifications, default location, and policy acceptance.</p>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <SettingCard
          title="Language"
          subtitle={language === "en" ? "Currently: English" : "वर्तमान: हिंदी"}
          icon={<Languages className="h-5 w-5" />}
          action={
            <button
              type="button"
              onClick={toggleLanguage}
              className="rounded-xl bg-gov-primary text-white px-4 py-2 font-bold shadow-soft hover:brightness-110 transition"
            >
              Toggle EN / हिं
            </button>
          }
        />

        <SettingCard
          title="Notifications"
          subtitle="SMS / WhatsApp alerts — coming soon"
          icon={<Bell className="h-5 w-5" />}
          action={<span className="text-xs font-bold text-slate-500">Pilot phase</span>}
        />

        <SettingCard
          title="Default location"
          subtitle="Patna, Bihar (25.5941, 85.1376)"
          icon={<MapPin className="h-5 w-5" />}
          action={<span className="text-xs font-bold text-slate-500">Editable soon</span>}
        />

        <SettingCard
          title="Terms &amp; Conditions"
          subtitle={isAccepted ? `Accepted ${acceptedAt ? `on ${new Date(acceptedAt).toLocaleString()}` : ""}` : "Not yet accepted"}
          icon={<FileText className="h-5 w-5" />}
          extra={
            isAccepted ? (
              <span className="inline-flex items-center gap-1.5 text-emerald-700 text-xs font-bold">
                <CheckCircle className="h-4 w-4" /> Active
              </span>
            ) : (
              <span className="inline-flex items-center gap-1.5 text-amber-700 text-xs font-bold">
                <AlertCircle className="h-4 w-4" /> Pending
              </span>
            )
          }
          action={
            <div className="flex gap-2">
              <Link
                to="/terms"
                className="inline-flex rounded-xl bg-gov-primary text-white px-3 py-2 text-sm font-bold shadow-soft hover:brightness-110 transition"
              >
                View terms
              </Link>
              {isAccepted && (
                <button
                  type="button"
                  onClick={() => {
                    reset();
                    toast("Acceptance reset");
                  }}
                  className="inline-flex rounded-xl border border-gov-border bg-white px-3 py-2 text-sm font-bold hover:bg-gov-bg"
                >
                  Reset
                </button>
              )}
            </div>
          }
        />
      </div>
    </div>
  );
}

function SettingCard({ title, subtitle, icon, action, extra }) {
  return (
    <div className="rounded-xl2 bg-white border border-gov-border shadow-soft p-5">
      <div className="flex items-start gap-3">
        <div className="h-10 w-10 rounded-xl bg-blue-50 text-gov-primary flex items-center justify-center">{icon}</div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2 flex-wrap">
            <div className="font-extrabold text-slate-900">{title}</div>
            {extra}
          </div>
          <div className="text-sm text-slate-600 mt-1">{subtitle}</div>
          <div className="mt-3">{action}</div>
        </div>
      </div>
    </div>
  );
}

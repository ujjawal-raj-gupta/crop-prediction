import { useMemo, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { HelpCircle, X, Phone, Mail, MessageCircle, FileText } from "lucide-react";
import { Link } from "react-router-dom";

import { useLanguage } from "../../context/LanguageContext.jsx";

export default function SupportWidget() {
  const [open, setOpen] = useState(false);
  const { t } = useLanguage();

  const waLink = useMemo(
    () =>
      "https://wa.me/918000001234?text=" +
      encodeURIComponent("Hello, I need help with Bihar Agriculture 4.0 platform"),
    []
  );

  return (
    <>
      <motion.button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="fixed bottom-6 right-6 z-50 rounded-full bg-gov-primary text-white shadow-soft px-4 py-4 hover:brightness-110 transition"
        whileHover={{ scale: 1.06 }}
        whileTap={{ scale: 0.95 }}
        aria-label="Open support"
      >
        {open ? <X className="h-6 w-6" /> : <HelpCircle className="h-6 w-6" />}
      </motion.button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, x: 320 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 320 }}
            transition={{ type: "spring", damping: 28 }}
            className="fixed bottom-24 right-6 z-40 w-[min(420px,92vw)] rounded-xl2 border border-gov-border bg-white shadow-soft overflow-hidden"
          >
            <div className="bg-gradient-to-r from-gov-primary to-gov-navy text-white p-4">
              <div className="text-lg font-bold">{t("support.title")}</div>
              <div className="text-sm opacity-90">{t("support.subtitle")}</div>
            </div>

            <div className="p-4 space-y-3">
              <Action
                icon={<Phone className="h-5 w-5" />}
                title="Toll-free helpline"
                subtitle="1800-XXX-XXXX (Mon–Sat 9 AM – 6 PM IST)"
                onClick={() => (window.location.href = "tel:+911800XXXXXXXX")}
              />
              <Action
                icon={<MessageCircle className="h-5 w-5" />}
                title="WhatsApp support"
                subtitle="+91-80000-1234 (template message)"
                onClick={() => window.open(waLink, "_blank")}
              />
              <Action
                icon={<Mail className="h-5 w-5" />}
                title="Email support"
                subtitle="support@biharagri.gov.in"
                onClick={() =>
                  (window.location.href =
                    "mailto:support@biharagri.gov.in?subject=" +
                    encodeURIComponent("Bihar Agriculture 4.0 Support"))
                }
              />
              <Link
                to="/faq"
                className="w-full flex items-center gap-3 p-3 rounded-xl border border-gov-border bg-gov-bg hover:bg-white transition"
                onClick={() => setOpen(false)}
              >
                <div className="text-gov-primary">
                  <FileText className="h-5 w-5" />
                </div>
                <div className="text-left">
                  <div className="font-semibold text-slate-900">FAQ</div>
                  <div className="text-xs text-slate-600">Search common questions</div>
                </div>
              </Link>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}

function Action({ icon, title, subtitle, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="w-full flex items-center gap-3 p-3 rounded-xl border border-gov-border bg-gov-bg hover:bg-white transition"
    >
      <div className="text-gov-primary">{icon}</div>
      <div className="text-left">
        <div className="font-semibold text-slate-900">{title}</div>
        <div className="text-xs text-slate-600">{subtitle}</div>
      </div>
    </button>
  );
}


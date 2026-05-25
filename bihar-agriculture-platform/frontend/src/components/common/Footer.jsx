import { Link } from "react-router-dom";
import { Phone, Mail, FileText } from "lucide-react";

export default function Footer() {
  return (
    <footer className="mt-10 border-t border-gov-border bg-white">
      <div className="mx-auto max-w-7xl px-4 py-8 grid gap-6 md:grid-cols-[2fr_1fr_1fr_1fr]">
        <div>
          <div className="flex items-center gap-2">
            <div className="h-7 w-1 rounded-full bg-gov-saffron" />
            <div>
              <div className="font-extrabold text-slate-900">Bihar Agriculture 4.0</div>
              <div className="text-xs text-slate-600">Government-grade citizen advisory platform</div>
            </div>
          </div>
          <p className="mt-3 text-sm text-slate-600 max-w-md leading-relaxed">
            A pilot portal combining ML-driven crop advisory, mandi price intelligence, and stage-aware pest warnings.
            Advisory only - always validate with your local Krishi Vigyan Kendra.
          </p>
        </div>

        <div>
          <div className="text-xs font-bold tracking-wide text-slate-500 uppercase">Services</div>
          <ul className="mt-3 space-y-2 text-sm">
            <li><Link to="/market"   className="text-slate-700 hover:text-gov-primary font-semibold">Market intelligence</Link></li>
            <li><Link to="/pest-warning" className="text-slate-700 hover:text-gov-primary font-semibold">Pest warning</Link></li>
            <li><Link to="/crop-recommendation" className="text-slate-700 hover:text-gov-primary font-semibold">Crop recommendation</Link></li>
            <li><Link to="/analytics" className="text-slate-700 hover:text-gov-primary font-semibold">Analytics</Link></li>
          </ul>
        </div>

        <div>
          <div className="text-xs font-bold tracking-wide text-slate-500 uppercase">Legal</div>
          <ul className="mt-3 space-y-2 text-sm">
            <li><Link to="/terms"    className="inline-flex items-center gap-1.5 text-slate-700 hover:text-gov-primary font-semibold"><FileText className="h-3.5 w-3.5" /> Terms &amp; Conditions</Link></li>
            <li><Link to="/contact"  className="text-slate-700 hover:text-gov-primary font-semibold">Contact</Link></li>
            <li><Link to="/faq"      className="text-slate-700 hover:text-gov-primary font-semibold">FAQ</Link></li>
          </ul>
        </div>

        <div>
          <div className="text-xs font-bold tracking-wide text-slate-500 uppercase">Helpdesk</div>
          <ul className="mt-3 space-y-2 text-sm">
            <li className="inline-flex items-center gap-1.5 text-slate-700"><Phone className="h-3.5 w-3.5 text-gov-primary" /> 1800-XXX-XXXX</li>
            <li className="inline-flex items-center gap-1.5 text-slate-700"><Mail  className="h-3.5 w-3.5 text-gov-primary" /> support@biharagri.gov.in</li>
            <li className="text-xs text-slate-500">Mon-Sat &middot; 9 AM - 6 PM IST</li>
          </ul>
        </div>
      </div>

      <div className="border-t border-gov-border bg-gov-bg">
        <div className="mx-auto max-w-7xl px-4 py-3 flex flex-col md:flex-row items-center justify-between gap-2 text-xs text-slate-600">
          <div>© 2026 Government of Bihar &middot; Agriculture Department</div>
          <div className="flex items-center gap-4">
            <Link to="/terms" className="hover:text-slate-900 font-semibold">Terms</Link>
            <Link to="/contact" className="hover:text-slate-900 font-semibold">Contact</Link>
            <Link to="/support" className="hover:text-slate-900 font-semibold">Support</Link>
          </div>
        </div>
      </div>
    </footer>
  );
}

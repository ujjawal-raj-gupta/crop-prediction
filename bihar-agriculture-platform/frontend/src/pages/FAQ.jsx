import { Link } from "react-router-dom";

export default function FAQ() {
  return (
    <div className="rounded-xl2 bg-white border border-gov-border shadow-soft p-6">
      <div className="font-bold text-slate-900">FAQ</div>
      <div className="text-sm text-slate-600 mt-1">Dedicated FAQ experience (search + categories next).</div>
      <div className="mt-4">
        <Link className="font-bold text-gov-primary" to="/support">
          Go to Support →
        </Link>
      </div>
    </div>
  );
}


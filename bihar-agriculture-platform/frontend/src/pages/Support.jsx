import { useMutation, useQuery } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import toast from "react-hot-toast";

import { supportApi } from "../services/api.js";
import TermsGate, { requireTermsOrToast } from "../components/common/TermsGate.jsx";
import { useTermsAcceptance } from "../hooks/useTermsAcceptance.js";

export default function Support() {
  const { data } = useQuery({ queryKey: ["support", "faqs"], queryFn: () => supportApi.faqs() });
  const { register, handleSubmit, formState } = useForm();
  const { isAccepted } = useTermsAcceptance();

  const mutation = useMutation({
    mutationFn: async (payload) => {
      const fd = new FormData();
      fd.append("name", payload.name);
      fd.append("email", payload.email || "");
      fd.append("phone", payload.phone);
      fd.append("category", payload.category);
      fd.append("description", payload.description);
      if (payload.attachment?.[0]) fd.append("attachment", payload.attachment[0]);
      return supportApi.createTicket(fd);
    },
    onSuccess: (r) => toast.success(`Ticket created: ${r.ticket_number}`),
    onError: (e) => toast.error(e.message)
  });

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <section className="rounded-xl2 bg-white border border-gov-border shadow-soft p-6">
        <div className="font-bold text-slate-900">Help center</div>
        <div className="text-sm text-slate-600 mt-1">Search FAQs and common topics</div>
        <div className="mt-4 space-y-3">
          {(data?.faqs || []).map((f, idx) => (
            <details key={idx} className="rounded-xl border border-gov-border bg-gov-bg p-4">
              <summary className="cursor-pointer font-semibold text-slate-900">{f.q}</summary>
              <div className="mt-2 text-sm text-slate-700">{f.a}</div>
            </details>
          ))}
        </div>
      </section>

      <section className="rounded-xl2 bg-white border border-gov-border shadow-soft p-6">
        <div className="font-bold text-slate-900">Submit a ticket</div>
        <div className="text-sm text-slate-600 mt-1">We respond within 24 office hours</div>

        <form
          className="mt-5 space-y-4"
          onSubmit={handleSubmit((v) => {
            if (!requireTermsOrToast(isAccepted)) return;
            mutation.mutate(v);
          })}
        >
          <Field label="Name">
            <input className="w-full rounded-xl border border-gov-border px-3 py-2" {...register("name", { required: true })} />
          </Field>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Field label="Phone">
              <input className="w-full rounded-xl border border-gov-border px-3 py-2" {...register("phone", { required: true })} />
            </Field>
            <Field label="Email (optional)">
              <input className="w-full rounded-xl border border-gov-border px-3 py-2" type="email" {...register("email")} />
            </Field>
          </div>
          <Field label="Category">
            <select className="w-full rounded-xl border border-gov-border px-3 py-2" {...register("category", { required: true })}>
              <option>Technical</option>
              <option>Price Prediction</option>
              <option>Pest Alert</option>
              <option>Crop Recommendation</option>
              <option>Other</option>
            </select>
          </Field>
          <Field label="Description">
            <textarea className="w-full rounded-xl border border-gov-border px-3 py-2" rows={4} {...register("description", { required: true })} />
          </Field>
          <Field label="Attachment (optional)">
            <input className="w-full" type="file" {...register("attachment")} />
          </Field>

          <TermsGate id="support-terms-gate" />

          <button
            type="submit"
            className="w-full rounded-xl bg-gov-primary text-white px-4 py-3 font-bold shadow-soft hover:brightness-110 transition disabled:opacity-60"
            disabled={mutation.isPending || formState.isSubmitting}
          >
            {mutation.isPending ? "Submitting…" : "Submit"}
          </button>
        </form>
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


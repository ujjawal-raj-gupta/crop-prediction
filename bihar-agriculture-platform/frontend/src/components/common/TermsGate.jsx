import { useState } from "react";
import { Link } from "react-router-dom";
import toast from "react-hot-toast";

import { useTermsAcceptance } from "../../hooks/useTermsAcceptance.js";

/**
 * Inline "I agree to Terms" gate. Render before submit-style buttons.
 *
 * Props:
 *   - onAccept (optional): callback fired after the user ticks the box.
 *
 * Usage:
 *   const { gateOk, GateNode } = TermsGate.use();
 *   <GateNode />
 *   <button onClick={() => { if (!gateOk()) return; ...submit }}>Submit</button>
 *
 * Or use the simpler component form (renders nothing if already accepted):
 *   <TermsGate />
 */
export default function TermsGate({ id, label }) {
  const { isAccepted, accept } = useTermsAcceptance();
  const [checked, setChecked] = useState(false);

  if (isAccepted) return null;

  const onChange = (e) => {
    const next = e.target.checked;
    setChecked(next);
    if (next) accept();
  };

  return (
    <label
      htmlFor={id || "terms-gate"}
      className="mt-2 flex items-start gap-3 cursor-pointer rounded-xl border border-gov-border bg-gov-bg p-3 hover:bg-white transition"
    >
      <input
        id={id || "terms-gate"}
        type="checkbox"
        checked={checked}
        onChange={onChange}
        className="mt-0.5 h-5 w-5 rounded border-slate-300 text-gov-primary focus:ring-2 focus:ring-gov-primary"
      />
      <span className="text-xs text-slate-700 leading-snug">
        {label || (
          <>
            I agree to the{" "}
            <Link to="/terms" className="font-semibold text-gov-primary underline" target="_blank" rel="noopener">
              Terms &amp; Conditions
            </Link>{" "}
            and the privacy notice. Required to use this advisory.
          </>
        )}
      </span>
    </label>
  );
}

/**
 * Imperative variant: useful when the submit handler needs to enforce
 * acceptance and toast a warning if the user hasn't ticked the box.
 */
export function requireTermsOrToast(isAccepted) {
  if (isAccepted) return true;
  toast.error("Please accept the Terms & Conditions to continue");
  return false;
}

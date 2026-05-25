import { useCallback, useEffect, useState } from "react";

/**
 * Single source of truth for "did the user accept the Terms & Conditions?".
 * Acceptance is persisted in localStorage under "bihar_terms_accepted" with a
 * version prefix so we can invalidate old acceptances when policy updates.
 *
 * Storage shape: "<TERMS_VERSION>@<ISO timestamp>"
 *   e.g. "v1@2026-05-21T14:23:01.999Z"
 */

export const TERMS_VERSION = "v1";
export const TERMS_STORAGE_KEY = "bihar_terms_accepted";

function readStored() {
  try {
    return localStorage.getItem(TERMS_STORAGE_KEY) || "";
  } catch {
    return "";
  }
}

function parseAccepted(raw) {
  if (!raw || !raw.startsWith(`${TERMS_VERSION}@`)) return null;
  const ix = raw.indexOf("@");
  return ix > 0 ? raw.slice(ix + 1) : null;
}

export function useTermsAcceptance() {
  const [acceptedAt, setAcceptedAt] = useState(() => parseAccepted(readStored()));

  // Keep multiple components in sync if the storage changes
  useEffect(() => {
    const onStorage = (e) => {
      if (e.key === TERMS_STORAGE_KEY) setAcceptedAt(parseAccepted(e.newValue || ""));
    };
    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
  }, []);

  const accept = useCallback(() => {
    const ts = new Date().toISOString();
    try {
      localStorage.setItem(TERMS_STORAGE_KEY, `${TERMS_VERSION}@${ts}`);
    } catch {
      /* localStorage may be unavailable in private mode; just no-op */
    }
    setAcceptedAt(ts);
    return ts;
  }, []);

  const reset = useCallback(() => {
    try {
      localStorage.removeItem(TERMS_STORAGE_KEY);
    } catch {
      /* ignore */
    }
    setAcceptedAt(null);
  }, []);

  return {
    isAccepted: !!acceptedAt,
    acceptedAt,
    accept,
    reset
  };
}

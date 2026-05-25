import { createContext, useContext, useMemo, useState } from "react";
import translations from "../utils/translations.js";

const LanguageContext = createContext(null);

export function LanguageProvider({ children }) {
  const [language, setLanguage] = useState("en");

  const t = (key) => translations?.[language]?.[key] ?? translations?.en?.[key] ?? key;
  const toggleLanguage = () => setLanguage((l) => (l === "en" ? "hi" : "en"));

  const value = useMemo(() => ({ language, setLanguage, t, toggleLanguage }), [language]);
  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

export function useLanguage() {
  const ctx = useContext(LanguageContext);
  if (!ctx) throw new Error("useLanguage must be used within LanguageProvider");
  return ctx;
}


import { useLanguage } from "../../context/LanguageContext.jsx";

export default function LanguageSwitcher() {
  const { language, toggleLanguage } = useLanguage();
  return (
    <button
      type="button"
      onClick={toggleLanguage}
      className="inline-flex items-center justify-center rounded-xl border border-gov-border bg-white px-3 py-2 text-sm font-bold text-gov-primary shadow-soft hover:shadow transition"
      aria-label="Toggle language"
    >
      {language === "en" ? "हिं" : "EN"}
    </button>
  );
}


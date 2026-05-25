/* =====================================================================
 * Bihar Agriculture 4.0 - Portal client
 * - i18n (EN/HI), nav highlighting, support FAB, toast helper
 * - Per-page initializers (home/market/pest/crop/support/faq/analytics/settings/terms)
 * - Pest suggestion renderer with risk-tier driven sections (LOW/MED/HIGH)
 * - Centralised Terms & Conditions acceptance (localStorage)
 * - Programmatic injection of Terms links into nav + footer so every page
 *   gets the link without editing 15 HTML files individually.
 * ===================================================================== */

(() => {
  const API_BASE = `${location.origin}/api/v1`;
  const TERMS_VERSION = "v1";
  const TERMS_KEY = "bihar_terms_accepted";

  /* ---------------- i18n ------------------------------------------------ */
  const translations = {
    en: {
      "nav.home": "Home",
      "nav.market": "Market Intelligence",
      "nav.pest": "Pest Warning",
      "nav.crop": "Crop Recommendation",
      "nav.analytics": "Analytics",
      "nav.reports": "Reports",
      "nav.monitoring": "Monitoring",
      "nav.services": "Services",
      "nav.alerts": "Alerts",
      "nav.support": "Support",
      "nav.terms": "Terms",
      "home.title": "Bihar Agriculture 4.0",
      "home.subtitle": "Smart Farming Intelligence Platform",
      "home.cta": "Get Started",
      "home.watch": "Watch Demo",
      "support.title": "Citizen Assistance",
      "support.search": "How can we help you?"
    },
    hi: {
      "nav.home": "होम",
      "nav.market": "बाजार सूचना",
      "nav.pest": "कीट चेतावनी",
      "nav.crop": "फसल सिफारिश",
      "nav.analytics": "विश्लेषण",
      "nav.reports": "रिपोर्ट",
      "nav.monitoring": "निगरानी",
      "nav.services": "सेवाएँ",
      "nav.alerts": "सूचनाएँ",
      "nav.support": "सहायता",
      "nav.terms": "नियम",
      "home.title": "बिहार कृषि 4.0",
      "home.subtitle": "स्मार्ट खेती सूचना मंच",
      "home.cta": "शुरू करें",
      "home.watch": "डेमो देखें",
      "support.title": "नागरिक सहायता",
      "support.search": "हम आपकी कैसे सहायता करें?"
    }
  };

  const state = { lang: localStorage.getItem("gov_lang") || "en" };
  const t = (key) => translations?.[state.lang]?.[key] ?? translations.en[key] ?? key;

  function setLang(next) {
    state.lang = next;
    localStorage.setItem("gov_lang", next);
    applyTranslations();
  }

  function applyTranslations() {
    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const key = el.getAttribute("data-i18n");
      el.textContent = t(key);
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
      const key = el.getAttribute("data-i18n-placeholder");
      el.setAttribute("placeholder", t(key));
    });
    const btn = document.getElementById("langBtn");
    if (btn) btn.textContent = state.lang === "en" ? "हिं" : "EN";
  }

  /* ---------------- toast ---------------------------------------------- */
  function toast(message, kind = "success") {
    const host = document.getElementById("toastHost");
    if (!host) return;
    const tone = kind === "error" ? "border-red-600" : kind === "warning" ? "border-amber-500" : "border-green-700";
    host.innerHTML = `<div class="gov-card p-4 border-l-4 ${tone}"><div class="font-semibold">${message}</div></div>`;
    setTimeout(() => (host.innerHTML = ""), 5200);
  }

  async function json(url, opts) {
    const r = await fetch(url, opts);
    if (!r.ok) throw new Error(await r.text());
    return r.json();
  }

  /* ---------------- nav + footer programmatic injection ---------------- */
  function injectTermsLink() {
    // Footer link (in the right-side links block)
    document.querySelectorAll("[data-footer-links]").forEach((host) => {
      if (host.querySelector('a[href$="terms.html"]')) return;
      const a = document.createElement("a");
      a.className = "hover:text-slate-900 font-semibold";
      a.href = "./terms.html";
      a.setAttribute("data-i18n", "nav.terms");
      a.textContent = t("nav.terms");
      host.appendChild(a);
    });
    // Top nav link (after the existing items)
    document.querySelectorAll("[data-nav-root]").forEach((host) => {
      if (host.querySelector('a[href$="terms.html"]')) return;
      const a = document.createElement("a");
      a.setAttribute("data-nav", "");
      a.setAttribute("data-i18n", "nav.terms");
      a.href = "./terms.html";
      a.className = "py-2 font-semibold text-slate-700 hover:text-slate-900";
      a.textContent = t("nav.terms");
      host.appendChild(a);
    });
  }

  function activeNav() {
    const path = location.pathname;
    document.querySelectorAll("[data-nav]").forEach((a) => {
      const href = a.getAttribute("href") || "";
      const active = path.endsWith(href) || (href.endsWith("index.html") && (path.endsWith("/portal/") || path.endsWith("/portal")));
      // Legacy class (saffron underline) for the inner-page navs.
      a.classList.toggle("gov-link-active", active);
      // New emerald-underline tab style used by the redesigned home page.
      a.classList.toggle("active", active);
    });
  }

  function wireSupport() {
    const fab = document.getElementById("supportFab");
    const panel = document.getElementById("supportPanel");
    const close = document.getElementById("supportClose");
    if (!fab || !panel) return;
    const toggle = () => panel.classList.toggle("open");
    fab.addEventListener("click", (e) => {
      e.preventDefault();
      toggle();
    });
    close?.addEventListener("click", toggle);
  }

  /* ---------------- Terms & Conditions plumbing ----------------------- */
  const terms = {
    isAccepted() {
      try {
        const v = localStorage.getItem(TERMS_KEY);
        return !!v && v.startsWith(TERMS_VERSION + "@");
      } catch {
        return false;
      }
    },
    accept() {
      localStorage.setItem(TERMS_KEY, `${TERMS_VERSION}@${new Date().toISOString()}`);
    },
    clear() {
      localStorage.removeItem(TERMS_KEY);
    },
    timestamp() {
      const v = localStorage.getItem(TERMS_KEY) || "";
      const ix = v.indexOf("@");
      return ix > 0 ? v.slice(ix + 1) : null;
    },
    /**
     * Render an inline "I agree" gate inside `hostEl`. If terms are already
     * accepted, nothing is rendered. Returns a getter that the form's
     * submit handler can call to decide whether to proceed.
     */
    inlineGate(hostEl) {
      if (!hostEl) return () => true;
      if (terms.isAccepted()) {
        hostEl.innerHTML = "";
        return () => true;
      }
      hostEl.innerHTML = `
        <label class="mt-2 flex items-start gap-3 cursor-pointer rounded-xl border border-slate-200 bg-slate-50 p-3">
          <input data-terms-gate type="checkbox" class="mt-0.5 h-5 w-5 rounded border-slate-300 text-gov-navy focus:ring-2 focus:ring-gov-navy" />
          <span class="text-xs text-slate-700 leading-snug">
            I agree to the <a class="font-semibold text-gov-navy underline" href="./terms.html" target="_blank" rel="noopener">Terms &amp; Conditions</a>
            and the privacy notice. Required before using this advisory.
          </span>
        </label>
      `;
      const box = hostEl.querySelector("[data-terms-gate]");
      return () => {
        if (!box) return true;
        if (box.checked) {
          terms.accept();
          hostEl.innerHTML = "";
          return true;
        }
        toast("Please accept the Terms & Conditions to continue", "warning");
        box.focus();
        return false;
      };
    }
  };

  /* ---------------- HOME ---------------------------------------------- */
  function formatKpi(id, v) {
    if (id === "kpiSavings") {
      // Display in crores when large, else plain rupees
      const cr = v / 10000000;
      return cr >= 1 ? `₹${cr.toFixed(2)} Cr` : `₹${Math.round(v).toLocaleString("en-IN")}`;
    }
    if (id === "kpiSuccess") return `${Math.round(v)}%`;
    return Math.round(v).toLocaleString("en-IN");
  }

  function animateCounter(id, target) {
    const el = document.getElementById(id);
    if (!el) return;
    const start = performance.now();
    const dur = 1100;
    const tick = (ts) => {
      const p = Math.min(1, (ts - start) / dur);
      const eased = p * (2 - p);
      el.textContent = formatKpi(id, target * eased);
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }

  // Hero carousel state (image + crop recommendation rotate together)
  const HERO_SLIDES = [
    { img: "https://images.unsplash.com/photo-1625246333195-78d9c38ad449?auto=format&fit=crop&w=1400&q=80", crop: "Maize" },
    { img: "https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1400&q=80", crop: "Wheat" },
    { img: "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?auto=format&fit=crop&w=1400&q=80", crop: "Rice" },
    { img: "https://images.unsplash.com/photo-1592982537447-7440770cbfc9?auto=format&fit=crop&w=1400&q=80", crop: "Mustard" }
  ];

  function initHeroCarousel() {
    const imgEl = document.getElementById("heroImg");
    const cropEl = document.getElementById("heroRecCrop");
    const dotsEl = document.getElementById("heroDots");
    if (!imgEl || !cropEl) return;
    let i = 0;

    const renderDots = () => {
      if (!dotsEl) return;
      dotsEl.innerHTML = HERO_SLIDES.map((_, idx) => `<i class="${idx === i ? "active" : ""}"></i>`).join("");
    };
    const go = (n) => {
      i = (n + HERO_SLIDES.length) % HERO_SLIDES.length;
      imgEl.style.opacity = "0";
      setTimeout(() => {
        imgEl.style.backgroundImage = `url('${HERO_SLIDES[i].img}')`;
        cropEl.textContent = HERO_SLIDES[i].crop;
        imgEl.style.opacity = "1";
        renderDots();
      }, 200);
    };
    imgEl.style.transition = "opacity .35s ease";

    document.querySelector(".hero-arrow.left")?.addEventListener("click", () => go(i - 1));
    document.querySelector(".hero-arrow.right")?.addEventListener("click", () => go(i + 1));

    let timer = setInterval(() => go(i + 1), 5500);
    // Pause on hover
    const frame = document.querySelector(".hero-frame");
    frame?.addEventListener("mouseenter", () => { clearInterval(timer); });
    frame?.addEventListener("mouseleave", () => { timer = setInterval(() => go(i + 1), 5500); });

    renderDots();
  }

  async function initHome() {
    const counters = [
      ["kpiPred", 10000],
      ["kpiFarmers", 9500],
      ["kpiSavings", 24500000], // ~₹2.45 Cr
      ["kpiSuccess", 92]
    ];
    counters.forEach(([id, target]) => animateCounter(id, target));
    initHeroCarousel();
  }

  /* ---------------- MARKET -------------------------------------------- */
  async function initMarket() {
    const crops = await json(`${API_BASE}/market/crops`).catch(() => ({ crops: ["Wheat"] }));
    const mandis = await json(`${API_BASE}/market/mandis`).catch(() => ({ mandis: ["Patna"] }));
    const cropSel = document.getElementById("cropSel");
    const mandiSel = document.getElementById("mandiSel");
    if (cropSel) cropSel.innerHTML = crops.crops.map((c) => `<option>${c}</option>`).join("");
    if (mandiSel) mandiSel.innerHTML = mandis.mandis.map((m) => `<option>${m}</option>`).join("");

    const btn = document.getElementById("marketBtn");
    const run = async () => {
      const payload = {
        crop: cropSel?.value || "Wheat",
        mandi: mandiSel?.value || "Patna",
        quantity: +(document.getElementById("qty")?.value || 10)
      };
      try {
        const out = await json(`${API_BASE}/market/predict`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        const cur = out.current_price;
        document.getElementById("curPrice").textContent =
          cur == null || cur === ""
            ? "—"
            : `₹ ${Number(cur).toLocaleString("en-IN")}`;
        const rec = out.recommendation || {};
        document.getElementById("bestDate").textContent =
          rec.optimal_date || rec.optimal_sell_date || "—";
        renderMarketCharts(out);
        toast(out.recommendation?.demo ? "Forecast ready (demo — ingest prices for live data)" : "Forecast generated");
      } catch (e) {
        toast("Could not generate forecast", "error");
      }
    };

    btn?.addEventListener("click", run);

    setTimeout(() => {
      if (!document.getElementById("curPrice")?.textContent?.includes("₹")) run();
    }, 250);
  }

  function renderMarketCharts(out) {
    const pts = out.predicted_prices || [];
    const dates = pts.map((p) => p.date);
    const mid = pts.map((p) => p.price);
    const band = pts.map((p) => [p.confidence_low, p.confidence_high]);

    const el = document.getElementById("marketForecast");
    if (!el) return;
    if (!window.ApexCharts) {
      el.innerHTML = chartUnavailable();
      return;
    }
    el.innerHTML = "";
    const options = {
      chart: {
        type: "line", height: 340,
        toolbar: { show: true, tools: { download: true, zoom: true, pan: true } },
        animations: { enabled: true, easing: "easeinout", speed: 800 }
      },
      colors: ["#003087", "#138808"],
      stroke: { curve: "smooth", width: [3, 2], dashArray: [0, 6] },
      xaxis: { categories: dates, labels: { rotate: -30 } },
      yaxis: { labels: { formatter: (v) => `₹${Math.round(v)}` } },
      tooltip: { shared: true, y: { formatter: (v) => `₹${Number(v).toLocaleString("en-IN")}` } },
      fill: { type: "solid" },
      series: [
        { name: "Predicted", data: mid },
        { name: "Band (high)", data: band.map((b) => b[1]) }
      ]
    };
    new ApexCharts(el, options).render();
  }

  function chartUnavailable() {
    return `
      <div class="gov-card p-5 border-l-4 border-red-600">
        <div class="font-extrabold text-slate-900">Charts library not loaded</div>
        <div class="mt-1 text-sm text-slate-700">
          ApexCharts CDN may be blocked. Allow <span class="font-mono">cdn.jsdelivr.net</span>.
        </div>
      </div>`;
  }

  /* ---------------- PEST ---------------------------------------------- */
  // Sections shown by tier; mirrors backend's recommendation_set.
  const SECTION_META = {
    emergency_actions:   { label: "Emergency action",   icon: "🚨", urgent: true },
    symptoms_list:       { label: "Symptoms",           icon: "👁️", urgent: false },
    prevention:          { label: "Prevention",         icon: "🛡️", urgent: false },
    organic_solutions:   { label: "Organic solutions",  icon: "🌿", urgent: false },
    chemical_treatments: { label: "Chemical treatment", icon: "⚗️", urgent: false },
    irrigation_advice:   { label: "Irrigation advice",  icon: "💧", urgent: false }
  };
  const SEV_CLASS = { LOW: "sev-low", MEDIUM: "sev-medium", HIGH: "sev-high" };

  async function initPest() {
    const btn = document.getElementById("pestBtn");
    const btnMobile = document.getElementById("pestBtnMobile");
    const acceptIfReady = terms.inlineGate(document.getElementById("pestTermsGate"));

    const run = async () => {
      if (!acceptIfReady()) return;
      const payload = {
        latitude: +(document.getElementById("lat")?.value || 25.5941),
        longitude: +(document.getElementById("lon")?.value || 85.1376),
        crop: document.getElementById("pCrop")?.value || "rice",
        growth_stage: document.getElementById("stage")?.value || "tillering"
      };

      // Loading state
      setRiskHeader({ overall_risk: null, risk_level: null, headline: "Assessing…", sub: "Fetching forecast + KB lookup" });
      renderGauge(0, true);
      renderThreats([], { overall_risk: 0 });

      try {
        const out = await json(`${API_BASE}/pest/check-risk`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        renderPestResult(out);
        toast("Risk assessed");
      } catch {
        toast("Risk check failed", "error");
        setRiskHeader({ overall_risk: 0, risk_level: "LOW", headline: "Could not assess risk", sub: "Verify backend connectivity and try again." });
        renderThreats([], { overall_risk: 0 });
      }
    };

    btn?.addEventListener("click", run);
    btnMobile?.addEventListener("click", run);

    // Auto-run once (only if terms already accepted)
    setTimeout(() => {
      if (terms.isAccepted()) run();
      else setRiskHeader({ overall_risk: 0, risk_level: "LOW", headline: "Accept terms to run", sub: "Tick the agreement above and press Assess risk." });
    }, 250);
  }

  function setRiskHeader({ overall_risk, risk_level, headline, sub }) {
    const head = document.getElementById("riskHeadline");
    const subEl = document.getElementById("riskSub");
    const pill = document.getElementById("riskPill");
    const score = document.getElementById("riskScore");
    if (head) head.textContent = headline ?? "—";
    if (subEl) subEl.textContent = sub ?? "";
    if (pill) {
      pill.className = `sev-pill ${SEV_CLASS[risk_level] || "sev-low"}`;
      pill.textContent = risk_level || "—";
    }
    if (score) score.textContent = (overall_risk == null ? "—" : overall_risk) + " / 100";
  }

  function renderPestResult(out) {
    const level = out.risk_level || "LOW";
    const tier = out.tier_advice || {};
    setRiskHeader({
      overall_risk: out.overall_risk,
      risk_level: level,
      headline: tier.headline || (level === "HIGH" ? "Act now" : level === "MEDIUM" ? "Take preventive + curative steps" : "Stay watchful"),
      sub: `${(out.threats || []).length} threats matched in the knowledge base for this crop & stage.`
    });
    renderGauge(out.overall_risk || 0);
    renderWeatherSummary(out.weather_forecast);
    renderTierBanner(level, tier);
    renderThreats(out.threats || [], out);

    const meta = document.getElementById("suggestionMeta");
    if (meta) meta.textContent = `Risk tier: ${level} · sections shown: ${(out.recommendation_set || []).length}`;
  }

  function renderWeatherSummary(wx) {
    if (!wx) return;
    const t = document.getElementById("wxTemp");
    const h = document.getElementById("wxHum");
    if (t) t.textContent = wx.temp_avg_next_3_days != null ? `${Number(wx.temp_avg_next_3_days).toFixed(1)} °C` : "—";
    if (h) h.textContent = wx.humidity_avg_next_3_days != null ? `${Number(wx.humidity_avg_next_3_days).toFixed(0)} %` : "—";
  }

  function renderTierBanner(level, tier) {
    const banner = document.getElementById("tierBanner");
    const emergency = document.getElementById("emergencyBanner");
    if (banner) {
      banner.className = `mt-4 sev-banner ${SEV_CLASS[level] || "sev-low"}`;
      banner.classList.remove("hidden");
      const title = document.getElementById("tierBannerTitle");
      const body = document.getElementById("tierBannerBody");
      if (title) title.textContent = tier.headline || (level === "HIGH" ? "Immediate action required" : level === "MEDIUM" ? "Plan preventive + curative steps" : "Stay watchful");
      if (body) body.textContent =
        level === "HIGH"   ? "Apply highlighted emergency actions within 24-48 hours and coordinate with the helpdesk." :
        level === "MEDIUM" ? "Combine prevention, organic and selective chemical control."
                           : "Continue scouting and follow preventive practices.";
    }
    if (emergency) {
      emergency.classList.toggle("hidden", level !== "HIGH");
    }
  }

  function renderThreats(threats, out) {
    const host = document.getElementById("threatList");
    if (!host) return;
    if (!threats.length) {
      host.innerHTML = `
        <div class="gov-card-flat p-6 text-center fade-in-up">
          <div class="text-3xl">✅</div>
          <div class="mt-2 font-extrabold text-slate-900">No matched threats</div>
          <div class="text-sm text-slate-600">No pests in the knowledge base flagged this crop + stage combination.</div>
        </div>`;
      return;
    }

    const sectionsToShow = out?.recommendation_set?.length
      ? out.recommendation_set
      : ["symptoms_list", "prevention", "organic_solutions", "chemical_treatments", "irrigation_advice"];

    host.innerHTML = threats.map((threat, i) => renderThreatCard(threat, sectionsToShow, i === 0)).join("");
  }

  function renderThreatCard(threat, sectionsToShow, openByDefault) {
    const sevClass = SEV_CLASS[threat.risk_level] || "sev-low";
    const suggestions = threat.suggestions || {};
    const hasAny = Object.values(suggestions).some((arr) => Array.isArray(arr) && arr.length);
    const factors = threat.factors || {};

    const sections = sectionsToShow
      .filter((k) => suggestions[k]?.length)
      .map((k) => renderSection(k, suggestions[k]))
      .join("");

    const factorChips = renderFactorChips(factors);

    return `
      <details class="suggest-card ${sevClass} fade-in-up" ${openByDefault ? "open" : ""}>
        <summary>
          <div class="text-2xl leading-none">${threat.icon || "🐛"}</div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 flex-wrap">
              <div class="font-extrabold text-slate-900 truncate">${escapeHtml(threat.pest_name || threat.pest_key || "Pest")}</div>
              <span class="sev-pill ${sevClass}">${threat.risk_level || "—"}</span>
              ${threat.recommendation_set?.includes("emergency_actions") ? `<span class="action-badge">Act now</span>` : ""}
            </div>
            <div class="mt-1 text-xs text-slate-600 truncate">${escapeHtml(threat.category || "")} · ${escapeHtml(threat.summary || "")}</div>
            <div class="mt-2 sev-bar"><i style="width:${threat.risk_score || 0}%"></i></div>
          </div>
          <div class="text-right">
            <div class="font-extrabold text-slate-900">${threat.risk_score ?? "—"}</div>
            <div class="text-[10px] tracking-wide text-slate-500 font-semibold">/ 100</div>
          </div>
          <svg class="chev w-5 h-5 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6"/></svg>
        </summary>
        <div class="body">
          ${factorChips ? `<div class="my-3 flex flex-wrap gap-2 text-xs">${factorChips}</div>` : ""}
          ${hasAny ? sections : `<div class="text-sm text-slate-600">No additional advisory sections available for this pest.</div>`}
        </div>
      </details>`;
  }

  function renderSection(key, items) {
    const meta = SECTION_META[key] || { label: key, icon: "📌", urgent: false };
    const urgentClass = meta.urgent ? "action-badge" : "";
    const tag = meta.urgent ? `<span class="${urgentClass}">Emergency</span>` : "";
    return `
      <div class="suggest-section">
        <h4>
          <span aria-hidden="true">${meta.icon}</span>
          <span>${meta.label}</span>
          ${tag}
        </h4>
        <ul>${items.map((s) => `<li>${escapeHtml(s)}</li>`).join("")}</ul>
      </div>`;
  }

  function renderFactorChips(factors) {
    const chips = [];
    if (factors.growth_stage_vulnerable !== undefined) {
      chips.push(chip(`Stage vulnerable: ${factors.growth_stage_vulnerable ? "yes" : "no"}`, factors.growth_stage_vulnerable));
    }
    if (factors.humidity_trigger_met !== undefined) {
      chips.push(chip(`Humidity trigger: ${factors.humidity_trigger_met ? "met" : "no"}`, factors.humidity_trigger_met));
    }
    if (factors.temp_trigger_met !== undefined) {
      chips.push(chip(`Temp trigger: ${factors.temp_trigger_met ? "met" : "no"}`, factors.temp_trigger_met));
    }
    return chips.join("");
  }
  function chip(label, active) {
    return `<span class="px-2 py-1 rounded-full ${active ? "bg-rose-50 text-rose-800 border border-rose-200" : "bg-slate-100 text-slate-700 border border-slate-200"} font-semibold">${escapeHtml(label)}</span>`;
  }

  function renderGauge(value, loading = false) {
    const el = document.getElementById("pestGauge");
    if (!el) return;
    if (!window.ApexCharts) {
      el.innerHTML = chartUnavailable();
      return;
    }
    el.innerHTML = "";
    const v = Math.max(0, Math.min(100, +value));
    const color = v > 60 ? "#DC3545" : v > 30 ? "#FFA500" : "#138808";
    new ApexCharts(el, {
      chart: { type: "radialBar", height: 260, animations: { enabled: true, speed: 800 } },
      series: [v],
      labels: ["Overall risk"],
      colors: [color],
      plotOptions: {
        radialBar: {
          startAngle: -135,
          endAngle: 135,
          hollow: { size: "65%" },
          track: { background: "#F1F5F9", strokeWidth: "100%" },
          dataLabels: {
            value: { fontSize: "30px", fontWeight: 800, color: "#0F172A", formatter: (val) => loading ? "…" : `${Math.round(val)}` },
            name: { fontSize: "12px", color: "#64748B" }
          }
        }
      }
    }).render();
  }

  function escapeHtml(s) {
    return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  /* ---------------- SUPPORT ------------------------------------------- */
  async function initSupport() {
    const form = document.getElementById("ticketForm");
    if (!form) return;
    const acceptIfReady = terms.inlineGate(document.getElementById("supportTermsGate"));

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (!acceptIfReady()) return;
      const fd = new FormData(form);
      try {
        const out = await json(`${API_BASE}/support/create-ticket`, { method: "POST", body: fd });
        const outEl = document.getElementById("ticketOut");
        if (outEl) outEl.textContent = `Ticket ${out.ticket_number} created.`;
        toast(`Ticket created: ${out.ticket_number}`);
        form.reset();
      } catch {
        toast("Ticket submission failed", "error");
      }
    });
  }

  /* ---------------- CROP ---------------------------------------------- */
  function normalizeCropApiResponse(raw) {
    const recList = raw.recommendations || [];
    if (!recList.length) return { zone: "—", recommendations: [] };
    const first = recList[0];
    if (first.confidence_pct != null) {
      const zoneTitle = raw.zone_characteristics?.zone_name || (raw.detected_zone || "").replace(/_/g, " ").trim();
      const recommendations = recList.map((r) => ({
        crop: r.crop,
        confidence: Math.round(Number(r.confidence_pct) || 0),
        expected_yield_quintals_acre: r.expected_yield_quintals_acre ?? r.top_farmer_yield_quintals_acre ?? r.yield_avg ?? "—"
      }));
      return { zone: zoneTitle || "—", recommendations };
    }
    return {
      zone: raw.zone ?? "—",
      recommendations: recList.map((r) => ({
        crop: r.crop,
        confidence: Math.round(Number(r.confidence) || 0),
        expected_yield_quintals_acre: r.expected_yield_quintals_acre ?? "—"
      }))
    };
  }

  function renderCropChart(recs) {
    const host = document.getElementById("cropChartHost");
    if (!host) return;
    const labels = recs.map((r) => r.crop);
    const values = recs.map((r) => Number(r.confidence) || 0);
    const palette = ["#003087", "#138808", "#FF9933", "#DC3545", "#FFA500"];
    const barColors = labels.map((_, i) => palette[i % palette.length]);
    if (host._apexCrop) { try { host._apexCrop.destroy(); } catch {} host._apexCrop = null; }
    host.innerHTML = "";
    if (window.ApexCharts) {
      const mount = document.createElement("div");
      mount.className = "min-h-[260px]";
      host.appendChild(mount);
      host._apexCrop = new ApexCharts(mount, {
        chart: { type: "bar", height: 300, toolbar: { show: true }, animations: { enabled: true } },
        series: [{ name: "Confidence (%)", data: values }],
        xaxis: { categories: labels, labels: { rotate: -22 } },
        plotOptions: { bar: { borderRadius: 8, columnWidth: "55%", distributed: true } },
        colors: barColors,
        dataLabels: { enabled: true, formatter: (v) => `${Math.round(v)}%` },
        yaxis: { max: 100, tickAmount: 5, labels: { formatter: (v) => `${Math.round(v)}%` } },
        tooltip: { y: { formatter: (v) => `${Math.round(Number(v))}%` } },
        legend: { show: false }
      });
      host._apexCrop.render();
      return;
    }
    host.innerHTML = chartUnavailable();
  }

  async function initCrop() {
    const btn = document.getElementById("cropBtn");
    if (!btn) return;
    const acceptIfReady = terms.inlineGate(document.getElementById("cropTermsGate"));

    const payloadFromForm = () => ({
      latitude: 25.5941,
      longitude: 85.1376,
      soil_npk: {
        n: +(document.getElementById("n")?.value || 90),
        p: +(document.getElementById("p")?.value || 42),
        k: +(document.getElementById("k")?.value || 43)
      },
      ph: +(document.getElementById("ph")?.value || 6.8),
      soil_type: document.getElementById("soilType")?.value || "alluvial",
      season: document.getElementById("season")?.value || "rabi",
      district: document.getElementById("district")?.value?.trim() || null
    });

    const applyResults = (out) => {
      const normalized = normalizeCropApiResponse(out);
      const recs = (normalized.recommendations || []).slice().sort((a, b) => (b.confidence || 0) - (a.confidence || 0));
      const list = document.getElementById("cropList");
      if (!recs.length) {
        document.getElementById("topCrop").textContent = "—";
        document.getElementById("topConf").textContent = "—";
        document.getElementById("zone").textContent = normalized.zone || "—";
        if (list) list.innerHTML = `<div class="gov-card p-4 text-sm text-slate-700">No recommendation rows returned.</div>`;
        return;
      }
      const top = recs[0];
      document.getElementById("topCrop").textContent = top.crop || "—";
      document.getElementById("topConf").textContent = `${top.confidence ?? "—"}%`;
      document.getElementById("zone").textContent = normalized.zone || "—";
      renderCropChart(recs);
      if (list) {
        list.innerHTML = recs.map((r, idx) => `
          <div class="gov-card-flat p-4 ${idx === 0 ? "border-l-4 border-gov-navy" : ""} fade-in-up">
            <div class="flex items-center justify-between gap-2">
              <div class="font-extrabold text-slate-900">${escapeHtml(r.crop)}</div>
              <div class="font-extrabold text-slate-900">${r.confidence}%</div>
            </div>
            <div class="mt-1 text-sm text-slate-700">Expected yield: <span class="font-semibold">${escapeHtml(String(r.expected_yield_quintals_acre ?? "—"))}</span> q/acre</div>
          </div>`).join("");
      }
    };

    const run = async () => {
      if (!acceptIfReady()) return;
      try {
        btn.disabled = true;
        btn.textContent = "Generating…";
        const body = payloadFromForm();
        let raw;
        try {
          raw = await json(`${API_BASE}/crop/recommend`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
        } catch {
          raw = await json(`${API_BASE}/crop/recommend-adaptive`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
        }
        applyResults(raw);
        toast("Recommendation generated");
      } catch (e) {
        console.error(e);
        toast("Could not generate recommendation", "error");
        const list = document.getElementById("cropList");
        if (list) list.innerHTML = `<div class="gov-card p-4 border-l-4 border-red-600"><div class="font-semibold">Could not load recommendations</div><div class="mt-2 text-sm text-slate-700">Confirm the API is running.</div></div>`;
      } finally {
        btn.disabled = false;
        btn.textContent = "Generate recommendation";
      }
    };

    btn.addEventListener("click", run);
    setTimeout(() => { if (terms.isAccepted() && document.getElementById("topCrop")?.textContent.trim() === "—") run(); }, 300);
  }

  /* ---------------- ANALYTICS ----------------------------------------- */
  async function initAnalytics() {
    const elA = document.getElementById("analyticsAdvisory");
    const elR = document.getElementById("analyticsRisk");
    const sub = document.getElementById("analyticsSubtitle");
    if (!elA || !elR) return;
    const bust = () => {
      try { elA._line?.destroy(); } catch {}
      try { elR._donut?.destroy(); } catch {}
      elA._line = null; elR._donut = null;
      elA.innerHTML = ""; elR.innerHTML = "";
    };
    if (!window.ApexCharts) {
      const msg = `<div class="gov-card p-4 border-l-4 border-red-600 text-sm">Charts library unavailable.</div>`;
      elA.innerHTML = msg; elR.innerHTML = msg; if (sub) sub.textContent = "";
      return;
    }
    try {
      bust();
      const d = await json(`${API_BASE}/dashboard/analytics-charts`);
      if (sub && d.subtitle) sub.textContent = d.subtitle;
      const m1 = document.createElement("div"); elA.appendChild(m1);
      elA._line = new ApexCharts(m1, {
        chart: { type: "area", height: 280, toolbar: { show: true }, animations: { enabled: true }, zoom: { enabled: true } },
        stroke: { curve: "smooth", width: 2 }, colors: ["#003087"],
        fill: { type: "gradient", gradient: { shadeIntensity: 0.65, opacityFrom: 0.45, opacityTo: 0.06, stops: [0, 90] } },
        series: [{ name: "Advisory consultations", data: d.advisory_volume || [] }],
        xaxis: { categories: d.month_labels || [], labels: { rotate: -12 } },
        dataLabels: { enabled: false },
        yaxis: { labels: { formatter: (v) => `${Math.round(v)}` } },
        tooltip: { y: { formatter: (v) => Number(v).toLocaleString("en-IN") } }
      });
      elA._line.render();
      const rk = d.risk_distribution_pct || {};
      const m2 = document.createElement("div"); elR.appendChild(m2);
      elR._donut = new ApexCharts(m2, {
        chart: { type: "donut", height: 290, animations: { enabled: true }, toolbar: { show: false } },
        labels: ["Low risk", "Medium risk", "High risk"],
        series: [rk.low ?? 58, rk.medium ?? 28, rk.high ?? 14],
        colors: ["#138808", "#FFA500", "#DC3545"],
        legend: { position: "bottom" },
        plotOptions: { pie: { donut: { size: "72%", labels: { show: true, total: { show: true, label: "Total", formatter: () => `${(Number(rk.low) + Number(rk.medium) + Number(rk.high)).toFixed(0)}%` } } } } },
        dataLabels: { enabled: false }
      });
      elR._donut.render();
    } catch (e) {
      console.error(e);
      bust();
      const err = `<div class="gov-card p-4 border-l-4 border-red-600 text-sm">Could not load analytics. Confirm API <span class="font-mono">/api/v1/dashboard/analytics-charts</span>.</div>`;
      elA.innerHTML = err; elR.innerHTML = err; if (sub) sub.textContent = "";
    }
  }

  /* ---------------- FAQ ----------------------------------------------- */
  async function initFaq() {
    const host = document.getElementById("faqHost");
    if (!host) return;
    try {
      const out = await json(`${API_BASE}/support/faqs`);
      const faqs = out.faqs || [];
      host.innerHTML = faqs.map((f) => `
        <details class="gov-card p-5">
          <summary class="cursor-pointer font-extrabold text-slate-900">${escapeHtml(f.q)}</summary>
          <div class="mt-2 text-slate-700">${escapeHtml(f.a)}</div>
        </details>`).join("");
    } catch {
      host.innerHTML = `<div class="gov-card p-5 border-l-4 border-red-600"><div class="font-semibold">Could not load FAQs.</div></div>`;
    }
  }

  /* ---------------- SETTINGS ------------------------------------------ */
  function initSettings() {
    const status = document.getElementById("settingsTermsStatus");
    const reset = document.getElementById("settingsTermsReset");
    const view = document.getElementById("settingsTermsView");
    function refresh() {
      if (!status) return;
      if (terms.isAccepted()) {
        const ts = terms.timestamp();
        status.innerHTML = `<span class="sev-pill sev-low">ACCEPTED</span> <span class="text-sm text-slate-600 ml-2">${ts ? new Date(ts).toLocaleString() : ""}</span>`;
      } else {
        status.innerHTML = `<span class="sev-pill sev-medium">NOT ACCEPTED</span>`;
      }
    }
    reset?.addEventListener("click", () => { terms.clear(); refresh(); toast("Terms acceptance cleared"); });
    view?.addEventListener("click", () => (location.href = "./terms.html"));
    refresh();
  }

  /* ---------------- TERMS PAGE --------------------------------------- */
  function initTerms() {
    const box = document.getElementById("termsAcceptBox");
    const save = document.getElementById("termsSaveBtn");
    const clear = document.getElementById("termsClearBtn");
    const status = document.getElementById("termsStatus");
    function refresh() {
      if (!status) return;
      if (terms.isAccepted()) {
        const ts = terms.timestamp();
        status.innerHTML = `Accepted on ${ts ? new Date(ts).toLocaleString() : "this device"}.`;
        if (box) box.checked = true;
      } else {
        status.textContent = "";
        if (box) box.checked = false;
      }
    }
    save?.addEventListener("click", () => {
      if (!box?.checked) { toast("Tick the agreement to save", "warning"); return; }
      terms.accept(); refresh(); toast("Acceptance saved on this device");
    });
    clear?.addEventListener("click", () => { terms.clear(); refresh(); toast("Acceptance cleared"); });
    refresh();
  }

  /* ---------------- bootstrap ----------------------------------------- */
  document.addEventListener("DOMContentLoaded", async () => {
    injectTermsLink();          // run BEFORE translations so labels apply
    applyTranslations();
    activeNav();
    wireSupport();

    document.getElementById("langBtn")?.addEventListener("click", () => setLang(state.lang === "en" ? "hi" : "en"));

    const page = document.body.getAttribute("data-page");
    if (page === "home") initHome();
    if (page === "market") initMarket();
    if (page === "pest") initPest();
    if (page === "support") initSupport();
    if (page === "crop") initCrop();
    if (page === "faq") initFaq();
    if (page === "analytics") initAnalytics();
    if (page === "settings") initSettings();
    if (page === "terms") initTerms();
  });
})();

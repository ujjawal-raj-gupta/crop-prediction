import { Routes, Route, Navigate } from "react-router-dom";
import { AnimatePresence } from "framer-motion";

import DashboardLayout from "./components/layout/DashboardLayout.jsx";
import Home from "./pages/Home.jsx";
import MarketIntelligence from "./pages/MarketIntelligence.jsx";
import PestWarning from "./pages/PestWarning.jsx";
import CropRecommendation from "./pages/CropRecommendation.jsx";
import Reports from "./pages/Reports.jsx";
import Monitoring from "./pages/Monitoring.jsx";
import Services from "./pages/Services.jsx";
import Alerts from "./pages/Alerts.jsx";
import Support from "./pages/Support.jsx";
import FAQ from "./pages/FAQ.jsx";
import Contact from "./pages/Contact.jsx";
import Settings from "./pages/Settings.jsx";
import Admin from "./pages/Admin.jsx";
import Terms from "./pages/Terms.jsx";

export default function App() {
  return (
    <AnimatePresence mode="wait">
      <Routes>
        <Route path="/" element={<DashboardLayout />}>
          <Route index element={<Home />} />
          <Route path="market" element={<MarketIntelligence />} />
          <Route path="pest-warning" element={<PestWarning />} />
          <Route path="crop-recommendation" element={<CropRecommendation />} />
          <Route path="reports" element={<Reports />} />
          <Route path="monitoring" element={<Monitoring />} />
          <Route path="services" element={<Services />} />
          <Route path="alerts" element={<Alerts />} />
          <Route path="support" element={<Support />} />
          <Route path="faq" element={<FAQ />} />
          <Route path="contact" element={<Contact />} />
          <Route path="settings" element={<Settings />} />
          <Route path="admin" element={<Admin />} />
          <Route path="terms" element={<Terms />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AnimatePresence>
  );
}


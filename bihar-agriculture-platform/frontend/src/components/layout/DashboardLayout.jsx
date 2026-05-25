import { Outlet } from "react-router-dom";

import Navbar from "../common/Navbar.jsx";
import Sidebar from "../common/Sidebar.jsx";
import Footer from "../common/Footer.jsx";
import SupportWidget from "../common/SupportWidget.jsx";

export default function DashboardLayout() {
  return (
    <div className="min-h-screen bg-gov-bg">
      <Navbar />
      <div className="mx-auto max-w-7xl px-4">
        <div className="grid grid-cols-1 lg:grid-cols-[260px_1fr] gap-6 py-6">
          <aside className="hidden lg:block">
            <Sidebar />
          </aside>
          <main className="min-w-0">
            <Outlet />
          </main>
        </div>
      </div>
      <Footer />
      <SupportWidget />
    </div>
  );
}


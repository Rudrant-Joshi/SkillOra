import { useState } from 'react';
import { AnimatePresence } from 'framer-motion';
import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from '../components/layout/Sidebar';
import TopBar from '../components/layout/TopBar';
import PageTransition from '../components/layout/PageTransition';

export default function AppShell() {
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const location = useLocation();

  return (
    <div className="min-h-screen flex relative overflow-hidden bg-black text-white">
      {/* Futuristic ambient background lighting */}
      <div className="fixed inset-0 pointer-events-none bg-[radial-gradient(ellipse_80%_60%_at_50%_-10%,rgba(57,255,20,0.06),transparent)] z-0" />
      <div className="fixed inset-0 pointer-events-none bg-[radial-gradient(ellipse_50%_50%_at_90%_90%,rgba(57,255,20,0.03),transparent)] z-0" />
      <div className="fixed inset-0 pointer-events-none bg-[linear-gradient(to_right,rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:4.5rem_4.5rem] z-0 opacity-60" />

      <Sidebar mobileOpen={mobileNavOpen} onCloseMobile={() => setMobileNavOpen(false)} />
      <div className="flex-1 min-w-0 lg:ml-[252px] relative z-10">
        <TopBar onOpenMobileNav={() => setMobileNavOpen(true)} />
        <main className="px-5 sm:px-8 lg:px-10 pt-9 pb-20 max-w-[1240px]">
          <AnimatePresence mode="wait">
            <PageTransition key={location.pathname}>
              <Outlet />
            </PageTransition>
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
}

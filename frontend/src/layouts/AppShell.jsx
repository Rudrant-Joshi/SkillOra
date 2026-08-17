import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from '../components/layout/Sidebar';
import TopBar from '../components/layout/TopBar';
import PageTransition from '../components/layout/PageTransition';
import AnimatedGrid from '../components/motion/AnimatedGrid';
import CursorGlow from '../components/motion/CursorGlow';
import GradientOrb from '../components/motion/GradientOrb';

export default function AppShell() {
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  return (
    <div className="min-h-screen flex relative bg-black text-white selection:bg-green selection:text-black overflow-x-hidden">
      {/* High-intensity Background Effects */}
      <AnimatedGrid />
      <CursorGlow />
      <GradientOrb
        color="rgba(57, 255, 20, 0.18)"
        size={850}
        style={{ top: '-10%', left: '20%' }}
      />
      <GradientOrb
        color="rgba(57, 255, 20, 0.14)"
        size={700}
        style={{ bottom: '5%', right: '10%' }}
      />

      <Sidebar mobileOpen={mobileNavOpen} onCloseMobile={() => setMobileNavOpen(false)} />
      <div className="flex-1 min-w-0 lg:ml-[252px] relative z-[2]">
        <TopBar onOpenMobileNav={() => setMobileNavOpen(true)} />
        <main className="px-5 sm:px-8 lg:px-10 pt-9 pb-20 max-w-[1240px] relative z-[2]">
          <PageTransition>
            <Outlet />
          </PageTransition>
        </main>
      </div>
    </div>
  );
}

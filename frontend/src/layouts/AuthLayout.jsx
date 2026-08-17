import { Outlet } from 'react-router-dom';
import AnimatedGrid from '../components/motion/AnimatedGrid';
import CursorGlow from '../components/motion/CursorGlow';
import GradientOrb from '../components/motion/GradientOrb';

export default function AuthLayout() {
  return (
    <div
      className="min-h-screen flex items-center justify-center px-5 py-10 relative overflow-hidden bg-black text-white selection:bg-green selection:text-black"
    >
      {/* High-intensity Background Effects */}
      <AnimatedGrid />
      <CursorGlow />
      <GradientOrb
        color="rgba(57, 255, 20, 0.24)"
        size={800}
        style={{ top: '5%', left: '15%' }}
      />
      <GradientOrb
        color="rgba(57, 255, 20, 0.18)"
        size={600}
        style={{ bottom: '5%', right: '15%' }}
      />
      <div className="relative z-10 w-full max-w-md">
        <Outlet />
      </div>
    </div>
  );
}

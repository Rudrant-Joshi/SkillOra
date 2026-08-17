import { useState } from 'react';
import { motion } from 'framer-motion';
import { Bell, Menu, Search } from 'lucide-react';
import { useLocation } from 'react-router-dom';
import NotificationPanel from './NotificationPanel';
import SearchOverlay from './SearchOverlay';
import { useSmoothScroll } from '../../hooks/useSmoothScroll';
import { springs } from '../../lib/motionConfig';

function titleFromPath(pathname) {
  const seg = pathname.split('/').filter(Boolean).pop() || 'dashboard';
  return seg.replace(/-/g, ' ');
}

export default function TopBar({ onOpenMobileNav }) {
  const [notifOpen, setNotifOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const location = useLocation();
  const { isScrolled } = useSmoothScroll();

  return (
    <>
      <motion.div
        className="h-16 border-b flex items-center justify-between px-5 lg:px-8 sticky top-0 z-40"
        animate={{
          backgroundColor: isScrolled ? 'rgba(0,0,0,0.95)' : 'rgba(0,0,0,0.7)',
          borderColor: isScrolled ? '#242424' : 'rgba(36,36,36,0.5)',
          backdropFilter: isScrolled ? 'blur(12px)' : 'blur(4px)',
        }}
        transition={{ duration: 0.35 }}
      >
        <div className="flex items-center gap-4">
          <motion.button
            className="lg:hidden icon-btn border border-borderDim w-8 h-8 flex items-center justify-center"
            onClick={onOpenMobileNav}
            type="button"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            transition={springs.snappy}
          >
            <Menu size={16} />
          </motion.button>
          <div className="text-[11px] tracking-[2px] text-textDim uppercase hidden sm:block">
            SkillGraph / <b className="text-white">{titleFromPath(location.pathname)}</b>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <motion.button
            className="w-[34px] h-[34px] border border-borderDim flex items-center justify-center text-textDim"
            onClick={() => setSearchOpen(true)}
            type="button"
            aria-label="Search"
            whileHover={{ scale: 1.08, color: '#fff' }}
            whileTap={{ scale: 0.93 }}
            transition={springs.snappy}
          >
            <Search size={14} />
          </motion.button>
          <motion.button
            className="relative w-[34px] h-[34px] border border-borderDim flex items-center justify-center text-textDim"
            onClick={() => setNotifOpen((v) => !v)}
            type="button"
            aria-label="Notifications"
            whileHover={{ scale: 1.08, color: '#fff' }}
            whileTap={{ scale: 0.93 }}
            transition={springs.snappy}
          >
            <Bell size={14} />
            <motion.span
              className="absolute top-1.5 right-1.5 w-1.5 h-1.5 bg-green rounded-full"
              animate={{
                boxShadow: [
                  '0 0 4px rgba(57,255,20,0.6)',
                  '0 0 10px rgba(57,255,20,0.3)',
                  '0 0 4px rgba(57,255,20,0.6)',
                ],
              }}
              transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
            />
          </motion.button>
        </div>
      </motion.div>
      <NotificationPanel open={notifOpen} onClose={() => setNotifOpen(false)} />
      <SearchOverlay open={searchOpen} onClose={() => setSearchOpen(false)} />
    </>
  );
}

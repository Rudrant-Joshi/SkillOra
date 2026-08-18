import { useState } from 'react';
import { motion } from 'framer-motion';
import { Bell, Menu, Search } from 'lucide-react';
import { useLocation } from 'react-router-dom';
import NotificationPanel from './NotificationPanel';
import SearchOverlay from './SearchOverlay';
import { press } from '../../lib/motion';

function titleFromPath(pathname) {
  const seg = pathname.split('/').filter(Boolean).pop() || 'dashboard';
  return seg.replace(/-/g, ' ');
}

export default function TopBar({ onOpenMobileNav }) {
  const [notifOpen, setNotifOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const location = useLocation();

  return (
    <>
      <div className="h-16 border-b border-borderDim flex items-center justify-between px-5 lg:px-8 sticky top-0 bg-black/90 backdrop-blur-md z-40">
        <div className="flex items-center gap-4">
          <motion.button
            className="lg:hidden icon-btn border border-borderDim w-8 h-8 flex items-center justify-center"
            onClick={onOpenMobileNav}
            type="button"
            whileHover={{ borderColor: '#fff' }}
            whileTap={{ scale: press.tapScale }}
          >
            <Menu size={16} />
          </motion.button>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
            key={location.pathname}
            className="text-[11px] tracking-[2px] text-textDim uppercase hidden sm:block"
          >
            SkillGraph / <b className="text-white">{titleFromPath(location.pathname)}</b>
          </motion.div>
        </div>
        <div className="flex items-center gap-4">
          <motion.button
            className="w-[34px] h-[34px] border border-borderDim flex items-center justify-center text-textDim"
            onClick={() => setSearchOpen(true)}
            type="button"
            aria-label="Search"
            whileHover={{ scale: 1.06, borderColor: '#fff', color: '#fff' }}
            whileTap={{ scale: press.tapScale }}
            transition={{ duration: 0.15 }}
          >
            <Search size={14} />
          </motion.button>
          <motion.button
            className="relative w-[34px] h-[34px] border border-borderDim flex items-center justify-center text-textDim"
            onClick={() => setNotifOpen((v) => !v)}
            type="button"
            aria-label="Notifications"
            whileHover={{ scale: 1.06, borderColor: '#fff', color: '#fff' }}
            whileTap={{ scale: press.tapScale }}
            transition={{ duration: 0.15 }}
          >
            <motion.span animate={{ rotate: notifOpen ? [0, -12, 12, 0] : 0 }} transition={{ duration: 0.35 }}>
              <Bell size={14} />
            </motion.span>
            <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 bg-green rounded-full shadow-[0_0_6px_var(--green)] status-pulse" />
          </motion.button>
        </div>
      </div>
      <NotificationPanel open={notifOpen} onClose={() => setNotifOpen(false)} />
      <SearchOverlay open={searchOpen} onClose={() => setSearchOpen(false)} />
    </>
  );
}

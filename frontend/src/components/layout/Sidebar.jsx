import { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { navGroups, routeFor, roleName, roleTitle, roleInitials } from '../../data/roles';
import { useAuth } from '../../context/AuthContext';
import { ease } from '../../lib/motion';
import { useReducedMotion } from '../../hooks/useReducedMotion';

export default function Sidebar({ mobileOpen, onCloseMobile }) {
  const { role, switchRole, logout } = useAuth();
  const navigate = useNavigate();
  const [roleMenuOpen, setRoleMenuOpen] = useState(false);
  const groups = navGroups[role] || navGroups.developer;
  const reduced = useReducedMotion();

  const handleSwitchRole = (r) => {
    setRoleMenuOpen(false);
    navigate(switchRole(r));
  };

  const sidebarBody = (
    <>
      <motion.div
        initial={reduced ? false : { opacity: 0, y: -6 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: ease.out }}
        className="px-[22px] pt-[26px] pb-5 h-display text-[19px] border-b border-borderDim"
      >
        SKILL<span className="text-green">GRAPH</span>
      </motion.div>

      <motion.nav
        className="flex-1 px-3 py-4 flex flex-col gap-0.5 overflow-y-auto scrollbar-thin"
        initial="hidden"
        animate="show"
        variants={{ hidden: {}, show: { transition: { staggerChildren: reduced ? 0 : 0.035, delayChildren: reduced ? 0 : 0.08 } } }}
      >
        {groups.map((group, gi) => (
          <div key={gi}>
            {group.label && (
              <motion.div
                variants={{ hidden: { opacity: 0 }, show: { opacity: 1, transition: { duration: 0.3 } } }}
                className="text-[9px] tracking-[2px] text-textMute px-3.5 pt-4 pb-1.5 uppercase"
              >
                {group.label}
              </motion.div>
            )}
            {group.items.map((item) => (
              <motion.div
                key={item.t}
                variants={{ hidden: reduced ? { opacity: 0 } : { opacity: 0, x: -8 }, show: { opacity: 1, x: 0, transition: { duration: 0.32, ease: ease.out } } }}
              >
                <NavLink
                  to={routeFor[item.t] || '/app/dashboard'}
                  onClick={onCloseMobile}
                  className={({ isActive }) =>
                    `group relative flex items-center gap-3 px-3.5 py-[11px] text-xs tracking-wider uppercase overflow-hidden transition-colors ${
                      isActive ? 'text-white bg-surface2' : 'text-textDim hover:text-white hover:bg-surface2'
                    }`
                  }
                >
                  {({ isActive }) => (
                    <>
                      {isActive && (
                        <motion.span
                          layoutId="sidebar-active-indicator"
                          className="absolute left-0 top-0 bottom-0 w-[2px] bg-green"
                          transition={{ type: 'spring', stiffness: 500, damping: 40 }}
                        />
                      )}
                      <motion.span
                        className="w-1.5 h-1.5 flex-shrink-0"
                        animate={{ background: isActive ? 'var(--green)' : 'var(--text-mute)', boxShadow: isActive ? '0 0 8px var(--green)' : '0 0 0px transparent' }}
                        whileHover={reduced ? undefined : { x: 3 }}
                        transition={{ duration: 0.2 }}
                      />
                      <motion.span whileHover={reduced ? undefined : { x: 3 }} transition={{ duration: 0.15 }}>
                        {item.l}
                      </motion.span>
                    </>
                  )}
                </NavLink>
              </motion.div>
            ))}
          </div>
        ))}
      </motion.nav>

      <div className="relative px-[18px] py-[16px] pb-[22px] border-t border-borderDim">
        <AnimatePresence>
          {roleMenuOpen && (
            <motion.div
              initial={{ opacity: 0, y: 8, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 8, scale: 0.98 }}
              transition={{ duration: 0.18, ease: ease.out }}
              className="absolute left-[14px] right-[14px] bottom-[64px] bg-black border border-borderDim z-[60]"
            >
              {['developer', 'recruiter', 'company'].map((r) => (
                <button
                  key={r}
                  onClick={() => handleSwitchRole(r)}
                  className="w-full text-left px-3.5 py-3 text-[11px] tracking-wide text-textDim border-b border-borderDim last:border-none hover:text-green hover:bg-surface2 transition-colors uppercase"
                >
                  Switch to {r}
                </button>
              ))}
              <button
                onClick={logout}
                className="w-full text-left px-3.5 py-3 text-[11px] tracking-wide text-textDim hover:text-green hover:bg-surface2 transition-colors uppercase"
              >
                Sign out
              </button>
            </motion.div>
          )}
        </AnimatePresence>
        <motion.button
          className="flex items-center gap-2.5 w-full text-left"
          onClick={() => setRoleMenuOpen((v) => !v)}
          type="button"
          whileTap={{ scale: 0.98 }}
        >
          <span className="w-[34px] h-[34px] flex-shrink-0 bg-green text-black flex items-center justify-center h-display text-[13px]">
            {roleInitials[role]}
          </span>
          <span className="min-w-0">
            <div className="text-xs tracking-wide truncate">{roleName[role]}</div>
            <div className="text-[10px] text-textDim tracking-wide mt-0.5 truncate">{roleTitle[role]}</div>
          </span>
        </motion.button>
      </div>
    </>
  );

  return (
    <>
      {/* Desktop sidebar — always mounted */}
      <aside className="fixed top-0 bottom-0 left-0 z-50 w-[252px] bg-black border-r border-borderDim flex-col hidden lg:flex">
        {sidebarBody}
      </aside>

      {/* Mobile drawer — mounts/unmounts with a real slide + backdrop fade */}
      <AnimatePresence>
        {mobileOpen && (
          <>
            <motion.div
              key="backdrop"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.25 }}
              className="fixed inset-0 bg-black/70 z-40 lg:hidden"
              onClick={onCloseMobile}
            />
            <motion.aside
              key="drawer"
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              transition={{ type: 'spring', stiffness: 340, damping: 34 }}
              className="fixed top-0 bottom-0 left-0 z-50 w-[252px] bg-black border-r border-borderDim flex flex-col lg:hidden"
            >
              {sidebarBody}
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </>
  );
}

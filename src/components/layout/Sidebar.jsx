import { useState } from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { navGroups, routeFor, roleName, roleTitle, roleInitials } from '../../data/roles';
import { useAuth } from '../../context/AuthContext';
import { springs, ease, duration } from '../../lib/motionConfig';

export default function Sidebar({ mobileOpen, onCloseMobile }) {
  const { role, switchRole, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [roleMenuOpen, setRoleMenuOpen] = useState(false);
  const groups = navGroups[role] || navGroups.developer;

  const handleSwitchRole = (r) => {
    setRoleMenuOpen(false);
    navigate(switchRole(r));
  };

  return (
    <>
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 w-[252px] bg-black/85 backdrop-blur-xl border-r border-borderDim flex flex-col transition-transform duration-300 ${
          mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        {/* Logo with ambient glow */}
        <div className="px-[22px] pt-[26px] pb-5 h-display text-[19px] border-b border-borderDim relative overflow-hidden">
          SKILL<span className="text-green" style={{ textShadow: '0 0 25px rgba(57,255,20,0.6), 0 0 45px rgba(57,255,20,0.3)' }}>GRAPH</span>
          {/* Subtle ambient glow behind logo */}
          <div
            aria-hidden="true"
            style={{
              position: 'absolute',
              top: '50%',
              left: '40%',
              width: 140,
              height: 50,
              background: 'radial-gradient(ellipse, rgba(57,255,20,0.2), transparent 70%)',
              transform: 'translate(-50%, -50%)',
              pointerEvents: 'none',
            }}
          />
        </div>

        <nav className="flex-1 px-3 py-4 flex flex-col gap-0.5 overflow-y-auto scrollbar-thin">
          {groups.map((group, gi) => (
            <div key={gi}>
              {group.label && (
                <motion.div
                  className="text-[9px] tracking-[2px] text-textMute px-3.5 pt-4 pb-1.5 uppercase"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: gi * 0.05 + 0.1 }}
                >
                  {group.label}
                </motion.div>
              )}
              {group.items.map((item) => {
                const to = routeFor[item.t] || '/app/dashboard';
                return (
                  <NavLink
                    key={item.t}
                    to={to}
                    onClick={onCloseMobile}
                    className={({ isActive }) =>
                      `relative flex items-center gap-3 px-3.5 py-[11px] text-xs tracking-wider uppercase transition-colors ${
                        isActive
                          ? 'text-white'
                          : 'text-textDim hover:text-white'
                      }`
                    }
                  >
                    {({ isActive }) => (
                      <>
                        {/* Animated active background */}
                        {isActive && (
                          <motion.div
                            layoutId="sidebar-active-bg"
                            className="absolute inset-0 bg-surface2 border-l-2 border-green"
                            transition={springs.snappy}
                            style={{ zIndex: -1 }}
                          />
                        )}
                        {/* Animated dot indicator */}
                        <motion.span
                          className="w-1.5 h-1.5 flex-shrink-0 rounded-[1px]"
                          style={{
                            background: isActive ? 'var(--green)' : 'var(--text-mute)',
                          }}
                          animate={{
                            scale: isActive ? 1 : 0.8,
                            boxShadow: isActive ? '0 0 8px var(--green)' : '0 0 0px transparent',
                          }}
                          transition={springs.snappy}
                        />
                        <motion.span
                          animate={{ x: isActive ? 2 : 0 }}
                          transition={springs.snappy}
                        >
                          {item.l}
                        </motion.span>
                      </>
                    )}
                  </NavLink>
                );
              })}
            </div>
          ))}
        </nav>

        {/* User profile footer */}
        <div className="relative px-[18px] py-[16px] pb-[22px] border-t border-borderDim">
          <AnimatePresence>
            {roleMenuOpen && (
              <motion.div
                initial={{ opacity: 0, y: 8, scale: 0.97 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 8, scale: 0.97 }}
                transition={springs.snappy}
                className="absolute left-[14px] right-[14px] bottom-[64px] bg-black border border-borderDim z-[60]"
              >
                {['developer', 'recruiter', 'company'].map((r, i) => (
                  <motion.button
                    key={r}
                    onClick={() => handleSwitchRole(r)}
                    className="w-full text-left px-3.5 py-3 text-[11px] tracking-wide text-textDim border-b border-borderDim last:border-none hover:text-green hover:bg-surface2 transition-colors uppercase"
                    initial={{ opacity: 0, x: -8 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.05, duration: 0.2 }}
                  >
                    Switch to {r}
                  </motion.button>
                ))}
                <motion.button
                  onClick={logout}
                  className="w-full text-left px-3.5 py-3 text-[11px] tracking-wide text-textDim hover:text-green hover:bg-surface2 transition-colors uppercase"
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.15, duration: 0.2 }}
                >
                  Sign out
                </motion.button>
              </motion.div>
            )}
          </AnimatePresence>
          <button
            className="flex items-center gap-2.5 w-full text-left group"
            onClick={() => setRoleMenuOpen((v) => !v)}
            type="button"
          >
            <motion.span
              className="w-[34px] h-[34px] flex-shrink-0 bg-green text-black flex items-center justify-center h-display text-[13px]"
              whileHover={{ scale: 1.08 }}
              whileTap={{ scale: 0.95 }}
              transition={springs.snappy}
            >
              {roleInitials[role]}
            </motion.span>
            <span className="min-w-0">
              <div className="text-xs tracking-wide truncate group-hover:text-green transition-colors">{roleName[role]}</div>
              <div className="text-[10px] text-textDim tracking-wide mt-0.5 truncate">{roleTitle[role]}</div>
            </span>
          </button>
        </div>
      </aside>
      {/* Mobile backdrop */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            className="fixed inset-0 bg-black/70 z-40 lg:hidden"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onCloseMobile}
          />
        )}
      </AnimatePresence>
    </>
  );
}

import { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { MessageSquare, MonitorUp, Users, X } from 'lucide-react';
import { press, ease } from '../../lib/motion';
import { useReducedMotion } from '../../hooks/useReducedMotion';

/**
 * Left-side companion widget. Mirrors AiAssistant's bubble + panel treatment
 * so the two float in balance on opposite corners.
 * Actions are placeholders — wire them to real screen-share / co-op
 * session logic when that backend exists.
 */
export default function ShareWalkWidget() {
  const [open, setOpen] = useState(false);
  const [status, setStatus] = useState(null); // 'share' | 'talk' | null
  const reduced = useReducedMotion();

  function handleAction(kind) {
    setStatus(kind);
    setTimeout(() => {
      setStatus(null);
      setOpen(false);
    }, 1400);
  }

  return (
    <div className="relative shrink-0 flex items-center">
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 8 }}
            transition={{ duration: 0.18, ease: ease.out }}
            className="absolute bottom-full right-0 mb-3.5 w-[214px] bg-black border border-zinc-700 shadow-[0_24px_48px_-12px_rgba(0,0,0,0.9),0_0_36px_-4px_rgba(57,255,20,0.2)] z-[80] overflow-hidden"
          >
            {/* Header */}
            <div className="flex items-center justify-between px-3.5 py-3 border-b border-zinc-800 bg-surface/40">
              <div className="flex items-center gap-2">
                <motion.span
                  className="w-1.5 h-1.5 bg-green rounded-full inline-block"
                  animate={{ scale: [1, 1.4, 1], opacity: [0.7, 1, 0.7] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                />
                <span className="text-[11px] tracking-[2px] uppercase text-white font-medium">Together</span>
              </div>
              <motion.button
                type="button"
                aria-label="Close"
                onClick={() => setOpen(false)}
                whileHover={{ rotate: 90, scale: 1.18, borderColor: '#fff', color: '#fff' }}
                whileTap={{ scale: 0.9 }}
                className="w-6 h-6 border border-borderDim flex items-center justify-center text-textDim hover:text-white shrink-0 transition-colors"
              >
                <X size={12} />
              </motion.button>
            </div>

            {/* Options */}
            <div className="p-2.5 flex flex-col gap-2">
              <motion.button
                type="button"
                onClick={() => handleAction('share')}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.2, delay: 0.05 }}
                whileHover={reduced ? undefined : { x: 5, scale: 1.02, borderColor: 'var(--green)', backgroundColor: 'rgba(57, 255, 20, 0.08)' }}
                whileTap={{ scale: press.tapScale }}
                className="group flex items-center gap-2.5 px-3 py-2.5 bg-surface border border-borderDim text-left transition-all"
              >
                <motion.div
                  className="w-7 h-7 border border-green/40 bg-black flex items-center justify-center shrink-0 group-hover:border-green group-hover:bg-green/10 transition-colors"
                  whileHover={{ rotate: [0, -8, 8, 0], scale: 1.1 }}
                  transition={{ duration: 0.3 }}
                >
                  <MonitorUp size={14} className="text-green transition-transform group-hover:scale-110" />
                </motion.div>
                <div className="min-w-0 flex-1">
                  <div className="text-[10px] tracking-[1px] uppercase text-white font-medium group-hover:text-green transition-colors">Share My Screen</div>
                  {status === 'share' && (
                    <motion.div
                      initial={{ opacity: 0, y: 2 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="text-[9px] text-green mt-0.5 flex items-center gap-1.5"
                    >
                      <motion.span
                        className="w-1.5 h-1.5 bg-green rounded-full"
                        animate={{ scale: [1, 1.5, 1], opacity: [0.4, 1, 0.4] }}
                        transition={{ duration: 0.8, repeat: Infinity }}
                      />
                      Starting share…
                    </motion.div>
                  )}
                </div>
              </motion.button>

              <motion.button
                type="button"
                onClick={() => handleAction('talk')}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.2, delay: 0.1 }}
                whileHover={reduced ? undefined : { x: 5, scale: 1.02, borderColor: 'var(--green)', backgroundColor: 'rgba(57, 255, 20, 0.08)' }}
                whileTap={{ scale: press.tapScale }}
                className="group flex items-center gap-2.5 px-3 py-2.5 bg-surface border border-borderDim text-left transition-all"
              >
                <motion.div
                  className="w-7 h-7 border border-green/40 bg-black flex items-center justify-center shrink-0 group-hover:border-green group-hover:bg-green/10 transition-colors"
                  whileHover={{ rotate: [0, -8, 8, 0], scale: 1.1 }}
                  transition={{ duration: 0.3 }}
                >
                  <MessageSquare size={14} className="text-green transition-transform group-hover:scale-110" />
                </motion.div>
                <div className="min-w-0 flex-1">
                  <div className="text-[10px] tracking-[1px] uppercase text-white font-medium group-hover:text-green transition-colors">Talk With Friend</div>
                  {status === 'talk' && (
                    <motion.div
                      initial={{ opacity: 0, y: 2 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="text-[9px] text-green mt-0.5 flex items-center gap-1.5"
                    >
                      <motion.span
                        className="w-1.5 h-1.5 bg-green rounded-full"
                        animate={{ scale: [1, 1.5, 1], opacity: [0.4, 1, 0.4] }}
                        transition={{ duration: 0.8, repeat: Infinity }}
                      />
                      Connecting with a friend…
                    </motion.div>
                  )}
                </div>
              </motion.button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Button placed after Rudrant Joshi with continuous floating and hover animation */}
      <motion.button
        type="button"
        title="Together (Talk / Share)"
        aria-label={open ? 'Close together panel' : 'Open together panel'}
        onClick={() => setOpen((o) => !o)}
        animate={
          reduced
            ? undefined
            : {
                y: [0, -3, 0],
                boxShadow: [
                  '0 10px 25px -4px rgba(57,255,20,0.45)',
                  '0 12px 35px -2px rgba(57,255,20,0.75)',
                  '0 10px 25px -4px rgba(57,255,20,0.45)',
                ],
              }
        }
        transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
        whileHover={
          reduced
            ? undefined
            : {
                rotate: [0, -10, 8, -4, 0],
                y: -4,
                boxShadow: '0 0 28px rgba(57,255,20,0.95), 0 0 60px rgba(57,255,20,0.45)',
                transition: { duration: 0.38, ease: 'easeInOut' },
              }
        }
        whileTap={{ scale: 0.95 }}
        className={`relative w-14 h-14 rounded-full bg-green text-black flex items-center justify-center shrink-0 shadow-[0_10px_30px_-6px_rgba(57,255,20,0.55)] cursor-pointer outline-none focus:outline-none focus-visible:outline-none focus:ring-0 active:outline-none select-none transition-colors ${
          open ? 'border-0 border-transparent' : 'border-2 border-green'
        }`}
      >
        {/* Subtle radar wave pulse rings */}
        {!open && !reduced && (
          <>
            <motion.span
              className="absolute inset-0 rounded-full border border-green/35 pointer-events-none"
              animate={{ scale: [1, 1.45], opacity: [0.35, 0] }}
              transition={{ duration: 2.4, repeat: Infinity, ease: 'easeOut' }}
            />
            <motion.span
              className="absolute inset-0 rounded-full border border-green/20 pointer-events-none"
              animate={{ scale: [1, 1.65], opacity: [0.2, 0] }}
              transition={{ duration: 2.4, repeat: Infinity, ease: 'easeOut', delay: 1.2 }}
            />
          </>
        )}
        <AnimatePresence initial={false}>
          {open ? (
            <motion.div
              key="close"
              initial={{ opacity: 0, rotate: -45 }}
              animate={{ opacity: 1, rotate: 0 }}
              exit={{ opacity: 0, rotate: 45 }}
              transition={{ duration: 0.15 }}
              className="absolute inset-0 flex items-center justify-center text-black"
            >
              <X size={24} strokeWidth={2.5} />
            </motion.div>
          ) : (
            <motion.div
              key="open"
              initial={{ opacity: 0, rotate: 45 }}
              animate={{ opacity: 1, rotate: 0 }}
              exit={{ opacity: 0, rotate: -45 }}
              transition={{ duration: 0.15 }}
              className="absolute inset-0 flex items-center justify-center text-black"
            >
              <motion.div
                animate={{ y: [0, -1.5, 0] }}
                transition={{ duration: 2.2, repeat: Infinity, ease: 'easeInOut' }}
                className="flex items-center justify-center"
              >
                <Users size={24} strokeWidth={2.2} />
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.button>
    </div>
  );
}

import { AnimatePresence, motion } from 'framer-motion';
import { notificationsData } from '../../data/social';

export default function NotificationPanel({ open, onClose }) {
  return (
    <AnimatePresence>
      {open && (
        <>
          <div className="fixed inset-0 z-[89]" onClick={onClose} />
          <motion.div
            initial={{ opacity: 0, y: -8, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -8, scale: 0.98 }}
            transition={{ duration: 0.18 }}
            className="fixed top-[64px] right-4 sm:right-8 w-[340px] max-w-[92vw] bg-black border border-white z-[90] max-h-[70vh] overflow-y-auto scrollbar-thin"
          >
            {notificationsData.map((n, i) => (
              <div key={i} className="p-4 border-b border-borderDim text-xs last:border-none">
                <div>{n.t}</div>
                <div className="text-textDim text-[10px] tracking-wide mt-1.5 flex justify-between">
                  <span>{n.sub}</span>
                  <span className="text-green cursor-pointer">{n.cta}</span>
                </div>
              </div>
            ))}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

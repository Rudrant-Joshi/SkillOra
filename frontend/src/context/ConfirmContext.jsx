import { createContext, useCallback, useContext, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Button } from '../components/ui/Primitives';

const ConfirmContext = createContext(null);

export function ConfirmProvider({ children }) {
  const [modal, setModal] = useState(null); // {title, message, confirmLabel, resolve}

  const confirm = useCallback(
    ({ title, message, confirmLabel = 'CONFIRM' }) =>
      new Promise((resolve) => {
        setModal({ title, message, confirmLabel, resolve });
      }),
    []
  );

  const close = (result) => {
    modal?.resolve(result);
    setModal(null);
  };

  return (
    <ConfirmContext.Provider value={{ confirm }}>
      {children}
      <AnimatePresence>
        {modal && (
          <motion.div
            className="fixed inset-0 z-[150] flex items-center justify-center bg-black/85 backdrop-blur-sm p-5"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => close(false)}
          >
            <motion.div
              className="w-full max-w-sm bg-black border-2 border-white p-8"
              initial={{ opacity: 0, y: 16, scale: 0.97 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 10, scale: 0.97 }}
              transition={{ duration: 0.2 }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="h-display text-lg">{modal.title || 'Are you sure?'}</div>
              <div className="dim mono text-xs mt-3 leading-relaxed text-textDim">{modal.message}</div>
              <div className="flex gap-3 mt-7">
                <Button tone="secondary" className="w-full justify-center" onClick={() => close(false)}>
                  CANCEL
                </Button>
                <Button tone="primary" className="w-full justify-center" onClick={() => close(true)}>
                  {modal.confirmLabel}
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </ConfirmContext.Provider>
  );
}

export function useConfirm() {
  const ctx = useContext(ConfirmContext);
  if (!ctx) throw new Error('useConfirm must be used within ConfirmProvider');
  return ctx.confirm;
}

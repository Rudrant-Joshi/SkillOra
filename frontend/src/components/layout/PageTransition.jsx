import { motion } from 'framer-motion';
import { ease } from '../../lib/motion';
import { useReducedMotion } from '../../hooks/useReducedMotion';

export default function PageTransition({ children }) {
  const reduced = useReducedMotion();

  if (reduced) {
    return <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.15 }}>{children}</motion.div>;
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 12, filter: 'blur(5px)' }}
      animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
      exit={{ opacity: 0, y: -8, filter: 'blur(4px)' }}
      transition={{ duration: 0.38, ease: ease.out }}
    >
      {children}
    </motion.div>
  );
}

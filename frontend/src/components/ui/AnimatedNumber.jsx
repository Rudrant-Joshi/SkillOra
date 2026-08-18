import { useEffect, useRef, useState } from 'react';
import { motion, useInView, animate } from 'framer-motion';

/** Counts from 0 to `value` when it enters the viewport with spring scale pop. */
export function AnimatedNumber({ value, suffix = '', duration = 1.2, className = '' }) {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: '-20px' });
  const [display, setDisplay] = useState(0);

  useEffect(() => {
    if (!inView) return;
    const controls = animate(0, value, {
      duration,
      ease: [0.16, 1, 0.3, 1],
      onUpdate: (v) => setDisplay(Math.round(v)),
    });
    return () => controls.stop();
  }, [inView, value, duration]);

  return (
    <motion.span
      ref={ref}
      className={`inline-block ${className}`}
      initial={{ scale: 0.85, opacity: 0 }}
      animate={inView ? { scale: 1, opacity: 1 } : { scale: 0.85, opacity: 0 }}
      transition={{ type: 'spring', stiffness: 350, damping: 22 }}
    >
      {display}
      {suffix}
    </motion.span>
  );
}

/** Progress bar that animates its width in from 0 on scroll-into-view with an active glowing shimmer. */
export function ProgressBar({ pct, tone = '' }) {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: '-30px' });
  return (
    <div className="progress-track relative overflow-hidden" ref={ref}>
      <motion.div
        className={`progress-fill relative overflow-hidden ${tone}`}
        initial={{ width: 0 }}
        animate={{ width: inView ? `${pct}%` : 0 }}
        transition={{ duration: 1.15, ease: [0.16, 1, 0.3, 1] }}
      >
        {/* Shimmer laser sweep */}
        <motion.div
          className="absolute inset-0 bg-gradient-to-r from-transparent via-white/40 to-transparent"
          initial={{ x: '-100%' }}
          animate={inView ? { x: '200%' } : { x: '-100%' }}
          transition={{ duration: 1.4, ease: 'easeInOut', delay: 0.2 }}
        />
      </motion.div>
    </div>
  );
}

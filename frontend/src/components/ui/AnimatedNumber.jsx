import { useEffect, useRef, useState } from 'react';
import { motion, useInView, animate } from 'framer-motion';

/** Counts from 0 to `value` when it enters the viewport. */
export function AnimatedNumber({ value, suffix = '', duration = 1.1, className = '' }) {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: '-40px' });
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
    <span ref={ref} className={className}>
      {display}
      {suffix}
    </span>
  );
}

/** Progress bar that animates its width in from 0 on scroll-into-view. */
export function ProgressBar({ pct, tone = '' }) {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: '-40px' });
  return (
    <div className="progress-track" ref={ref}>
      <motion.div
        className={`progress-fill ${tone}`}
        initial={{ width: 0 }}
        animate={{ width: inView ? `${pct}%` : 0 }}
        transition={{ duration: 1.1, ease: [0.16, 1, 0.3, 1] }}
      />
    </div>
  );
}

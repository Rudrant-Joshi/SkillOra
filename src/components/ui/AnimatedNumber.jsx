import { useEffect, useRef, useState } from 'react';
import { motion, useInView, animate } from 'framer-motion';
import { ease, duration as dur } from '../../lib/motionConfig';

/** Counts from 0 to `value` when it enters the viewport. Re-animates on value change. */
export function AnimatedNumber({ value, suffix = '', duration = 1.1, className = '' }) {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: '-40px' });
  const [display, setDisplay] = useState(0);
  const prevValue = useRef(0);

  useEffect(() => {
    if (!inView) return;
    const from = prevValue.current;
    const controls = animate(from, value, {
      duration,
      ease: ease.out,
      onUpdate: (v) => setDisplay(Math.round(v)),
    });
    prevValue.current = value;
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
        initial={{ width: 0, opacity: 0.5 }}
        animate={{
          width: inView ? `${pct}%` : 0,
          opacity: inView ? 1 : 0.5,
        }}
        transition={{
          width: { duration: 1.1, ease: ease.out },
          opacity: { duration: 0.4, delay: 0.1 },
        }}
      />
    </div>
  );
}

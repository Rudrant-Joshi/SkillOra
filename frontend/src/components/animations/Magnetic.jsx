import { useRef } from 'react';
import { motion, useMotionValue, useSpring } from 'framer-motion';
import { spring } from '../../lib/motion';
import { useReducedMotion } from '../../hooks/useReducedMotion';

/**
 * Wrap a button/CTA to make it feel magnetic: it nudges slightly toward
 * the pointer on hover and springs back on leave. Disabled on touch/coarse
 * pointers and when prefers-reduced-motion is set — desktop-only polish.
 */
export function Magnetic({ children, strength = 0.25, className = '', as: Comp = motion.div, ...rest }) {
  const ref = useRef(null);
  const reduced = useReducedMotion();
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const sx = useSpring(x, spring.button);
  const sy = useSpring(y, spring.button);

  const isCoarse = typeof window !== 'undefined' && window.matchMedia?.('(pointer: coarse)').matches;
  const disabled = reduced || isCoarse;

  function handleMove(e) {
    if (disabled || !ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    const relX = e.clientX - (rect.left + rect.width / 2);
    const relY = e.clientY - (rect.top + rect.height / 2);
    x.set(relX * strength);
    y.set(relY * strength);
  }

  function handleLeave() {
    x.set(0);
    y.set(0);
  }

  return (
    <Comp
      ref={ref}
      onPointerMove={handleMove}
      onPointerLeave={handleLeave}
      style={disabled ? undefined : { x: sx, y: sy }}
      whileTap={disabled ? undefined : { scale: 0.97 }}
      className={className}
      {...rest}
    >
      {children}
    </Comp>
  );
}

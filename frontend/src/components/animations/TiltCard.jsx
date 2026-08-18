import { useRef } from 'react';
import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion';
import { spring } from '../../lib/motion';
import { useReducedMotion } from '../../hooks/useReducedMotion';

/**
 * Extremely subtle pointer-driven 3D tilt (±2deg). Reserve this for a
 * small number of "featured" surfaces — hero cards, the passport, major
 * analysis panels — not every card in the app.
 */
export function TiltCard({ children, className = '', maxTilt = 2, ...rest }) {
  const ref = useRef(null);
  const reduced = useReducedMotion();
  const isCoarse = typeof window !== 'undefined' && window.matchMedia?.('(pointer: coarse)').matches;
  const disabled = reduced || isCoarse;

  const px = useMotionValue(0.5);
  const py = useMotionValue(0.5);
  const spx = useSpring(px, spring.soft);
  const spy = useSpring(py, spring.soft);
  const rotateX = useTransform(spy, [0, 1], [maxTilt, -maxTilt]);
  const rotateY = useTransform(spx, [0, 1], [-maxTilt, maxTilt]);

  function handleMove(e) {
    if (disabled || !ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    px.set((e.clientX - rect.left) / rect.width);
    py.set((e.clientY - rect.top) / rect.height);
  }

  function handleLeave() {
    px.set(0.5);
    py.set(0.5);
  }

  return (
    <motion.div
      ref={ref}
      onPointerMove={handleMove}
      onPointerLeave={handleLeave}
      style={disabled ? undefined : { rotateX, rotateY, transformPerspective: 900 }}
      className={className}
      {...rest}
    >
      {children}
    </motion.div>
  );
}

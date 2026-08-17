import { useRef, useCallback } from 'react';
import { motion, useMotionValue, useSpring } from 'framer-motion';
import { isTouchDevice, prefersReducedMotion } from '../../lib/motionConfig';

/**
 * Magnetic wrapper — child element subtly follows the cursor when hovered.
 * Strength controls pull distance (px). Spring return on leave.
 * Disabled on touch devices.
 */
export default function Magnetic({
  children,
  strength = 0.3,
  radius = 0.5,
  className = '',
  as = 'div',
  ...rest
}) {
  const ref = useRef(null);
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const springX = useSpring(x, { stiffness: 350, damping: 20 });
  const springY = useSpring(y, { stiffness: 350, damping: 20 });

  const disabled = isTouchDevice() || prefersReducedMotion();

  const handleMouse = useCallback(
    (e) => {
      if (disabled || !ref.current) return;
      const rect = ref.current.getBoundingClientRect();
      const cx = rect.left + rect.width / 2;
      const cy = rect.top + rect.height / 2;
      const dx = e.clientX - cx;
      const dy = e.clientY - cy;
      x.set(dx * strength);
      y.set(dy * strength);
    },
    [disabled, strength, x, y]
  );

  const handleLeave = useCallback(() => {
    x.set(0);
    y.set(0);
  }, [x, y]);

  const Comp = motion[as] || motion.div;

  return (
    <Comp
      ref={ref}
      onMouseMove={disabled ? undefined : handleMouse}
      onMouseLeave={disabled ? undefined : handleLeave}
      style={{ x: disabled ? 0 : springX, y: disabled ? 0 : springY }}
      className={className}
      {...rest}
    >
      {children}
    </Comp>
  );
}

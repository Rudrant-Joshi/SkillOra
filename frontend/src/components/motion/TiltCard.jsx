import { useRef, useCallback } from 'react';
import { motion, useMotionValue, useSpring } from 'framer-motion';
import { isTouchDevice, prefersReducedMotion } from '../../lib/motionConfig';

/**
 * Clean 3D perspective tilt card — crisp motion, zero shiny background washes.
 */
export default function TiltCard({
  children,
  className = '',
  tiltMax = 3.5,
  perspective = 900,
  scale = 1.008,
  ...rest
}) {
  const ref = useRef(null);

  const rotX = useMotionValue(0);
  const rotY = useMotionValue(0);

  const springRotX = useSpring(rotX, { stiffness: 350, damping: 30 });
  const springRotY = useSpring(rotY, { stiffness: 350, damping: 30 });

  const disabled = isTouchDevice() || prefersReducedMotion();

  const handleMove = useCallback(
    (e) => {
      if (disabled || !ref.current) return;
      const rect = ref.current.getBoundingClientRect();
      const px = (e.clientX - rect.left) / rect.width;
      const py = (e.clientY - rect.top) / rect.height;
      rotX.set((py - 0.5) * -tiltMax * 2);
      rotY.set((px - 0.5) * tiltMax * 2);
    },
    [disabled, tiltMax, rotX, rotY]
  );

  const handleLeave = useCallback(() => {
    rotX.set(0);
    rotY.set(0);
  }, [rotX, rotY]);

  return (
    <motion.div
      ref={ref}
      onMouseMove={disabled ? undefined : handleMove}
      onMouseLeave={disabled ? undefined : handleLeave}
      style={{
        perspective,
        transformStyle: 'preserve-3d',
      }}
      className={className}
      {...rest}
    >
      <motion.div
        style={{
          rotateX: disabled ? 0 : springRotX,
          rotateY: disabled ? 0 : springRotY,
          transformStyle: 'preserve-3d',
          width: '100%',
          height: '100%',
          position: 'relative',
        }}
        whileHover={disabled ? undefined : { scale }}
        transition={{ duration: 0.15 }}
      >
        {children}
      </motion.div>
    </motion.div>
  );
}

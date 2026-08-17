import { useRef } from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';
import { prefersReducedMotion } from '../../lib/motionConfig';

/**
 * Scroll-linked parallax wrapper.
 * speed < 1: moves slower than scroll (background feel)
 * speed > 1: moves faster than scroll (foreground feel)
 * speed = 1: normal scroll (no parallax)
 */
export default function Parallax({
  children,
  speed = 0.5,
  className = '',
  direction = 'y',
  ...rest
}) {
  const ref = useRef(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ['start end', 'end start'],
  });

  const range = 50 * (speed - 1);
  const transform = useTransform(scrollYProgress, [0, 1], [range, -range]);

  if (prefersReducedMotion()) {
    return (
      <div ref={ref} className={className} {...rest}>
        {children}
      </div>
    );
  }

  const style = direction === 'x' ? { x: transform } : { y: transform };

  return (
    <div ref={ref} className={className} {...rest}>
      <motion.div style={style}>
        {children}
      </motion.div>
    </div>
  );
}

import { motion } from 'framer-motion';
import { ease, duration, prefersReducedMotion } from '../../lib/motionConfig';

/**
 * High-performance, GPU-only scroll reveal (opacity & transform).
 * No heavy CSS filters or blur animations that trigger layout repaints.
 */
export function Reveal({
  children,
  delay = 0,
  y,
  x,
  direction = 'up',
  mode = 'default',
  className = '',
  as: Comp = motion.div,
  ...rest
}) {
  if (prefersReducedMotion()) {
    const Tag = Comp === motion.div ? 'div' : Comp;
    return <Tag className={className} {...rest}>{children}</Tag>;
  }

  let initial, target;

  if (mode === 'scale') {
    initial = { opacity: 0, scale: 0.97 };
    target = { opacity: 1, scale: 1 };
  } else if (mode === 'clipPath') {
    initial = { opacity: 0, clipPath: 'inset(100% 0% 0% 0%)' };
    target = { opacity: 1, clipPath: 'inset(0% 0% 0% 0%)' };
  } else {
    const dist = 16;
    const translate =
      direction === 'down'  ? { y: y ?? -dist } :
      direction === 'left'  ? { x: x ?? dist } :
      direction === 'right' ? { x: x ?? -dist } :
                              { y: y ?? dist };

    initial = { opacity: 0, ...translate };
    target = { opacity: 1, y: 0, x: 0 };
  }

  return (
    <Comp
      initial={initial}
      whileInView={target}
      viewport={{ once: true, margin: '-20px' }}
      transition={{ duration: 0.25, delay, ease: ease.out }}
      className={className}
      {...rest}
    >
      {children}
    </Comp>
  );
}

export function StaggerContainer({ children, className = '', stagger: staggerVal = 0.04 }) {
  return (
    <motion.div
      initial="hidden"
      whileInView="show"
      viewport={{ once: true, margin: '-20px' }}
      variants={{
        hidden: {},
        show: {
          transition: {
            staggerChildren: staggerVal,
          },
        },
      }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

export function StaggerItem({ children, className = '', direction = 'up' }) {
  if (prefersReducedMotion()) {
    return <div className={className}>{children}</div>;
  }

  const dist = 12;
  const translate =
    direction === 'left'  ? { x: dist, y: 0 } :
    direction === 'right' ? { x: -dist, y: 0 } :
    direction === 'down'  ? { y: -dist } :
                            { y: dist };

  return (
    <motion.div
      variants={{
        hidden: { opacity: 0, ...translate },
        show:   { opacity: 1, y: 0, x: 0 },
      }}
      transition={{ duration: 0.2, ease: ease.out }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

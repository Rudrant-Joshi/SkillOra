import { motion } from 'framer-motion';
import { ease, directionOffset } from '../../lib/motion';
import { useReducedMotion } from '../../hooks/useReducedMotion';

/**
 * Reveal — scroll/mount entrance primitive.
 * Optimized for ultra-smooth 60/120fps hardware-accelerated sliding on scroll.
 */
export function Reveal({
  children,
  delay = 0,
  duration = 0.42,
  distance = 18,
  direction = 'up',
  variant = 'soft', // soft | scale | slide | none
  scale,
  once = true,
  amount = 0.05,
  margin = '0px 0px -40px 0px',
  easing = ease.out,
  className = '',
  style = {},
  as: Comp = motion.div,
  ...rest
}) {
  const reduced = useReducedMotion();

  const resolvedScale = scale ?? (variant === 'scale' ? 0.97 : undefined);
  const offset = reduced ? {} : directionOffset(direction, distance);

  const initial = {
    opacity: 0,
    ...offset,
    ...(resolvedScale !== undefined ? { scale: resolvedScale } : {}),
  };
  const animateTo = {
    opacity: 1,
    y: 0,
    x: 0,
    ...(resolvedScale !== undefined ? { scale: 1 } : {}),
  };

  return (
    <Comp
      initial={reduced ? { opacity: 0 } : initial}
      whileInView={reduced ? { opacity: 1 } : animateTo}
      viewport={{ once, margin, amount }}
      transition={{ duration: reduced ? 0.15 : duration, delay: reduced ? 0 : delay, ease: easing }}
      className={className}
      style={{ willChange: 'transform, opacity', ...style }}
      {...rest}
    >
      {children}
    </Comp>
  );
}

/** Same as Reveal but animates on mount instead of on scroll-into-view. */
export function RevealMount({ children, delay = 0, distance = 16, direction = 'up', className = '', style = {}, ...rest }) {
  const reduced = useReducedMotion();
  const offset = reduced ? {} : directionOffset(direction, distance);
  return (
    <motion.div
      initial={reduced ? { opacity: 0 } : { opacity: 0, ...offset }}
      animate={{ opacity: 1, y: 0, x: 0 }}
      transition={{ duration: reduced ? 0.15 : 0.4, delay: reduced ? 0 : delay, ease: ease.out }}
      className={className}
      style={{ willChange: 'transform, opacity', ...style }}
      {...rest}
    >
      {children}
    </motion.div>
  );
}

/** Stagger container — wrap a list of <StaggerItem /> to cascade their entrance. */
export function StaggerContainer({ children, className = '', stagger = 0.05, once = true, margin = '0px 0px -40px 0px', delayChildren = 0, ...rest }) {
  const reduced = useReducedMotion();
  return (
    <motion.div
      initial="hidden"
      whileInView="show"
      viewport={{ once, margin, amount: 0.05 }}
      variants={{ hidden: {}, show: { transition: { staggerChildren: reduced ? 0 : stagger, delayChildren } } }}
      className={className}
      {...rest}
    >
      {children}
    </motion.div>
  );
}

export function StaggerItem({ children, className = '', direction = 'up', distance = 14, scale, style = {}, as: Comp = motion.div, ...rest }) {
  const reduced = useReducedMotion();
  const offset = directionOffset(direction, distance);
  return (
    <Comp
      variants={{
        hidden: reduced
          ? { opacity: 0 }
          : { opacity: 0, ...offset, ...(scale ? { scale } : {}) },
        show: {
          opacity: 1,
          y: 0,
          x: 0,
          ...(scale ? { scale: 1 } : {}),
          transition: { duration: reduced ? 0.15 : 0.38, ease: ease.out },
        },
      }}
      className={className}
      style={{ willChange: 'transform, opacity', ...style }}
      {...rest}
    >
      {children}
    </Comp>
  );
}

/** Assembles a page header in sequence: eyebrow → title → subtitle → actions. */
export function SequencedGroup({ children, gap = 0.06 }) {
  return (
    <motion.div initial="hidden" animate="show" variants={{ hidden: {}, show: { transition: { staggerChildren: gap } } }}>
      {children}
    </motion.div>
  );
}

export function SequencedItem({ children, direction = 'up', distance = 10, className = '' }) {
  const reduced = useReducedMotion();
  const offset = directionOffset(direction, distance);
  return (
    <motion.div
      variants={{
        hidden: reduced ? { opacity: 0 } : { opacity: 0, ...offset },
        show: { opacity: 1, y: 0, x: 0, transition: { duration: reduced ? 0.15 : 0.4, ease: ease.out } },
      }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

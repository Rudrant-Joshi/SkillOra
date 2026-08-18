import { motion } from 'framer-motion';
import { ease, directionOffset } from '../../lib/motion';
import { useReducedMotion } from '../../hooks/useReducedMotion';

/**
 * Reveal — scroll/mount entrance primitive.
 * Supports multiple rich elemental variants: pop, scale, slideLeft, slideRight, soft.
 */
export function Reveal({
  children,
  delay = 0,
  duration = 0.45,
  distance = 20,
  direction = 'up',
  variant = 'pop', // pop | scale | slideLeft | slideRight | soft | none
  scale,
  once = true,
  amount = 0.08,
  margin = '0px 0px -40px 0px',
  easing = ease.out,
  className = '',
  style = {},
  as: Comp = motion.div,
  ...rest
}) {
  const reduced = useReducedMotion();

  const isPop = variant === 'pop';
  const resolvedScale = scale ?? (isPop ? 0.92 : variant === 'scale' ? 0.96 : undefined);
  const resolvedDir = variant === 'slideLeft' ? 'left' : variant === 'slideRight' ? 'right' : direction;
  const offset = reduced ? {} : directionOffset(resolvedDir, distance);

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

  const transition = isPop && !reduced
    ? { type: 'spring', stiffness: 320, damping: 24, delay }
    : { duration: reduced ? 0.15 : duration, delay: reduced ? 0 : delay, ease: easing };

  return (
    <Comp
      initial={reduced ? { opacity: 0 } : initial}
      whileInView={reduced ? { opacity: 1 } : animateTo}
      viewport={{ once, margin, amount }}
      transition={transition}
      className={className}
      style={{ willChange: 'transform, opacity', ...style }}
      {...rest}
    >
      {children}
    </Comp>
  );
}

/** LaserDivider — animated horizontal rule that sweeps open on scroll into view. */
export function LaserDivider({ className = '' }) {
  const reduced = useReducedMotion();
  return (
    <div className={`relative my-6 overflow-hidden ${className}`}>
      <motion.div
        initial={reduced ? { scaleX: 1 } : { scaleX: 0, opacity: 0 }}
        whileInView={{ scaleX: 1, opacity: 1 }}
        viewport={{ once: true, margin: '0px 0px -30px 0px' }}
        transition={{ duration: 0.65, ease: [0.16, 1, 0.3, 1] }}
        className="h-[1px] bg-gradient-to-r from-transparent via-green/70 to-transparent origin-center w-full"
      />
    </div>
  );
}

/** Stagger container — wrap a list of <StaggerItem /> to cascade their pop-up entrance. */
export function StaggerContainer({ children, className = '', stagger = 0.06, once = true, margin = '0px 0px -40px 0px', delayChildren = 0.04, ...rest }) {
  const reduced = useReducedMotion();
  return (
    <motion.div
      initial="hidden"
      whileInView="show"
      viewport={{ once, margin, amount: 0.05 }}
      variants={{
        hidden: {},
        show: {
          transition: {
            staggerChildren: reduced ? 0 : stagger,
            delayChildren: reduced ? 0 : delayChildren,
          },
        },
      }}
      className={className}
      {...rest}
    >
      {children}
    </motion.div>
  );
}

/** StaggerItem — spring pop-up element inside StaggerContainer. */
export function StaggerItem({
  children,
  className = '',
  direction = 'up',
  distance = 16,
  scale = 0.94,
  style = {},
  as: Comp = motion.div,
  ...rest
}) {
  const reduced = useReducedMotion();
  const offset = directionOffset(direction, distance);
  return (
    <Comp
      variants={{
        hidden: reduced
          ? { opacity: 0 }
          : { opacity: 0, ...offset, scale },
        show: {
          opacity: 1,
          y: 0,
          x: 0,
          scale: 1,
          transition: reduced
            ? { duration: 0.15 }
            : { type: 'spring', stiffness: 360, damping: 25 },
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

/** SequencedGroup — assembles page headers with progressive stagger. */
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
        hidden: reduced ? { opacity: 0 } : { opacity: 0, ...offset, scale: 0.98 },
        show: {
          opacity: 1,
          y: 0,
          x: 0,
          scale: 1,
          transition: { duration: reduced ? 0.15 : 0.42, ease: [0.16, 1, 0.3, 1] },
        },
      }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

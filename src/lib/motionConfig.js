/**
 * Motion Design System — Centralized tokens & utilities
 * All animation parameters flow from here to ensure visual cohesion.
 */

// ─── Spring Presets ─────────────────────────────────────────────
export const springs = {
  snappy:    { type: 'spring', stiffness: 400, damping: 30 },
  smooth:    { type: 'spring', stiffness: 200, damping: 24 },
  gentle:    { type: 'spring', stiffness: 120, damping: 20 },
  bouncy:    { type: 'spring', stiffness: 300, damping: 15 },
  // For page transitions & large movements
  cinematic: { type: 'spring', stiffness: 80, damping: 18 },
};

// ─── Easing Curves ──────────────────────────────────────────────
export const ease = {
  out:       [0.16, 1, 0.3, 1],      // smooth deceleration (existing app standard)
  inOut:     [0.4, 0, 0.2, 1],       // material-style in-out
  snap:      [0.6, 0.01, 0, 0.9],    // fast start, controlled end
  soft:      [0.25, 0.46, 0.45, 0.94],
};

// ─── Duration Scale ─────────────────────────────────────────────
export const duration = {
  instant: 0.1,
  fast:    0.15,
  normal:  0.3,
  medium:  0.4,
  slow:    0.5,
  slower:  0.7,
  cinematic: 0.9,
};

// ─── Stagger Timing ─────────────────────────────────────────────
export const stagger = {
  fast:   0.04,
  normal: 0.06,
  slow:   0.1,
  cards:  0.08,
};

// ─── Reveal Variants ───────────────────────────────────────────
// Each returns { hidden, show } variant pair

export const fadeUp = (y = 24, blur = 6) => ({
  hidden: { opacity: 0, y, filter: `blur(${blur}px)` },
  show:   { opacity: 1, y: 0, filter: 'blur(0px)' },
});

export const fadeDown = (y = -24, blur = 6) => ({
  hidden: { opacity: 0, y, filter: `blur(${blur}px)` },
  show:   { opacity: 1, y: 0, filter: 'blur(0px)' },
});

export const fadeLeft = (x = -30) => ({
  hidden: { opacity: 0, x },
  show:   { opacity: 1, x: 0 },
});

export const fadeRight = (x = 30) => ({
  hidden: { opacity: 0, x },
  show:   { opacity: 1, x: 0 },
});

export const scaleIn = (s = 0.94) => ({
  hidden: { opacity: 0, scale: s },
  show:   { opacity: 1, scale: 1 },
});

export const blurIn = (blur = 12) => ({
  hidden: { opacity: 0, filter: `blur(${blur}px)` },
  show:   { opacity: 1, filter: 'blur(0px)' },
});

// ─── Container Variant (for stagger orchestration) ─────────────
export const staggerContainer = (staggerVal = stagger.normal) => ({
  hidden: {},
  show: {
    transition: {
      staggerChildren: staggerVal,
      delayChildren: 0.05,
    },
  },
});

// ─── Child Variant (for items inside stagger container) ────────
export const staggerChild = {
  hidden: { opacity: 0, y: 16, filter: 'blur(4px)' },
  show:   { opacity: 1, y: 0, filter: 'blur(0px)' },
};

// ─── Page Transition Variants ──────────────────────────────────
export const pageVariants = {
  initial: { opacity: 0, y: 14, scale: 0.99, filter: 'blur(6px)' },
  animate: { opacity: 1, y: 0, scale: 1, filter: 'blur(0px)' },
  exit:    { opacity: 0, y: -8, scale: 0.99, filter: 'blur(4px)' },
};

// ─── Modal Variants ────────────────────────────────────────────
export const modalBackdrop = {
  hidden: { opacity: 0 },
  show:   { opacity: 1 },
  exit:   { opacity: 0 },
};

export const modalContent = {
  hidden: { opacity: 0, y: 20, scale: 0.95, filter: 'blur(4px)' },
  show:   { opacity: 1, y: 0, scale: 1, filter: 'blur(0px)' },
  exit:   { opacity: 0, y: 12, scale: 0.97, filter: 'blur(2px)' },
};

// ─── Drawer Variants ───────────────────────────────────────────
export const drawerSlide = (side = 'right', width = 380) => {
  const x = side === 'right' ? width : -width;
  return {
    hidden: { x },
    show:   { x: 0 },
    exit:   { x },
  };
};

// ─── Utility: Check reduced motion ────────────────────────────
export function prefersReducedMotion() {
  if (typeof window === 'undefined') return false;
  return window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
}

// ─── Utility: Check if touch device ───────────────────────────
export function isTouchDevice() {
  if (typeof window === 'undefined') return false;
  return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
}

// ─── Utility: Lerp ────────────────────────────────────────────
export function lerp(a, b, t) {
  return a + (b - a) * t;
}

// ─── Utility: Clamp ───────────────────────────────────────────
export function clamp(val, min, max) {
  return Math.max(min, Math.min(max, val));
}

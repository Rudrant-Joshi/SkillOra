/**
 * Central motion system for AI SkillGraph.
 * Every duration, easing curve and spring used across the app should
 * come from here so motion stays consistent instead of hand-tuned per file.
 */

// ---- Easing --------------------------------------------------------------
export const ease = {
  out: [0.16, 1, 0.3, 1], // elegant entrances
  inOut: [0.65, 0, 0.35, 1], // state-to-state transitions
  standard: [0.4, 0, 0.2, 1],
};

// ---- Durations (seconds) --------------------------------------------------
// Level 1 micro / Level 2 standard / Level 3 featured / Level 4 cinematic
export const dur = {
  micro: 0.14,
  standard: 0.22,
  reveal: 0.42,
  featured: 0.55,
  cinematic: 0.65,
};

// ---- Springs ---------------------------------------------------------------
export const spring = {
  snappy: { type: 'spring', stiffness: 420, damping: 32, mass: 0.6 },
  soft: { type: 'spring', stiffness: 260, damping: 26, mass: 0.7 },
  button: { type: 'spring', stiffness: 500, damping: 28, mass: 0.5 },
};

// ---- Press / hover scale tokens -------------------------------------------
export const press = {
  hoverScale: 1.045,
  tapScale: 0.95,
  cardLift: -10,
  cardLiftLg: -14,
};

// ---- Vibration feedback (used on click/tap of interactive surfaces) ------
// A short, punchy shake so a click reads as unmistakably registered.
export const vibrate = {
  x: [0, -7, 7, -5, 5, -3, 3, -1, 1, 0],
  transition: { duration: 0.38, ease: 'easeInOut' },
};

export const vibrateStrong = {
  x: [0, -10, 10, -8, 8, -5, 5, -2, 2, 0],
  y: [0, 1, -1, 1, -1, 0, 0, 0, 0, 0],
  transition: { duration: 0.42, ease: 'easeInOut' },
};

// ---- Heavy hover treatment for cards ---------------------------------------
export const cardHover = {
  y: press.cardLift,
  scale: 1.025,
  borderColor: '#39FF14',
  boxShadow: '0 24px 48px -12px rgba(0,0,0,0.65), 0 0 0 1px rgba(57,255,20,0.25), 0 0 32px -4px rgba(57,255,20,0.35)',
  transition: { type: 'spring', stiffness: 340, damping: 20, mass: 0.7 },
};

export const cardHoverFeatured = {
  y: press.cardLiftLg,
  scale: 1.035,
  borderColor: '#39FF14',
  boxShadow: '0 32px 64px -14px rgba(0,0,0,0.7), 0 0 0 1.5px rgba(57,255,20,0.35), 0 0 48px -2px rgba(57,255,20,0.45)',
  transition: { type: 'spring', stiffness: 300, damping: 18, mass: 0.8 },
};

// ---- Shared variants --------------------------------------------------------
export const fadeUp = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0, transition: { duration: dur.reveal, ease: ease.out } },
};

export const scaleIn = {
  hidden: { opacity: 0, scale: 0.96 },
  show: { opacity: 1, scale: 1, transition: { duration: dur.reveal, ease: ease.out } },
};

export const dropdownVariants = {
  hidden: { opacity: 0, y: -6, scale: 0.98 },
  show: { opacity: 1, y: 0, scale: 1, transition: { duration: dur.standard, ease: ease.out } },
  exit: { opacity: 0, y: -4, scale: 0.98, transition: { duration: dur.micro, ease: ease.standard } },
};

export const modalVariants = {
  backdrop: {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { duration: dur.standard } },
    exit: { opacity: 0, transition: { duration: dur.micro } },
  },
  panel: {
    hidden: { opacity: 0, scale: 0.96, y: 10 },
    show: { opacity: 1, scale: 1, y: 0, transition: { duration: dur.reveal, ease: ease.out } },
    exit: { opacity: 0, scale: 0.97, y: 6, transition: { duration: dur.micro, ease: ease.standard } },
  },
};

export const toastVariants = {
  hidden: { opacity: 0, x: 30 },
  show: { opacity: 1, x: 0, transition: { duration: dur.standard, ease: ease.out } },
  exit: { opacity: 0, x: 30, transition: { duration: dur.micro } },
};

export const listItemVariants = {
  hidden: { opacity: 0, y: 10, scale: 0.98 },
  show: { opacity: 1, y: 0, scale: 1, transition: { duration: dur.reveal, ease: ease.out } },
  exit: { opacity: 0, scale: 0.98, transition: { duration: dur.micro } },
};

// Direction offsets used by <Reveal direction="..." />
export const directionOffset = (direction, distance) => {
  switch (direction) {
    case 'down':
      return { y: -distance };
    case 'left':
      return { x: distance };
    case 'right':
      return { x: -distance };
    case 'none':
      return {};
    case 'up':
    default:
      return { y: distance };
  }
};

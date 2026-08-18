import { useRef } from 'react';

/**
 * Tracks pointer position over its child and exposes it as CSS vars
 * (--mouse-x / --mouse-y) so a ::before radial-gradient (see .pointer-glow
 * in globals.css) can follow the cursor. Extremely low-opacity by design —
 * a premium material response, not a neon effect. No-op on touch.
 */
export function PointerGlow({ children, className = '', ...rest }) {
  const ref = useRef(null);

  function handleMove(e) {
    const el = ref.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    el.style.setProperty('--mouse-x', `${e.clientX - rect.left}px`);
    el.style.setProperty('--mouse-y', `${e.clientY - rect.top}px`);
  }

  return (
    <div ref={ref} className={`pointer-glow ${className}`} onPointerMove={handleMove} {...rest}>
      {children}
    </div>
  );
}

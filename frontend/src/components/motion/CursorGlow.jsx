import { useEffect, useRef } from 'react';
import { isTouchDevice, prefersReducedMotion, lerp } from '../../lib/motionConfig';

/**
 * High-intensity interactive cursor glow aura.
 * Casts a smooth neon-green dynamic radiant spotlight wherever the cursor moves.
 */
export default function CursorGlow() {
  const glowRef = useRef(null);
  const posRef = useRef({ x: -1000, y: -1000, targetX: -1000, targetY: -1000 });

  useEffect(() => {
    if (isTouchDevice() || prefersReducedMotion()) return;

    const el = glowRef.current;
    if (!el) return;

    let rafId;

    const handleMouseMove = (e) => {
      posRef.current.targetX = e.clientX;
      posRef.current.targetY = e.clientY;
    };

    const handleMouseLeave = () => {
      posRef.current.targetX = -1000;
      posRef.current.targetY = -1000;
    };

    const update = () => {
      const p = posRef.current;
      p.x = lerp(p.x, p.targetX, 0.12);
      p.y = lerp(p.y, p.targetY, 0.12);

      if (el) {
        el.style.background = `
          radial-gradient(650px circle at ${p.x}px ${p.y}px, rgba(57, 255, 20, 0.16), rgba(57, 255, 20, 0.04) 45%, transparent 75%),
          radial-gradient(220px circle at ${p.x}px ${p.y}px, rgba(57, 255, 20, 0.24), transparent 70%)
        `;
      }

      rafId = requestAnimationFrame(update);
    };

    window.addEventListener('mousemove', handleMouseMove, { passive: true });
    window.addEventListener('mouseleave', handleMouseLeave);
    rafId = requestAnimationFrame(update);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseleave', handleMouseLeave);
      cancelAnimationFrame(rafId);
    };
  }, []);

  if (isTouchDevice() || prefersReducedMotion()) return null;

  return (
    <div
      ref={glowRef}
      aria-hidden="true"
      style={{
        position: 'fixed',
        inset: 0,
        width: '100vw',
        height: '100vh',
        pointerEvents: 'none',
        zIndex: 1,
        transition: 'opacity 0.2s ease',
      }}
    />
  );
}

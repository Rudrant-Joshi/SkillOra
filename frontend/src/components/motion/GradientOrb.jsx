import { useEffect, useRef } from 'react';
import { prefersReducedMotion } from '../../lib/motionConfig';

/**
 * Slow-moving ambient radial gradient decoration with high-intensity neon glow.
 * Creates an immersive breathing cyber aurora in the background.
 */
export default function GradientOrb({
  color = 'rgba(57, 255, 20, 0.22)',
  size = 750,
  className = '',
  style: propStyle = {},
}) {
  const ref = useRef(null);

  useEffect(() => {
    if (prefersReducedMotion()) return;

    const el = ref.current;
    if (!el) return;

    let time = 0;
    let rafId;

    const animate = () => {
      time += 0.004;
      const x = 50 + Math.sin(time) * 18;
      const y = 50 + Math.cos(time * 0.7) * 14;
      const scale = 1 + Math.sin(time * 0.5) * 0.12;

      el.style.transform = `translate(${x - 50}%, ${y - 50}%) scale(${scale})`;

      rafId = requestAnimationFrame(animate);
    };

    rafId = requestAnimationFrame(animate);

    return () => cancelAnimationFrame(rafId);
  }, []);

  if (prefersReducedMotion()) return null;

  return (
    <div
      ref={ref}
      aria-hidden="true"
      className={className}
      style={{
        position: 'absolute',
        width: size,
        height: size,
        borderRadius: '50%',
        background: `radial-gradient(circle, ${color} 0%, rgba(57, 255, 20, 0.08) 40%, transparent 70%)`,
        filter: 'blur(40px)',
        pointerEvents: 'none',
        zIndex: 0,
        ...propStyle,
      }}
    />
  );
}

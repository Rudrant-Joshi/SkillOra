import { useRef, useState, useCallback } from 'react';
import { isTouchDevice, prefersReducedMotion } from '../../lib/motionConfig';

/**
 * High-intensity spotlight effect for cards and panels.
 * Follows the mouse with a vivid neon-green spotlight aura over the component.
 */
export default function Spotlight({
  children,
  className = '',
  color = 'rgba(57, 255, 20, 0.28)',
  size = 360,
  ...rest
}) {
  const containerRef = useRef(null);
  const [pos, setPos] = useState({ x: 0, y: 0 });
  const [isHovered, setIsHovered] = useState(false);

  const disabled = isTouchDevice() || prefersReducedMotion();

  const handleMouseMove = useCallback((e) => {
    if (disabled || !containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    setPos({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
    });
  }, [disabled]);

  return (
    <div
      ref={containerRef}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={`relative overflow-hidden ${className}`}
      {...rest}
    >
      {!disabled && isHovered && (
        <div
          aria-hidden="true"
          style={{
            position: 'absolute',
            inset: 0,
            pointerEvents: 'none',
            background: `radial-gradient(${size}px circle at ${pos.x}px ${pos.y}px, ${color}, transparent 80%)`,
            transition: 'opacity 0.15s ease',
            zIndex: 1,
          }}
        />
      )}
      <div className="relative z-[2]">
        {children}
      </div>
    </div>
  );
}

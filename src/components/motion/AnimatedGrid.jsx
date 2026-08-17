import { useEffect, useRef } from 'react';
import { isTouchDevice, prefersReducedMotion, lerp } from '../../lib/motionConfig';

/**
 * High-intensity animated cyber grid background with glowing nodes and dynamic cursor web.
 * Responds to scroll position and cursor proximity with bright neon green radiance.
 * Active across the entire website for maximum visual impact.
 */
export default function AnimatedGrid({ className = '' }) {
  const canvasRef = useRef(null);
  const mouse = useRef({ x: -2000, y: -2000 });
  const smoothMouse = useRef({ x: -2000, y: -2000 });

  useEffect(() => {
    if (prefersReducedMotion()) return;

    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    let rafId;
    let scrollY = 0;
    let time = 0;
    const spacing = 44;
    const baseDotRadius = 1.4;
    const influenceRadius = 180;

    const resize = () => {
      const dpr = window.devicePixelRatio || 1;
      canvas.width = canvas.offsetWidth * dpr;
      canvas.height = canvas.offsetHeight * dpr;
      ctx.scale(dpr, dpr);
    };

    const isTouch = isTouchDevice();

    const handleMouse = (e) => {
      if (isTouch) return;
      const rect = canvas.getBoundingClientRect();
      mouse.current.x = e.clientX - rect.left;
      mouse.current.y = e.clientY - rect.top;
    };

    const handleMouseLeave = () => {
      mouse.current.x = -2000;
      mouse.current.y = -2000;
    };

    const handleScroll = () => {
      scrollY = window.scrollY;
    };

    const draw = () => {
      time += 0.02;
      const w = canvas.offsetWidth;
      const h = canvas.offsetHeight;

      if (!isTouch) {
        smoothMouse.current.x = lerp(smoothMouse.current.x, mouse.current.x, 0.08);
        smoothMouse.current.y = lerp(smoothMouse.current.y, mouse.current.y, 0.08);
      }

      ctx.clearRect(0, 0, w, h);

      const offsetY = (scrollY * 0.06) % spacing;
      const activeNodes = [];

      for (let x = 0; x < w + spacing; x += spacing) {
        for (let y = -spacing + offsetY; y < h + spacing; y += spacing) {
          // Subtle organic wave pulse
          const wave = Math.sin(time + x * 0.02 + y * 0.02) * 0.08;
          let alpha = 0.22 + wave;
          let radius = baseDotRadius;
          let isHovered = false;

          if (!isTouch) {
            const dx = smoothMouse.current.x - x;
            const dy = smoothMouse.current.y - y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist < influenceRadius) {
              const boost = 1 - dist / influenceRadius;
              alpha = 0.22 + boost * 0.75;
              radius = baseDotRadius + boost * 1.8;
              isHovered = true;
              activeNodes.push({ x, y, dist, boost });
            }
          }

          // Draw high-intensity glowing dot
          ctx.beginPath();
          ctx.arc(x, y, radius, 0, Math.PI * 2);
          if (isHovered) {
            ctx.shadowBlur = 10;
            ctx.shadowColor = '#39ff14';
            ctx.fillStyle = `rgba(57, 255, 20, ${alpha})`;
          } else {
            ctx.shadowBlur = 0;
            ctx.fillStyle = `rgba(57, 255, 20, ${alpha})`;
          }
          ctx.fill();
        }
      }

      // Draw cyber connection lines to cursor for nodes in proximity
      if (!isTouch && activeNodes.length > 0) {
        ctx.shadowBlur = 6;
        ctx.shadowColor = '#39ff14';
        for (const node of activeNodes) {
          const lineAlpha = (1 - node.dist / influenceRadius) * 0.45;
          ctx.beginPath();
          ctx.moveTo(node.x, node.y);
          ctx.lineTo(smoothMouse.current.x, smoothMouse.current.y);
          ctx.strokeStyle = `rgba(57, 255, 20, ${lineAlpha})`;
          ctx.lineWidth = 1;
          ctx.stroke();
        }
        ctx.shadowBlur = 0;
      }

      rafId = requestAnimationFrame(draw);
    };

    resize();
    window.addEventListener('resize', resize);
    window.addEventListener('mousemove', handleMouse, { passive: true });
    window.addEventListener('mouseleave', handleMouseLeave);
    window.addEventListener('scroll', handleScroll, { passive: true });
    rafId = requestAnimationFrame(draw);

    return () => {
      window.removeEventListener('resize', resize);
      window.removeEventListener('mousemove', handleMouse);
      window.removeEventListener('mouseleave', handleMouseLeave);
      window.removeEventListener('scroll', handleScroll);
      cancelAnimationFrame(rafId);
    };
  }, []);

  if (prefersReducedMotion()) return null;

  return (
    <canvas
      ref={canvasRef}
      aria-hidden="true"
      className={className}
      style={{
        position: 'fixed',
        inset: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
        zIndex: 0,
        opacity: 1,
      }}
    />
  );
}

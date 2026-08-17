import { useEffect, useRef, useState, useCallback } from 'react';

/**
 * Scroll position + velocity hook.
 * Drives header response, parallax intensity, velocity-based motion.
 * Uses a single RAF to compute velocity without excessive re-renders.
 */
export function useSmoothScroll() {
  const [scrollState, setScrollState] = useState({
    y: 0,
    velocity: 0,
    direction: 'down',
    progress: 0,
    isScrolled: false,
  });

  const prevY = useRef(0);
  const rafId = useRef(null);
  const ticking = useRef(false);

  const update = useCallback(() => {
    const y = window.scrollY;
    const velocity = y - prevY.current;
    const direction = velocity >= 0 ? 'down' : 'up';
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const progress = docHeight > 0 ? y / docHeight : 0;
    const isScrolled = y > 10;

    prevY.current = y;
    ticking.current = false;

    setScrollState({ y, velocity, direction, progress, isScrolled });
  }, []);

  useEffect(() => {
    const onScroll = () => {
      if (!ticking.current) {
        ticking.current = true;
        rafId.current = requestAnimationFrame(update);
      }
    };

    window.addEventListener('scroll', onScroll, { passive: true });

    return () => {
      window.removeEventListener('scroll', onScroll);
      if (rafId.current) cancelAnimationFrame(rafId.current);
    };
  }, [update]);

  return scrollState;
}

/**
 * Lightweight variant: returns a ref (no re-renders).
 * For imperative scroll-linked style updates.
 */
export function useScrollRef() {
  const ref = useRef({ y: 0, velocity: 0, isScrolled: false });

  useEffect(() => {
    let prevY = 0;
    let ticking = false;

    const update = () => {
      const y = window.scrollY;
      ref.current = {
        y,
        velocity: y - prevY,
        isScrolled: y > 10,
      };
      prevY = y;
      ticking = false;
    };

    const onScroll = () => {
      if (!ticking) {
        ticking = true;
        requestAnimationFrame(update);
      }
    };

    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return ref;
}

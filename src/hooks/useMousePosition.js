import { useEffect, useRef, useCallback } from 'react';
import { lerp, isTouchDevice, prefersReducedMotion } from '../lib/motionConfig';

/**
 * Global mouse position hook with lerp interpolation.
 * Uses a single shared RAF loop to avoid per-component event listeners.
 * Returns smoothly interpolated { x, y } coordinates.
 */

// Singleton state — shared across all hook instances
let listeners = new Set();
let rawX = 0;
let rawY = 0;
let smoothX = 0;
let smoothY = 0;
let rafId = null;
let initialized = false;

function handleMouseMove(e) {
  rawX = e.clientX;
  rawY = e.clientY;
}

function tick() {
  smoothX = lerp(smoothX, rawX, 0.12);
  smoothY = lerp(smoothY, rawY, 0.12);

  const pos = { x: smoothX, y: smoothY, rawX, rawY };
  listeners.forEach((cb) => cb(pos));

  rafId = requestAnimationFrame(tick);
}

function startGlobalListening() {
  if (initialized) return;
  initialized = true;
  window.addEventListener('mousemove', handleMouseMove, { passive: true });
  rafId = requestAnimationFrame(tick);
}

function stopGlobalListening() {
  if (listeners.size > 0) return;
  initialized = false;
  window.removeEventListener('mousemove', handleMouseMove);
  if (rafId) {
    cancelAnimationFrame(rafId);
    rafId = null;
  }
}

export function useMousePosition(lerpFactor) {
  const posRef = useRef({ x: 0, y: 0, rawX: 0, rawY: 0 });
  const subscribersRef = useRef(new Set());

  // Allow external subscribers (for imperative updates e.g. DOM style)
  const subscribe = useCallback((cb) => {
    subscribersRef.current.add(cb);
    return () => subscribersRef.current.delete(cb);
  }, []);

  useEffect(() => {
    // Disable on touch devices or reduced motion
    if (isTouchDevice() || prefersReducedMotion()) return;

    const handleUpdate = (pos) => {
      posRef.current = pos;
      subscribersRef.current.forEach((cb) => cb(pos));
    };

    listeners.add(handleUpdate);
    startGlobalListening();

    return () => {
      listeners.delete(handleUpdate);
      stopGlobalListening();
    };
  }, []);

  return { posRef, subscribe };
}

/**
 * Lightweight hook that just returns raw (non-lerped) mouse position
 * via a ref — no re-renders, no RAF. Good for simple effects.
 */
export function useMousePositionRef() {
  const ref = useRef({ x: 0, y: 0 });

  useEffect(() => {
    if (isTouchDevice() || prefersReducedMotion()) return;

    const handler = (e) => {
      ref.current.x = e.clientX;
      ref.current.y = e.clientY;
    };

    // If global listener is already running, tap into it
    const handleUpdate = (pos) => {
      ref.current.x = pos.rawX;
      ref.current.y = pos.rawY;
    };

    listeners.add(handleUpdate);
    startGlobalListening();

    return () => {
      listeners.delete(handleUpdate);
      stopGlobalListening();
    };
  }, []);

  return ref;
}

import { useEffect, useState, useCallback } from 'react';

/**
 * Frontend-only persistence hook. Mirrors the demo-state pattern from the
 * original HTML (localStorage.getItem/setItem) but exposes it the React way.
 */
export function useLocalStorage(key, initialValue) {
  const [value, setValue] = useState(() => {
    try {
      const raw = window.localStorage.getItem(key);
      return raw ? JSON.parse(raw) : initialValue;
    } catch (e) {
      console.warn('useLocalStorage: could not read', key, e);
      return initialValue;
    }
  });

  useEffect(() => {
    try {
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch (e) {
      console.warn('useLocalStorage: could not persist', key, e);
    }
  }, [key, value]);

  const reset = useCallback(() => setValue(initialValue), [initialValue]);

  return [value, setValue, reset];
}

export function resetAllDemoData() {
  Object.keys(window.localStorage)
    .filter((k) => k.startsWith('skillgraph_'))
    .forEach((k) => window.localStorage.removeItem(k));
  window.location.href = '/login';
}

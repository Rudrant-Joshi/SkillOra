import { createContext, useContext, useMemo, useState, useCallback } from 'react';
import { roleHome } from '../data/roles';

const AuthContext = createContext(null);

const SESSION_KEY = 'skillgraph_demo_session_v1';

export function AuthProvider({ children }) {
  const [session, setSession] = useState(() => {
    try {
      const stored = localStorage.getItem(SESSION_KEY);
      if (stored) return JSON.parse(stored);
    } catch (e) {
      // corrupt storage
    }
    return null;
  });

  const [loading, setLoading] = useState(false);

  const persistSession = useCallback((data) => {
    setSession(data);
    try {
      localStorage.setItem(SESSION_KEY, JSON.stringify(data));
    } catch (e) {
      // localStorage disabled
    }
  }, []);

  const value = useMemo(
    () => ({
      isAuthenticated: !!session?.token,
      role: session?.role || 'developer',
      email: session?.email || '',
      full_name: session?.full_name || '',
      user_id: session?.user_id || null,
      company_id: session?.company_id || null,
      token: session?.token || null,
      login: async ({ email, password, role: requestedRole }) => {
        // Map frontend role to backend role where needed
        const roleMap = { developer: 'candidate', recruiter: 'trainer', company: 'admin' };
        const backendRole = roleMap[requestedRole] || 'candidate';

        setLoading(true);
        try {
          const resp = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password, role: backendRole }),
          });

          if (!resp.ok) {
            const err = await resp.json().catch(() => ({}));
            throw new Error(err.detail || 'Login failed');
          }

          const data = await resp.json();
          const frontendRole = (['admin'] .includes(data.role) ? 'company' : data.role === 'trainer' ? 'recruiter' : 'developer');

          const sess = {
            token: data.access_token,
            role: frontendRole,
            email: data.email,
            full_name: data.full_name,
            user_id: data.user_id,
            company_id: data.company_id,
            at: Date.now(),
          };
          persistSession(sess);
          return roleHome[frontendRole] || '/app/dashboard';
        } finally {
          setLoading(false);
        }
      },
      logout: () => {
        setSession(null);
        try {
          localStorage.removeItem(SESSION_KEY);
          localStorage.removeItem('skillgraph_auth_token_v1');
        } catch (e) {
          // ignore
        }
      },
      switchRole: (role) => {
        setSession((prev) => (prev ? { ...prev, role } : prev));
        return roleHome[role] || '/app/dashboard';
      },
      loading,
    }),
    [session, persistSession, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

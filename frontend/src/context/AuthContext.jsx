import { createContext, useContext, useMemo } from 'react';
import { useLocalStorage } from '../hooks/useLocalStorage';
import { roleHome } from '../data/roles';

const AuthContext = createContext(null);

const SESSION_KEY = 'skillgraph_demo_session_v1';

export function AuthProvider({ children }) {
  const [session, setSession] = useLocalStorage(SESSION_KEY, null);

  const value = useMemo(
    () => ({
      isAuthenticated: !!session,
      role: session?.role || 'developer',
      email: session?.email || '',
      // Frontend-only demo login: validate non-empty fields, fabricate a session, no backend call.
      login: ({ email, role }) => {
        const nextSession = { email: email || 'demo@skillgraph.dev', role: role || 'developer', at: Date.now() };
        setSession(nextSession);
        return roleHome[nextSession.role] || '/app/dashboard';
      },
      switchRole: (role) => {
        setSession((prev) => (prev ? { ...prev, role } : prev));
        return roleHome[role] || '/app/dashboard';
      },
      logout: () => setSession(null),
    }),
    [session, setSession]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

import { createContext, useContext, useCallback, useMemo } from 'react';
import { useLocalStorage } from '../hooks/useLocalStorage';
import { initialSnippets, initialSolvedProblems, problemsData } from '../data/code';
import { networkSeed, feedSeed } from '../data/social';
import { useToast } from './ToastContext';

const STATE_KEY = 'skillgraph_demo_state_v1';

const defaultState = {
  snippets: initialSnippets,
  solved: initialSolvedProblems,
  followingCount: 128,
  network: networkSeed,
  feed: feedSeed,
};

const DemoStateContext = createContext(null);

export function DemoStateProvider({ children }) {
  const [state, setState] = useLocalStorage(STATE_KEY, defaultState);
  const { showToast } = useToast();

  const pushActivity = useCallback((entry) => {
    setState((prev) => ({ ...prev, feed: [{ id: `f${Date.now()}`, ...entry }, ...prev.feed] }));
  }, [setState]);

  // ---- Snippets ----
  const saveSnippet = useCallback((snippet) => {
    setState((prev) => {
      const exists = prev.snippets.some((s) => s.id === snippet.id);
      const snippets = exists
        ? prev.snippets.map((s) => (s.id === snippet.id ? snippet : s))
        : [snippet, ...prev.snippets];
      return { ...prev, snippets };
    });
  }, [setState]);

  const deleteSnippet = useCallback((id) => {
    setState((prev) => ({ ...prev, snippets: prev.snippets.filter((s) => s.id !== id) }));
  }, [setState]);

  const restoreSnippetVersion = useCallback((id, versionMsg) => {
    showToast(`Restored version — ${versionMsg}`);
  }, [showToast]);

  // ---- Problems ----
  const markSolved = useCallback((id) => {
    let wasSolved = false;
    setState((prev) => {
      wasSolved = prev.solved.includes(id);
      if (wasSolved) return prev;
      return { ...prev, solved: [...prev.solved, id] };
    });
    if (!wasSolved) {
      const p = problemsData.find((x) => x.id === id);
      if (p) {
        pushActivity({ type: 'solved_problem', name: 'Rudrant Joshi', role: 'Backend Developer', title: p.title, diff: p.diff });
        showToast(`Solved "${p.title}" — profile and feed updated`);
      }
    }
    return !wasSolved;
  }, [setState, pushActivity, showToast]);

  // ---- Network / following ----
  const toggleFollow = useCallback((name) => {
    setState((prev) => {
      const network = prev.network.map((n) => {
        if (n.name !== name) return n;
        const following = !n.following;
        return { ...n, following, status: following ? 'CONNECTED' : 'CONNECT' };
      });
      const target = network.find((n) => n.name === name);
      const followingCount = prev.followingCount + (target?.following ? 1 : -1);
      return { ...prev, network, followingCount };
    });
    const target = state.network.find((n) => n.name === name);
    if (target && !target.following) {
      pushActivity({ type: 'started_following', name: 'Rudrant Joshi', role: 'Backend Developer', target: name });
    }
  }, [setState, state.network, pushActivity]);

  const value = useMemo(() => ({
    ...state,
    saveSnippet,
    deleteSnippet,
    restoreSnippetVersion,
    markSolved,
    toggleFollow,
    pushActivity,
    resetDemoData: () => setState(defaultState),
  }), [state, saveSnippet, deleteSnippet, restoreSnippetVersion, markSolved, toggleFollow, pushActivity, setState]);

  return <DemoStateContext.Provider value={value}>{children}</DemoStateContext.Provider>;
}

export function useDemoState() {
  const ctx = useContext(DemoStateContext);
  if (!ctx) throw new Error('useDemoState must be used within DemoStateProvider');
  return ctx;
}

import { useEffect, useMemo, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { problemsData } from '../../data/code';
import { jobsData } from '../../data/social';
import { networkSeed } from '../../data/social';

export default function SearchOverlay({ open, onClose }) {
  const [q, setQ] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    if (!open) setQ('');
  }, [open]);

  useEffect(() => {
    if (!open) return;
    const onKey = (e) => e.key === 'Escape' && onClose();
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [open, onClose]);

  const results = useMemo(() => {
    const query = q.trim().toLowerCase();
    if (!query) return { problems: [], jobs: [], people: [] };
    return {
      problems: problemsData.filter((p) => p.title.toLowerCase().includes(query)).slice(0, 4),
      jobs: jobsData.filter((j) => j.title.toLowerCase().includes(query) || j.company.toLowerCase().includes(query)).slice(0, 4),
      people: networkSeed.filter((n) => n.name.toLowerCase().includes(query)).slice(0, 4),
    };
  }, [q]);

  const go = (path) => {
    navigate(path);
    onClose();
  };

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-[110] bg-black/85 backdrop-blur-sm pt-24 px-4"
          onClick={onClose}
        >
          <motion.div
            initial={{ opacity: 0, y: -16 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -16 }}
            transition={{ duration: 0.22 }}
            className="max-w-xl mx-auto bg-black border-2 border-white"
            onClick={(e) => e.stopPropagation()}
          >
            <input
              autoFocus
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Search problems, jobs, people…"
              className="w-full bg-transparent border-b border-borderDim text-white font-mono text-[15px] p-5 focus:outline-none"
            />
            <div className="py-2 max-h-[400px] overflow-y-auto scrollbar-thin">
              {q.trim() === '' && <div className="px-5 py-6 text-xs text-textDim">Start typing to search…</div>}
              {results.problems.length > 0 && (
                <ResultGroup label="Problems">
                  {results.problems.map((p) => (
                    <ResultRow key={p.id} onClick={() => go(`/app/problems/${p.id}`)}>
                      {p.title} <span className="text-textDim">{p.diff}</span>
                    </ResultRow>
                  ))}
                </ResultGroup>
              )}
              {results.jobs.length > 0 && (
                <ResultGroup label="Jobs">
                  {results.jobs.map((j) => (
                    <ResultRow key={j.id} onClick={() => go(`/app/jobs/${j.id}`)}>
                      {j.title} <span className="text-textDim">{j.company}</span>
                    </ResultRow>
                  ))}
                </ResultGroup>
              )}
              {results.people.length > 0 && (
                <ResultGroup label="People">
                  {results.people.map((p) => (
                    <ResultRow key={p.name} onClick={() => go('/app/network')}>
                      {p.name} <span className="text-textDim">{p.role}</span>
                    </ResultRow>
                  ))}
                </ResultGroup>
              )}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

function ResultGroup({ label, children }) {
  return (
    <div>
      <div className="text-[10px] tracking-[2px] text-textMute px-5 pt-3 pb-1.5 uppercase">{label}</div>
      {children}
    </div>
  );
}

function ResultRow({ children, onClick }) {
  return (
    <div onClick={onClick} className="px-5 py-2.5 text-[13px] flex justify-between cursor-pointer hover:bg-surface2 hover:text-green transition-colors">
      {children}
    </div>
  );
}

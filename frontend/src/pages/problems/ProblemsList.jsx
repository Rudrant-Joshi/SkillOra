import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { PageHeader } from '../../components/ui/Primitives';
import { StaggerContainer, StaggerItem } from '../../components/animations/Reveal';
import { problemsData } from '../../data/code';
import { useDemoState } from '../../context/DemoStateContext';

const DIFFS = ['all', 'Easy', 'Medium', 'Hard'];
const SOLVED_FILTERS = ['all', 'solved', 'unsolved'];

export default function ProblemsList() {
  const { solved } = useDemoState();
  const [search, setSearch] = useState('');
  const [diff, setDiff] = useState('all');
  const [solvedFilter, setSolvedFilter] = useState('all');

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return problemsData.filter((p) => {
      if (diff !== 'all' && p.diff !== diff) return false;
      const isSolved = solved.includes(p.id);
      if (solvedFilter === 'solved' && !isSolved) return false;
      if (solvedFilter === 'unsolved' && isSolved) return false;
      if (q && !p.title.toLowerCase().includes(q) && !p.tags.some((t) => t.toLowerCase().includes(q))) return false;
      return true;
    });
  }, [search, diff, solvedFilter, solved]);

  const clearFilters = () => {
    setSearch('');
    setDiff('all');
    setSolvedFilter('all');
  };

  return (
    <div>
      <PageHeader title="Problems" subtitle="Judge0-ready problem set. Solving updates your profile and feed." />

      <div className="flex flex-wrap gap-4 items-center mb-5">
        <input className="field-input max-w-[260px] m-0" placeholder="Search by title or tag…" value={search} onChange={(e) => setSearch(e.target.value)} />
        <div className="flex gap-1.5">
          {DIFFS.map((d) => (
            <button key={d} className={`btn-small ${diff === d ? 'active' : ''}`} onClick={() => setDiff(d)}>
              {d.toUpperCase()}
            </button>
          ))}
        </div>
        <div className="flex gap-1.5">
          {SOLVED_FILTERS.map((s) => (
            <button key={s} className={`btn-small ${solvedFilter === s ? 'active' : ''}`} onClick={() => setSolvedFilter(s)}>
              {s.toUpperCase()}
            </button>
          ))}
        </div>
        <button className="btn-small" onClick={clearFilters}>
          CLEAR FILTERS
        </button>
        <span className="mono dim text-[10px] ml-auto text-textDim">{filtered.length} PROBLEMS</span>
      </div>

      <StaggerContainer className="flex flex-col gap-2.5">
        {filtered.map((p) => {
          const isSolved = solved.includes(p.id);
          return (
            <StaggerItem key={p.id}>
              <Link to={`/app/problems/${p.id}`} className="block">
                <div className="problem-row group hover:border-white/30 transition-all">
                  <span className={`status-dot`} style={{ background: isSolved ? 'var(--green)' : '#4A4A4A', boxShadow: isSolved ? '0 0 8px #39ff14' : 'none' }} />
                  <span className="flex-1 text-[13px] font-medium text-white group-hover:text-green transition-colors">{p.title}</span>
                  <div className="flex gap-1.5 flex-wrap">
                    {p.tags.map((t) => (
                      <span key={t} className="tech-pill">{t}</span>
                    ))}
                  </div>
                  <span className={`badge ${p.diff === 'Easy' ? 'strong' : p.diff === 'Medium' ? 'warn' : 'gap'}`}>{p.diff.toUpperCase()}</span>
                </div>
              </Link>
            </StaggerItem>
          );
        })}
        {filtered.length === 0 && <div className="card-flat text-center py-8 dim text-xs text-textDim">No problems match these filters.</div>}
      </StaggerContainer>
    </div>
  );
}

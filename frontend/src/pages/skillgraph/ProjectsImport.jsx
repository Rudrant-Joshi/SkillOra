import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Check } from 'lucide-react';
import { PageHeader } from '../../components/ui/Primitives';
import { apStepsData } from '../../data/skills';

export default function ProjectsImport() {
  const [repoUrl, setRepoUrl] = useState('');
  const [running, setRunning] = useState(false);
  const [stepIndex, setStepIndex] = useState(-1);
  const navigate = useNavigate();
  const timers = useRef([]);

  useEffect(() => () => timers.current.forEach(clearTimeout), []);

  const startAnalysis = (e) => {
    e.preventDefault();
    if (running) return;
    setRunning(true);
    setStepIndex(0);
    apStepsData.forEach((_, i) => {
      const t = setTimeout(() => setStepIndex(i), i * 550);
      timers.current.push(t);
    });
    const done = setTimeout(() => {
      navigate('/app/skillgraph');
    }, apStepsData.length * 550 + 700);
    timers.current.push(done);
  };

  return (
    <div>
      <PageHeader title="Import / Analyze Project" subtitle="Connect a repository to generate a verified SkillGraph from real code, not self-reported claims." />

      {!running && (
        <form onSubmit={startAnalysis} className="card-flat max-w-lg">
          <div className="field-label">Repository URL</div>
          <input
            className="field-input"
            placeholder="https://github.com/you/your-repo"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
          />
          <button type="submit" className="btn-primary w-full justify-center">
            ANALYZE REPOSITORY
          </button>
        </form>
      )}

      {running && (
        <div className="card-flat max-w-lg">
          <div className="flex flex-col gap-3">
            {apStepsData.map((label, i) => {
              const state = i < stepIndex ? 'done' : i === stepIndex ? 'active' : 'pending';
              return (
                <motion.div
                  key={label}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: state === 'pending' ? 0.35 : 1, x: 0 }}
                  transition={{ duration: 0.3 }}
                  className="flex items-center gap-3 text-xs"
                >
                  <span
                    className={`w-5 h-5 flex-shrink-0 border flex items-center justify-center ${
                      state === 'done' ? 'border-green text-green' : state === 'active' ? 'border-white text-white' : 'border-borderDim text-textMute'
                    }`}
                  >
                    {state === 'done' ? (
                      <Check size={12} />
                    ) : state === 'active' ? (
                      <motion.span
                        className="w-1.5 h-1.5 bg-white rounded-full"
                        animate={{ opacity: [1, 0.3, 1] }}
                        transition={{ duration: 0.9, repeat: Infinity }}
                      />
                    ) : (
                      i + 1
                    )}
                  </span>
                  <span className={state === 'done' ? 'text-green' : ''}>{label}</span>
                </motion.div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

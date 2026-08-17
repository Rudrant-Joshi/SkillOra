import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Check } from 'lucide-react';
import { PageHeader } from '../../components/ui/Primitives';
import Magnetic from '../../components/motion/Magnetic';
import { apStepsData } from '../../data/skills';
import { springs, ease } from '../../lib/motionConfig';

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

  const progress = running ? Math.min(((stepIndex + 1) / apStepsData.length) * 100, 100) : 0;

  return (
    <div>
      <PageHeader title="Import / Analyze Project" subtitle="Connect a repository to generate a verified SkillGraph from real code, not self-reported claims." />

      {!running && (
        <motion.form
          onSubmit={startAnalysis}
          className="card-flat max-w-lg"
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15, duration: 0.4, ease: ease.out }}
        >
          <div className="field-label">Repository URL</div>
          <input
            className="field-input"
            placeholder="https://github.com/you/your-repo"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
          />
          <Magnetic strength={0.15}>
            <motion.button
              type="submit"
              className="btn-primary w-full justify-center"
              whileHover={{ y: -2 }}
              whileTap={{ scale: 0.97 }}
              transition={springs.snappy}
            >
              ANALYZE REPOSITORY
            </motion.button>
          </Magnetic>
        </motion.form>
      )}

      {running && (
        <motion.div
          className="card-flat max-w-lg"
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4, ease: ease.out }}
        >
          {/* Progress bar at top */}
          <div className="mb-5">
            <div className="flex justify-between text-[10px] text-textDim mb-1.5">
              <span>ANALYSIS PROGRESS</span>
              <span className="text-green">{Math.round(progress)}%</span>
            </div>
            <div className="progress-track">
              <motion.div
                className="progress-fill"
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.4, ease: ease.out }}
              />
            </div>
          </div>

          {/* Connecting line */}
          <div className="relative">
            <motion.div
              className="absolute left-[9px] top-[10px] w-px bg-borderDim"
              style={{ bottom: 10 }}
              initial={{ scaleY: 0 }}
              animate={{ scaleY: 1 }}
              transition={{ duration: 0.6, ease: ease.out }}
            />
            <div className="flex flex-col gap-3 relative">
              {apStepsData.map((label, i) => {
                const state = i < stepIndex ? 'done' : i === stepIndex ? 'active' : 'pending';
                return (
                  <motion.div
                    key={label}
                    initial={{ opacity: 0, x: -12 }}
                    animate={{
                      opacity: state === 'pending' ? 0.3 : 1,
                      x: 0,
                    }}
                    transition={{ duration: 0.35, delay: i * 0.04, ease: ease.out }}
                    className="flex items-center gap-3 text-xs relative z-10"
                  >
                    <motion.span
                      className={`w-5 h-5 flex-shrink-0 border flex items-center justify-center ${
                        state === 'done' ? 'border-green text-green bg-black' : state === 'active' ? 'border-white text-white bg-black' : 'border-borderDim text-textMute bg-black'
                      }`}
                      animate={state === 'active' ? {
                        borderColor: ['#fff', '#39FF14', '#fff'],
                        boxShadow: ['0 0 0px transparent', '0 0 8px rgba(57,255,20,0.3)', '0 0 0px transparent'],
                      } : {}}
                      transition={state === 'active' ? { duration: 1.5, repeat: Infinity } : springs.snappy}
                    >
                      {state === 'done' ? (
                        <motion.span
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          transition={springs.bouncy}
                        >
                          <Check size={12} />
                        </motion.span>
                      ) : state === 'active' ? (
                        <motion.span
                          className="w-1.5 h-1.5 bg-white rounded-full"
                          animate={{ opacity: [1, 0.3, 1] }}
                          transition={{ duration: 0.9, repeat: Infinity }}
                        />
                      ) : (
                        <span className="text-[9px]">{i + 1}</span>
                      )}
                    </motion.span>
                    <motion.span
                      className={state === 'done' ? 'text-green' : ''}
                      animate={state === 'active' ? { x: [0, 2, 0] } : {}}
                      transition={state === 'active' ? { duration: 1, repeat: Infinity } : {}}
                    >
                      {label}
                    </motion.span>
                  </motion.div>
                );
              })}
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}

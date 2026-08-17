import { motion } from 'framer-motion';
import { Reveal, StaggerContainer, StaggerItem } from '../../components/animations/Reveal';
import { ProgressBar, AnimatedNumber } from '../../components/ui/AnimatedNumber';
import Spotlight from '../../components/motion/Spotlight';
import TiltCard from '../../components/motion/TiltCard';
import { springs, ease } from '../../lib/motionConfig';

const dimensions = [
  { name: 'Architecture', pct: 78 },
  { name: 'Code Quality', pct: 74 },
  { name: 'Testing', pct: 41 },
  { name: 'Documentation', pct: 58 },
  { name: 'Security', pct: 69 },
  { name: 'Performance', pct: 66 },
];

export default function Xray() {
  return (
    <div>
      <Reveal>
        <div className="flex justify-between items-start flex-wrap gap-4">
          <div>
            <div className="h-display text-2xl">E-Commerce API</div>
            <div className="mono dim text-[11px] mt-1.5 text-textDim">github.com/rudrant/ecommerce-api</div>
            <div className="flex gap-2 mt-3 flex-wrap">
              {['PYTHON', 'FASTAPI', 'POSTGRESQL', 'DOCKER'].map((t, i) => (
                <motion.span
                  key={t}
                  className="tech-pill"
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.2 + i * 0.06, duration: 0.3 }}
                >
                  {t}
                </motion.span>
              ))}
            </div>
          </div>
          <div className="flex gap-2.5">
            <motion.button
              className="btn-small"
              whileHover={{ y: -2 }}
              whileTap={{ scale: 0.96 }}
              transition={springs.snappy}
            >
              RE-ANALYZE
            </motion.button>
            <motion.button
              className="btn-small"
              whileHover={{ y: -2 }}
              whileTap={{ scale: 0.96 }}
              transition={springs.snappy}
            >
              VIEW REPOSITORY
            </motion.button>
          </div>
        </div>
        <div className="divider" />
      </Reveal>

      <div className="grid grid-cols-1 lg:grid-cols-[1fr_1.4fr] gap-4 items-start">
        <Reveal delay={0.05} mode="scale">
          <TiltCard tiltMax={3}>
            <Spotlight>
              <div className="offset-panel">
                <div className="inner p-7">
                  <div className="eyebrow">Project Health</div>
                  {/* Radial progress visual */}
                  <div className="relative w-32 h-32 mx-auto mt-3">
                    <svg viewBox="0 0 120 120" className="w-full h-full">
                      <circle cx="60" cy="60" r="52" fill="none" stroke="#242424" strokeWidth="6" />
                      <motion.circle
                        cx="60" cy="60" r="52"
                        fill="none" stroke="#39FF14" strokeWidth="6"
                        strokeLinecap="butt"
                        strokeDasharray={`${2 * Math.PI * 52}`}
                        initial={{ strokeDashoffset: 2 * Math.PI * 52 }}
                        whileInView={{ strokeDashoffset: 2 * Math.PI * 52 * (1 - 0.72) }}
                        viewport={{ once: true }}
                        transition={{ duration: 1.2, ease: ease.out, delay: 0.3 }}
                        transform="rotate(-90 60 60)"
                      />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="big-num text-3xl">
                        <AnimatedNumber value={72} />
                      </div>
                    </div>
                  </div>
                  <div className="text-center mt-2">
                    <motion.span
                      className="badge strong"
                      initial={{ opacity: 0, scale: 0.8 }}
                      whileInView={{ opacity: 1, scale: 1 }}
                      viewport={{ once: true }}
                      transition={{ delay: 0.5, ...springs.snappy }}
                    >
                      ◆ GOOD
                    </motion.span>
                  </div>
                  <div className="mono dim text-[11px] mt-4 cursor-pointer hover:text-white transition-colors text-textDim text-center">
                    WHY THIS SCORE? →
                  </div>
                </div>
              </div>
            </Spotlight>
          </TiltCard>
        </Reveal>
        <Reveal delay={0.1}>
          <TiltCard tiltMax={2.5}>
            <Spotlight>
              <div className="card-flat">
                <div className="eyebrow">Health Dimensions</div>
                <div className="flex flex-col gap-3 mt-3">
                  {dimensions.map((d, i) => (
                    <Reveal key={d.name} delay={0.15 + i * 0.05}>
                      <div>
                        <div className="flex justify-between text-[11px] mb-1.5">
                          <span>{d.name}</span>
                          <span className="text-textDim">{d.pct}%</span>
                        </div>
                        <ProgressBar pct={d.pct} tone={d.pct < 50 ? 'amber' : ''} />
                      </div>
                    </Reveal>
                  ))}
                </div>
              </div>
            </Spotlight>
          </TiltCard>
        </Reveal>
      </div>

      <div className="divider" />
      <Reveal>
        <div className="text-xs tracking-widest uppercase text-textDim mb-4">Architecture</div>
        <TiltCard tiltMax={2}>
          <Spotlight>
            <div className="card-flat flex flex-col items-center gap-0 py-9">
              {['CLIENT', 'API GATEWAY — FASTAPI', 'SERVICES', 'POSTGRESQL'].map((node, i) => (
                <motion.div
                  key={node}
                  className="flex flex-col items-center"
                  initial={{ opacity: 0, y: 10 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.15 + i * 0.12, duration: 0.4, ease: ease.out }}
                >
                  <motion.div
                    className={`px-5 py-2.5 border text-xs tracking-wide ${i === 1 ? 'border-green text-green' : 'border-borderDim'}`}
                    whileHover={{ scale: 1.02 }}
                    transition={springs.snappy}
                  >
                    {node}
                  </motion.div>
                  {i < 3 && (
                    <motion.div
                      className="w-px h-6 bg-borderDim"
                      initial={{ scaleY: 0 }}
                      whileInView={{ scaleY: 1 }}
                      viewport={{ once: true }}
                      transition={{ delay: 0.3 + i * 0.12, duration: 0.3 }}
                      style={{ transformOrigin: 'top' }}
                    />
                  )}
                </motion.div>
              ))}
            </div>
          </Spotlight>
        </TiltCard>
      </Reveal>

      <div className="divider" />
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Reveal direction="left">
          <TiltCard tiltMax={2.5}>
            <Spotlight>
              <div className="card-flat">
                <div className="eyebrow text-green">Strengths</div>
                <div className="mono text-xs leading-loose">
                  {['Clean API structure', 'Good separation of concerns', 'Consistent error handling'].map((s, i) => (
                    <motion.div
                      key={s}
                      initial={{ opacity: 0, x: -10 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      viewport={{ once: true }}
                      transition={{ delay: 0.1 + i * 0.08, duration: 0.3, ease: ease.out }}
                    >
                      ✓ {s}
                    </motion.div>
                  ))}
                </div>
              </div>
            </Spotlight>
          </TiltCard>
        </Reveal>
        <Reveal direction="right" delay={0.05}>
          <TiltCard tiltMax={2.5}>
            <Spotlight>
              <div className="card-flat">
                <div className="eyebrow">Warnings</div>
                <div className="mono text-xs leading-loose">
                  {['Limited automated testing', 'Documentation incomplete', 'No caching layer'].map((s, i) => (
                    <motion.div
                      key={s}
                      initial={{ opacity: 0, x: 10 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      viewport={{ once: true }}
                      transition={{ delay: 0.1 + i * 0.08, duration: 0.3, ease: ease.out }}
                    >
                      ⚠ {s}
                    </motion.div>
                  ))}
                </div>
              </div>
            </Spotlight>
          </TiltCard>
        </Reveal>
      </div>
    </div>
  );
}

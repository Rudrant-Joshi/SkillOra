import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { PageHeader } from '../../components/ui/Primitives';
import { Reveal } from '../../components/animations/Reveal';
import { AnimatedNumber } from '../../components/ui/AnimatedNumber';
import { beforeAfterData } from '../../data/skills';
import { springs, ease } from '../../lib/motionConfig';

export default function Verify() {
  const [analyzing, setAnalyzing] = useState(true);

  useEffect(() => {
    const t = setTimeout(() => setAnalyzing(false), 1800);
    return () => clearTimeout(t);
  }, []);

  const stages = ['PREVIOUS\nANALYSIS', 'PROJECT\nIMPROVEMENTS', 'NEW REPO\nANALYSIS', 'EVIDENCE\nCOMPARISON', '✓ VERIFIED\nIMPROVEMENT'];

  return (
    <div>
      <PageHeader title="Project Improvement" subtitle="Your latest project changes were analyzed and verified." />

      <Reveal mode="scale">
        <div className="offset-panel">
          <div className="inner p-8 text-center">
            <div className="eyebrow">Overall Skill Confidence</div>
            <div className="flex items-center justify-center gap-6 mt-2.5">
              <motion.div
                className="h-display text-4xl text-textMute"
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2, duration: 0.4 }}
              >
                58%
              </motion.div>
              <motion.div
                className="text-2xl text-green"
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.4, ...springs.bouncy }}
              >
                →
              </motion.div>
              <motion.div
                className="h-display text-green text-5xl md:text-[56px]"
                initial={{ opacity: 0, x: 10, scale: 0.9 }}
                animate={{ opacity: 1, x: 0, scale: 1 }}
                transition={{ delay: 0.5, ...springs.smooth }}
                style={{ textShadow: '0 0 30px rgba(57,255,20,0.2)' }}
              >
                <AnimatedNumber value={82} suffix="%" />
              </motion.div>
            </div>
            <motion.div
              className="text-green mono text-[13px] mt-2"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.7 }}
            >
              +24%
            </motion.div>
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.8, ...springs.snappy }}
            >
              <span className="badge strong mt-4 inline-block">{analyzing ? '◆ ANALYZING…' : '◆ VERIFIED'}</span>
            </motion.div>
          </div>
        </div>
      </Reveal>

      <div className="divider" />
      <Reveal>
        <div className="text-xs tracking-widest uppercase text-textDim mb-4">Before / After</div>
      </Reveal>
      <div className="flex flex-col gap-2.5">
        {beforeAfterData.map((b, i) => (
          <Reveal key={b.name} delay={i * 0.06}>
            <motion.div
              className="skill-row cursor-default"
              whileHover={{ x: 2 }}
              transition={springs.snappy}
            >
              <span className="skill-name">{b.name}</span>
              <span className="text-xs">
                <span className="text-textMute">{b.before}%</span>
                <motion.span
                  className="text-green mx-2"
                  animate={{ x: [0, 3, 0] }}
                  transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
                >
                  →
                </motion.span>
                <span className="text-green">{b.after}%</span>
              </span>
            </motion.div>
          </Reveal>
        ))}
      </div>

      <div className="divider" />
      <Reveal>
        <div className="text-xs tracking-widest uppercase text-textDim mb-5">Verification Timeline</div>
        <div className="card-flat flex justify-between items-center flex-wrap gap-3.5">
          {stages.map((s, i) => (
            <motion.div
              key={s}
              initial={{ opacity: 0, y: 8 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.12, duration: 0.4, ease: ease.out }}
              className={`mono text-[11px] text-center whitespace-pre-line ${i === stages.length - 1 ? 'text-green' : ''}`}
            >
              {s}
              {i < stages.length - 1 && (
                <motion.div
                  className="text-green mt-1"
                  initial={{ opacity: 0 }}
                  whileInView={{ opacity: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.12 + 0.2 }}
                >
                  →
                </motion.div>
              )}
            </motion.div>
          ))}
        </div>
      </Reveal>
    </div>
  );
}

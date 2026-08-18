import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { PageHeader } from '../../components/ui/Primitives';
import { Reveal } from '../../components/animations/Reveal';
import { AnimatedNumber } from '../../components/ui/AnimatedNumber';
import { beforeAfterData } from '../../data/skills';

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

      <div className="offset-panel">
        <div className="inner p-8 text-center">
          <div className="eyebrow">Overall Skill Confidence</div>
          <div className="flex items-center justify-center gap-6 mt-2.5">
            <div className="h-display text-4xl text-textMute">58%</div>
            <div className="text-2xl text-green">→</div>
            <div className="h-display text-green text-5xl md:text-[56px]">
              <AnimatedNumber value={58} suffix="%" />
            </div>
          </div>
          <div className="text-green mono text-[13px] mt-2">+24%</div>
          <div className="badge strong mt-4">{analyzing ? '◆ ANALYZING…' : '◆ VERIFIED'}</div>
        </div>
      </div>

      <div className="divider" />
      <Reveal>
        <div className="text-xs tracking-widest uppercase text-textDim mb-4">Before / After</div>
      </Reveal>
      <div className="flex flex-col gap-2.5">
        {beforeAfterData.map((b) => (
          <Reveal key={b.name}>
            <div className="skill-row cursor-default">
              <span className="skill-name">{b.name}</span>
              <span className="text-xs">
                <span className="text-textMute">{b.before}%</span>
                <span className="text-green mx-2">→</span>
                <span className="text-green">{b.after}%</span>
              </span>
            </div>
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
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: i * 0.1 }}
              className={`mono text-[11px] text-center whitespace-pre-line ${i === stages.length - 1 ? 'text-green' : ''}`}
            >
              {s}
              {i < stages.length - 1 && <div className="text-green mt-1">→</div>}
            </motion.div>
          ))}
        </div>
      </Reveal>
    </div>
  );
}

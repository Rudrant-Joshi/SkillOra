import { motion } from 'framer-motion';
import { PageHeader } from '../../components/ui/Primitives';
import { StaggerContainer, StaggerItem } from '../../components/animations/Reveal';
import { ProgressBar } from '../../components/ui/AnimatedNumber';
import Spotlight from '../../components/motion/Spotlight';
import TiltCard from '../../components/motion/TiltCard';
import { skills } from '../../data/skills';
import { springs } from '../../lib/motionConfig';

export default function Skills() {
  return (
    <div>
      <PageHeader title="Your Skills" subtitle="Skills inferred from your project evidence." />
      <StaggerContainer className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        {skills.map((s) => (
          <StaggerItem key={s.name}>
            <TiltCard tiltMax={3.5}>
              <Spotlight>
                <motion.div
                  className="card"
                  whileTap={{ scale: 0.985 }}
                  transition={springs.snappy}
                >
                  <div className="flex justify-between items-start">
                    <div className="h-display text-base">{s.name}</div>
                    <span className={`badge ${s.badge}`}>{s.pct}%</span>
                  </div>
                  <div className="text-textDim text-[11px] mt-2 uppercase tracking-wide">{s.status}</div>
                  <div className="mt-3">
                    <ProgressBar pct={s.pct} tone={s.badge === 'gap' ? 'red' : s.badge === 'warn' ? 'amber' : ''} />
                  </div>
                  <div className="flex justify-between text-[11px] text-textDim mt-3">
                    <span>{s.projects} projects</span>
                    <span>{s.evidence} evidence pts</span>
                  </div>
                </motion.div>
              </Spotlight>
            </TiltCard>
          </StaggerItem>
        ))}
      </StaggerContainer>
    </div>
  );
}

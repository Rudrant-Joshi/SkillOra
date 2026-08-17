import { motion } from 'framer-motion';
import { PageHeader } from '../../components/ui/Primitives';
import { Reveal, StaggerContainer, StaggerItem } from '../../components/animations/Reveal';
import { ProgressBar, AnimatedNumber } from '../../components/ui/AnimatedNumber';
import Spotlight from '../../components/motion/Spotlight';
import TiltCard from '../../components/motion/TiltCard';
import { roadmap } from '../../data/skills';
import { springs, ease } from '../../lib/motionConfig';

const STATUS_TONE = { 'NOT STARTED': 'text-textDim', 'IN PROGRESS': 'text-white', LOCKED: 'text-textMute', COMPLETE: 'text-green' };

export default function Roadmap() {
  const done = roadmap.filter((r) => r.status === 'COMPLETE').length;
  return (
    <div>
      <PageHeader title="Your Roadmap" subtitle="A prioritized plan to close your biggest skill gaps." />
      <Reveal>
        <div className="flex justify-between items-center">
          <div className="mono text-[11px] text-textDim">{done} / {roadmap.length} TASKS COMPLETED</div>
          <div className="mono text-green text-[11px]">READINESS <AnimatedNumber value={68} suffix="%" /></div>
        </div>
        <div className="mt-2">
          <ProgressBar pct={37} />
        </div>
      </Reveal>
      <div className="divider" />

      {/* Connecting line */}
      <div className="relative">
        <motion.div
          className="absolute left-[18px] top-0 w-px bg-borderDim"
          style={{ bottom: 0 }}
          initial={{ scaleY: 0 }}
          whileInView={{ scaleY: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, ease: ease.out }}
        />
        <StaggerContainer className="flex flex-col gap-3" stagger={0.1}>
          {roadmap.map((step, i) => (
            <StaggerItem key={step.n}>
              <TiltCard tiltMax={2.5}>
                <Spotlight>
                  <motion.div
                    className="card-flat flex gap-5 items-start relative z-10"
                    transition={springs.snappy}
                  >
                    <motion.div
                      className="h-display text-2xl text-textMute flex-shrink-0"
                      initial={{ scale: 0.7, opacity: 0 }}
                      whileInView={{ scale: 1, opacity: 1 }}
                      viewport={{ once: true }}
                      transition={{ delay: 0.1 + i * 0.08, ...springs.bouncy }}
                    >
                      {step.n}
                    </motion.div>
                    <div className="flex-1 min-w-0">
                      <div className="flex justify-between items-start flex-wrap gap-2">
                        <div className="h-display text-base">{step.title}</div>
                        <motion.span
                          className={`badge ${STATUS_TONE[step.status]}`}
                          animate={step.status === 'IN PROGRESS' ? {
                            borderColor: ['#242424', '#39FF14', '#242424'],
                          } : {}}
                          transition={step.status === 'IN PROGRESS' ? { duration: 2, repeat: Infinity } : {}}
                        >
                          {step.status}
                        </motion.span>
                      </div>
                      <div className="text-textDim text-xs mt-2 leading-relaxed">{step.why}</div>
                      <div className="text-xs mt-2">{step.task}</div>
                    </div>
                  </motion.div>
                </Spotlight>
              </TiltCard>
            </StaggerItem>
          ))}
        </StaggerContainer>
      </div>
    </div>
  );
}

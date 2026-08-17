import { AnimatePresence, motion } from 'framer-motion';
import { PageHeader } from '../../components/ui/Primitives';
import Spotlight from '../../components/motion/Spotlight';
import TiltCard from '../../components/motion/TiltCard';
import { useDemoState } from '../../context/DemoStateContext';
import { springs, ease } from '../../lib/motionConfig';

function ActivityBody({ item }) {
  if (item.type === 'solved_problem') {
    return (
      <div className="text-xs mt-1.5">
        Solved <b>{item.title}</b> <span className="tech-pill ml-1">{item.diff}</span>
      </div>
    );
  }
  if (item.type === 'started_following') {
    return (
      <div className="text-xs mt-1.5">
        Started following <b>{item.target}</b>
      </div>
    );
  }
  return (
    <div className="text-xs mt-1.5 leading-relaxed">
      {item.text}
      {item.before !== undefined && (
        <div className="mono text-[11px] mt-2">
          <span className="text-textMute">{item.before}%</span> <span className="text-green">→ {item.after}%</span> <span className="text-textDim">({item.skill})</span>
        </div>
      )}
      {item.badge && <span className="badge strong mt-2 inline-block">✓ {item.badge}</span>}
      {item.project && <span className="tech-pill mt-2 inline-block">{item.project}</span>}
      {item.job && <span className="badge mt-2 inline-block">{item.job}</span>}
    </div>
  );
}

export default function Feed() {
  const { feed } = useDemoState();

  return (
    <div>
      <PageHeader title="Feed" subtitle="Activity from your network — real work, not self-reported claims." />
      <div className="flex flex-col gap-3 max-w-2xl">
        <AnimatePresence initial={false}>
          {feed.map((item, i) => (
            <motion.div
              key={item.id}
              layout
              initial={{ opacity: 0, y: -16, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ duration: 0.35, delay: i * 0.04, ease: ease.out }}
            >
              <TiltCard tiltMax={2.5}>
                <Spotlight>
                  <div className="card-flat">
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="h-display text-sm">{item.name}</div>
                        <div className="text-textDim text-[10px] mt-0.5">{item.role}</div>
                      </div>
                    </div>
                    <ActivityBody item={item} />
                    <div className="flex gap-4 mt-3 text-textDim text-[11px]">
                      <motion.span
                        className="cursor-pointer"
                        whileHover={{ scale: 1.1, color: '#39FF14' }}
                        whileTap={{ scale: 0.9 }}
                        transition={springs.snappy}
                      >
                        ♥ {item.likes ?? 0}
                      </motion.span>
                      <motion.span
                        className="cursor-pointer"
                        whileHover={{ scale: 1.1 }}
                        transition={springs.snappy}
                      >
                        💬 {item.comments ?? 0}
                      </motion.span>
                    </div>
                  </div>
                </Spotlight>
              </TiltCard>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}

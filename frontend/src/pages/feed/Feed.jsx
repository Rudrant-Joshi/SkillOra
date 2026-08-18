import { AnimatePresence, motion } from 'framer-motion';
import { PageHeader } from '../../components/ui/Primitives';
import { useDemoState } from '../../context/DemoStateContext';

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
          {feed.map((item) => (
            <motion.div
              key={item.id}
              layout
              initial={{ opacity: 0, y: -12 }}
              animate={{ opacity: 1, y: 0 }}
              whileHover={{ y: -4, borderColor: 'rgba(57, 255, 20, 0.5)', boxShadow: '0 16px 32px -12px rgba(0,0,0,0.6), 0 0 20px -4px rgba(57,255,20,0.25)' }}
              transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
              className="card-flat border border-borderDim transition-colors"
            >
              <div className="flex justify-between items-start">
                <div>
                  <div className="h-display text-sm text-white">{item.name}</div>
                  <div className="text-textDim text-[10px] mt-0.5">{item.role}</div>
                </div>
              </div>
              <ActivityBody item={item} />
              <div className="flex gap-4 mt-3 text-textDim text-[11px] font-mono">
                <span className="hover:text-green cursor-pointer transition-colors">♥ {item.likes ?? 0}</span>
                <span className="hover:text-white cursor-pointer transition-colors">💬 {item.comments ?? 0}</span>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}

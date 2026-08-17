import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { PageHeader } from '../../components/ui/Primitives';
import { conversationsData } from '../../data/social';
import { springs, ease } from '../../lib/motionConfig';

export default function Messages() {
  const [activeId, setActiveId] = useState(conversationsData[0].id);
  const [draft, setDraft] = useState('');
  const [threads, setThreads] = useState(conversationsData);
  const active = threads.find((c) => c.id === activeId);

  const send = () => {
    if (!draft.trim()) return;
    setThreads((prev) => prev.map((t) => (t.id === activeId ? { ...t, msgs: [...t.msgs, { me: true, t: draft }] } : t)));
    setDraft('');
  };

  return (
    <div>
      <PageHeader title="Messages" subtitle="Direct messages, recruiter conversations, and community threads." />
      <div className="grid grid-cols-1 md:grid-cols-[280px_1fr] gap-4 border border-borderDim" style={{ minHeight: 480 }}>
        <div className="border-r border-borderDim overflow-y-auto scrollbar-thin">
          {threads.map((c) => (
            <motion.button
              key={c.id}
              onClick={() => setActiveId(c.id)}
              className={`relative w-full text-left px-4 py-3.5 border-b border-borderDim block ${c.id === activeId ? '' : 'hover:bg-surface2'}`}
              whileTap={{ scale: 0.98 }}
              transition={springs.snappy}
            >
              {c.id === activeId && (
                <motion.div
                  layoutId="msg-active"
                  className="absolute inset-0 bg-surface2"
                  transition={springs.snappy}
                  style={{ zIndex: 0 }}
                />
              )}
              <div className="relative z-10">
                <div className="flex justify-between items-center">
                  <span className="text-xs">{c.name}</span>
                  {c.online && (
                    <motion.span
                      className="w-1.5 h-1.5 bg-green rounded-full"
                      animate={{ boxShadow: ['0 0 3px rgba(57,255,20,0.4)', '0 0 8px rgba(57,255,20,0.2)', '0 0 3px rgba(57,255,20,0.4)'] }}
                      transition={{ duration: 2, repeat: Infinity }}
                    />
                  )}
                </div>
                <div className="text-textDim text-[10px] mt-1">{c.sub}</div>
                <span className="tech-pill mt-1.5 inline-block">{c.type}</span>
              </div>
            </motion.button>
          ))}
        </div>
        <div className="flex flex-col p-4">
          {active?.context && (
            <motion.div
              className="badge strong mb-3 self-start"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={springs.snappy}
            >
              {active.context}
            </motion.div>
          )}
          <div className="flex-1 flex flex-col gap-2.5 overflow-y-auto scrollbar-thin mb-3">
            <AnimatePresence initial={false}>
              {active?.msgs.map((m, i) => (
                <motion.div
                  key={`${activeId}-${i}`}
                  initial={{ opacity: 0, y: 8, scale: 0.97 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  transition={{ duration: 0.25, delay: i * 0.03, ease: ease.out }}
                  className={`max-w-[70%] px-3.5 py-2.5 text-xs ${m.me ? 'self-end bg-green text-black' : 'self-start bg-surface2 border border-borderDim'}`}
                >
                  {m.t}
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
          <div className="flex gap-2">
            <input
              className="field-input flex-1 m-0"
              placeholder="Write a message…"
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && send()}
            />
            <motion.button
              className="btn-primary"
              onClick={send}
              whileHover={{ y: -2 }}
              whileTap={{ scale: 0.95 }}
              transition={springs.snappy}
            >
              SEND
            </motion.button>
          </div>
        </div>
      </div>
    </div>
  );
}

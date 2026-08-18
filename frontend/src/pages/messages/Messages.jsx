import { useState } from 'react';
import { PageHeader } from '../../components/ui/Primitives';
import { Reveal, StaggerContainer, StaggerItem } from '../../components/animations/Reveal';
import { conversationsData } from '../../data/social';

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
      <Reveal>
        <div className="grid grid-cols-1 md:grid-cols-[280px_1fr] gap-4 border border-borderDim" style={{ minHeight: 480 }}>
          <div className="border-r border-borderDim overflow-y-auto scrollbar-thin">
            <StaggerContainer>
              {threads.map((c) => (
                <StaggerItem key={c.id} direction="left" distance={12}>
                  <button
                    onClick={() => setActiveId(c.id)}
                    className={`w-full text-left px-4 py-3.5 border-b border-borderDim block ${c.id === activeId ? 'bg-surface2' : 'hover:bg-surface2'}`}
                  >
                    <div className="flex justify-between items-center">
                      <span className="text-xs">{c.name}</span>
                      {c.online && <span className="w-1.5 h-1.5 bg-green rounded-full" />}
                    </div>
                    <div className="text-textDim text-[10px] mt-1">{c.sub}</div>
                    <span className="tech-pill mt-1.5 inline-block">{c.type}</span>
                  </button>
                </StaggerItem>
              ))}
            </StaggerContainer>
          </div>
          <div className="flex flex-col p-4">
            {active?.context && <div className="badge strong mb-3 self-start">{active.context}</div>}
            <div className="flex-1 flex flex-col gap-2.5 overflow-y-auto scrollbar-thin mb-3">
              {active?.msgs.map((m, i) => (
                <div key={i} className={`max-w-[70%] px-3.5 py-2.5 text-xs ${m.me ? 'self-end bg-green text-black' : 'self-start bg-surface2 border border-borderDim'}`}>
                  {m.t}
                </div>
              ))}
            </div>
            <div className="flex gap-2">
              <input
                className="field-input flex-1 m-0"
                placeholder="Write a message…"
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && send()}
              />
              <button className="btn-primary" onClick={send}>
                SEND
              </button>
            </div>
          </div>
        </div>
      </Reveal>
    </div>
  );
}

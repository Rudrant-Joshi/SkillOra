import { PageHeader, Card } from '../../components/ui/Primitives';
import { Reveal, StaggerContainer, StaggerItem } from '../../components/animations/Reveal';
import { ProgressBar } from '../../components/ui/AnimatedNumber';
import { roadmap } from '../../data/skills';

const STATUS_BADGE = {
  'NOT STARTED': { cls: 'warn', label: 'NOT STARTED' },
  'IN PROGRESS': { cls: 'cyan', label: 'IN PROGRESS' },
  LOCKED: { cls: '', label: 'LOCKED' },
  COMPLETE: { cls: 'strong', label: '✓ COMPLETE' },
};

export default function Roadmap() {
  const done = roadmap.filter((r) => r.status === 'COMPLETE').length;
  const pct = Math.round((done / roadmap.length) * 100);

  return (
    <div>
      <PageHeader title="Your Roadmap" subtitle="A prioritized plan to close your biggest skill gaps." />
      <Reveal>
        <div className="flex justify-between items-center font-mono">
          <div className="text-[11px] text-textDim tracking-wider">{done} / {roadmap.length} TASKS COMPLETED</div>
          <div className="text-green text-[11px] font-bold tracking-wider">READINESS 68%</div>
        </div>
        <div className="mt-2">
          <ProgressBar pct={pct || 37} />
        </div>
      </Reveal>
      <div className="divider" />
      <StaggerContainer className="flex flex-col gap-3">
        {roadmap.map((step) => (
          <StaggerItem key={step.n}>
            <Card hover className="flex gap-5 items-start">
              <div className="h-display text-2xl text-green/60 font-mono flex-shrink-0">{step.n}</div>
              <div className="flex-1 min-w-0">
                <div className="flex justify-between items-start flex-wrap gap-2">
                  <div className="h-display text-base text-white">{step.title}</div>
                  <span className={`badge ${STATUS_BADGE[step.status]?.cls || ''}`}>
                    {STATUS_BADGE[step.status]?.label || step.status}
                  </span>
                </div>
                <div className="text-textDim text-xs mt-2 leading-relaxed">{step.why}</div>
                <div className="text-xs mt-2 text-white/90 bg-surface2/60 p-2.5 border border-borderDim font-mono">
                  <span className="text-green mr-1.5">▸</span>{step.task}
                </div>
              </div>
            </Card>
          </StaggerItem>
        ))}
      </StaggerContainer>
    </div>
  );
}

import { PageHeader, Card } from '../../components/ui/Primitives';
import { StaggerContainer, StaggerItem } from '../../components/animations/Reveal';
import { ProgressBar } from '../../components/ui/AnimatedNumber';
import { skills } from '../../data/skills';

export default function Skills() {
  return (
    <div>
      <PageHeader title="Your Skills" subtitle="Skills inferred from your project evidence." />
      <StaggerContainer className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        {skills.map((s) => (
          <StaggerItem key={s.name}>
            <Card hover className="flex flex-col justify-between h-full">
              <div>
                <div className="flex justify-between items-start">
                  <div className="h-display text-base text-white">{s.name}</div>
                  <span className={`badge ${s.badge}`}>{s.pct}%</span>
                </div>
                <div className="text-textDim text-[11px] mt-2 uppercase tracking-wide font-mono">{s.status}</div>
                <div className="mt-3">
                  <ProgressBar pct={s.pct} tone={s.badge === 'gap' ? 'red' : s.badge === 'warn' ? 'amber' : ''} />
                </div>
              </div>
              <div className="flex justify-between text-[11px] text-textDim mt-4 font-mono">
                <span>{s.projects} projects</span>
                <span>{s.evidence} evidence pts</span>
              </div>
            </Card>
          </StaggerItem>
        ))}
      </StaggerContainer>
    </div>
  );
}

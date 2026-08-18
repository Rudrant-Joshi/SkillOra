import { useParams } from 'react-router-dom';
import { PageHeader, EmptyState } from '../../components/ui/Primitives';
import { ProgressBar } from '../../components/ui/AnimatedNumber';
import { Reveal, StaggerContainer, StaggerItem } from '../../components/animations/Reveal';
import { candidatesData } from '../../data/recruiter';

export default function Scorecard() {
  const { id } = useParams();
  const candidate = candidatesData[Number(id)];

  if (!candidate) {
    return (
      <div>
        <PageHeader title="Scorecard Not Found" />
        <EmptyState>No candidate matches this scorecard id.</EmptyState>
      </div>
    );
  }

  const dims = [
    { label: 'Technical Skills', pct: candidate.score },
    { label: 'Coding Assessment', pct: Math.min(95, candidate.score + 4) },
    { label: 'AI Interview Signal', pct: Math.max(40, candidate.score - 6) },
    { label: 'Communication', pct: Math.min(90, candidate.score - 2) },
  ];

  return (
    <div>
      <PageHeader title={`${candidate.name} — Scorecard`} subtitle={candidate.skills} />
      <Reveal variant="scale">
        <div className="offset-panel mb-8">
          <div className="inner p-8 text-center">
            <div className="eyebrow">Overall Score</div>
            <div className="h-display text-green text-5xl mt-2">{candidate.score}%</div>
            <div className="badge strong mt-3">{candidate.status.toUpperCase()}</div>
          </div>
        </div>
      </Reveal>
      <StaggerContainer className="flex flex-col gap-4">
        {dims.map((d) => (
          <StaggerItem key={d.label}>
            <div>
              <div className="flex justify-between text-xs mb-1.5">
                <span>{d.label}</span>
                <span className="text-textDim">{d.pct}%</span>
              </div>
              <ProgressBar pct={d.pct} />
            </div>
          </StaggerItem>
        ))}
      </StaggerContainer>
      <Reveal delay={0.15}>
        <div className="flex gap-3 mt-8">
          <button className="btn-primary">SHORTLIST</button>
          <button className="btn-secondary">SCHEDULE INTERVIEW</button>
          <button className="btn-secondary">REJECT</button>
        </div>
      </Reveal>
    </div>
  );
}

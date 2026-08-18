import { Link } from 'react-router-dom';
import { PageHeader, Card } from '../../components/ui/Primitives';
import { StaggerContainer, StaggerItem } from '../../components/animations/Reveal';
import { ProgressBar } from '../../components/ui/AnimatedNumber';
import { jobsData } from '../../data/social';

export default function Jobs() {
  return (
    <div>
      <PageHeader title="Jobs" subtitle="Roles matched to your evidence-backed skill profile." />
      <StaggerContainer className="flex flex-col gap-3">
        {jobsData.map((j) => (
          <StaggerItem key={j.id}>
            <Link to={`/app/jobs/${j.id}`} className="block">
              <Card hover className="flex flex-col sm:flex-row sm:items-center gap-4">
                <div className="flex-1">
                  <div className="h-display text-base text-white group-hover:text-green transition-colors">{j.title}</div>
                  <div className="text-textDim text-xs mt-1">{j.company} · {j.loc} · {j.type}</div>
                  <div className="flex gap-1.5 mt-2">
                    <span className="tech-pill">{j.salary}</span>
                    <span className="tech-pill">{j.posted}</span>
                  </div>
                </div>
                <div className="w-full sm:w-44 flex-shrink-0">
                  <div className="flex justify-between text-[11px] mb-1.5 font-mono">
                    <span className="text-textDim uppercase tracking-wider">Match</span>
                    <span className={`font-bold ${j.match >= 70 ? 'text-green' : j.match >= 50 ? 'text-amber-400' : 'text-red-400'}`}>{j.match}%</span>
                  </div>
                  <ProgressBar pct={j.match} tone={j.match < 50 ? 'red' : j.match < 70 ? 'amber' : ''} />
                </div>
              </Card>
            </Link>
          </StaggerItem>
        ))}
      </StaggerContainer>
    </div>
  );
}

import { Link } from 'react-router-dom';
import { PageHeader, Card } from '../../components/ui/Primitives';
import { StaggerContainer, StaggerItem } from '../../components/animations/Reveal';
import { projects } from '../../data/skills';

export default function Projects() {
  return (
    <div>
      <PageHeader
        title="Projects"
        subtitle="Projects analyzed for verified skill evidence."
        actions={
          <Link to="/app/projects-import" className="btn-primary">
            + IMPORT / ANALYZE PROJECT
          </Link>
        }
      />
      <StaggerContainer className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {projects.map((p) => (
          <StaggerItem key={p.name}>
            <Link to={`/app/projects/${encodeURIComponent(p.name)}`}>
              <Card>
                <div className="flex justify-between items-start">
                  <div className="h-display text-base">{p.name}</div>
                  <span className="badge strong">{p.health}%</span>
                </div>
                <div className="flex gap-1.5 flex-wrap mt-3">
                  {p.tech.map((t) => (
                    <span key={t} className="tech-pill">{t}</span>
                  ))}
                </div>
                <div className="text-textDim text-[11px] mt-3">{p.skills} skills detected · analyzed {p.ago}</div>
              </Card>
            </Link>
          </StaggerItem>
        ))}
      </StaggerContainer>
    </div>
  );
}

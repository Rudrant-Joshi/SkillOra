import { useParams, Link } from 'react-router-dom';
import { PageHeader, Card, EmptyState } from '../../components/ui/Primitives';
import { ProgressBar } from '../../components/ui/AnimatedNumber';
import { Reveal, StaggerContainer, StaggerItem } from '../../components/animations/Reveal';
import { projects } from '../../data/skills';

export default function ProjectDetail() {
  const { name } = useParams();
  const project = projects.find((p) => p.name === decodeURIComponent(name));

  if (!project) {
    return (
      <div>
        <PageHeader title="Project Not Found" />
        <EmptyState>That project doesn't exist in this demo dataset.</EmptyState>
      </div>
    );
  }

  return (
    <div>
      <PageHeader
        title={project.name}
        subtitle={`Analyzed ${project.ago} · Health score ${project.health}%`}
        actions={
          <Link to="/app/xray" className="btn-secondary">
            OPEN X-RAY →
          </Link>
        }
      />
      <StaggerContainer className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <StaggerItem>
          <Card>
            <div className="eyebrow">Project Health</div>
            <div className="big-num text-green text-4xl">{project.health}%</div>
            <div className="mt-3">
              <ProgressBar pct={project.health} />
            </div>
          </Card>
        </StaggerItem>
        <StaggerItem>
          <Card>
            <div className="eyebrow">Technologies Detected</div>
            <div className="flex gap-1.5 flex-wrap mt-2">
              {project.tech.map((t) => (
                <span key={t} className="tech-pill">{t}</span>
              ))}
            </div>
          </Card>
        </StaggerItem>
      </StaggerContainer>
      <div className="divider" />
      <Reveal>
        <div className="text-xs tracking-widest uppercase text-textDim mb-4">Skills Extracted</div>
      </Reveal>
      <Reveal delay={0.05}>
        <div className="card-flat text-sm text-textDim">{project.skills} distinct skills were detected from commits, file structure, and dependency manifests in this repository.</div>
      </Reveal>
    </div>
  );
}

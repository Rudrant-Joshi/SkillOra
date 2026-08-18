import { Link } from 'react-router-dom';
import { PageHeader, Card, StatCard } from '../../components/ui/Primitives';
import { Reveal, StaggerContainer, StaggerItem } from '../../components/animations/Reveal';
import { ProgressBar, AnimatedNumber } from '../../components/ui/AnimatedNumber';
import { skills, projects } from '../../data/skills';
import { useDemoState } from '../../context/DemoStateContext';

export default function Dashboard() {
  const { snippets, solved, followingCount } = useDemoState();
  const langCount = new Set(snippets.map((s) => s.lang)).size;

  return (
    <div>
      <PageHeader
        title="Dashboard"
        subtitle="Evidence-backed overview of your skills, projects, and coding activity."
        actions={
          <Link to="/app/projects" className="btn-primary">
            + ANALYZE PROJECT
          </Link>
        }
      />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Skill Confidence" value={82} suffix="%" tone="text-green" delay={0} />
        <StatCard label="Verified Skills" value={17} delay={0.05} />
        <StatCard label="Projects" value={8} delay={0.1} />
        <StatCard label="Assessments" value={4} delay={0.15} />
      </div>

      <div className="divider" />

      <Reveal>
        <div className="text-xs tracking-widest uppercase text-textDim mb-4">Coding Activity</div>
      </Reveal>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <div className="eyebrow">Problems Solved</div>
          <div className="big-num text-green text-[28px]">
            <AnimatedNumber value={solved.length} />
          </div>
        </Card>
        <Card>
          <div className="eyebrow">Snippets</div>
          <div className="big-num text-[28px]">
            <AnimatedNumber value={snippets.length} />
          </div>
        </Card>
        <Card>
          <div className="eyebrow">Languages</div>
          <div className="big-num text-[28px]">
            <AnimatedNumber value={langCount} />
          </div>
        </Card>
        <Card>
          <div className="eyebrow">Followers · Following</div>
          <div className="big-num text-[28px]">
            128 · <AnimatedNumber value={followingCount} />
          </div>
        </Card>
      </div>

      <div className="divider" />

      <Reveal>
        <div className="text-xs tracking-widest uppercase text-textDim mb-4">Skill Overview</div>
      </Reveal>
      <StaggerContainer className="flex flex-col gap-2.5">
        {skills.slice(0, 5).map((s) => (
          <StaggerItem key={s.name}>
            <div className="skill-row">
              <div className="flex-1 min-w-0">
                <div className="skill-name">{s.name}</div>
                <div className="mt-2">
                  <ProgressBar pct={s.pct} tone={s.badge === 'gap' ? 'red' : s.badge === 'warn' ? 'amber' : ''} />
                </div>
              </div>
              <span className={`badge ${s.badge}`}>{s.pct}%</span>
            </div>
          </StaggerItem>
        ))}
      </StaggerContainer>

      <div className="divider" />

      <Reveal>
        <div className="text-xs tracking-widest uppercase text-textDim mb-4">Recent Projects</div>
      </Reveal>
      <StaggerContainer className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {projects.map((p) => (
          <StaggerItem key={p.name}>
            <Card>
              <div className="flex justify-between items-start">
                <div className="h-display text-sm">{p.name}</div>
                <span className="badge strong">{p.health}%</span>
              </div>
              <div className="flex gap-1.5 flex-wrap mt-3">
                {p.tech.map((t) => (
                  <span key={t} className="tech-pill">{t}</span>
                ))}
              </div>
              <div className="text-textDim text-[11px] mt-3">{p.skills} skills detected · {p.ago}</div>
            </Card>
          </StaggerItem>
        ))}
      </StaggerContainer>
    </div>
  );
}

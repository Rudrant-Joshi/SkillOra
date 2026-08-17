import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { PageHeader } from '../../components/ui/Primitives';
import { StaggerContainer, StaggerItem } from '../../components/animations/Reveal';
import Spotlight from '../../components/motion/Spotlight';
import TiltCard from '../../components/motion/TiltCard';
import Magnetic from '../../components/motion/Magnetic';
import { projects } from '../../data/skills';
import { springs } from '../../lib/motionConfig';

export default function Projects() {
  return (
    <div>
      <PageHeader
        title="Projects"
        subtitle="Projects analyzed for verified skill evidence."
        actions={
          <Magnetic strength={0.2}>
            <Link to="/app/projects-import" className="btn-primary">
              + IMPORT / ANALYZE PROJECT
            </Link>
          </Magnetic>
        }
      />
      <StaggerContainer className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {projects.map((p) => (
          <StaggerItem key={p.name}>
            <Link to={`/app/projects/${encodeURIComponent(p.name)}`}>
              <TiltCard tiltMax={3.5}>
                <Spotlight>
                  <motion.div
                    className="card"
                    whileTap={{ scale: 0.985 }}
                    transition={springs.snappy}
                  >
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
                  </motion.div>
                </Spotlight>
              </TiltCard>
            </Link>
          </StaggerItem>
        ))}
      </StaggerContainer>
    </div>
  );
}

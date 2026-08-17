import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { PageHeader } from '../../components/ui/Primitives';
import { StaggerContainer, StaggerItem } from '../../components/animations/Reveal';
import Spotlight from '../../components/motion/Spotlight';
import TiltCard from '../../components/motion/TiltCard';
import Magnetic from '../../components/motion/Magnetic';
import { useDemoState } from '../../context/DemoStateContext';
import { springs } from '../../lib/motionConfig';

export default function CodeList() {
  const { snippets } = useDemoState();

  return (
    <div>
      <PageHeader
        title="Code / Snippets"
        subtitle="Your hosted code. Public snippets feed your profile and activity feed."
        actions={
          <Magnetic strength={0.2}>
            <Link to="/app/code/snippets/new" className="btn-primary">
              + CREATE SNIPPET
            </Link>
          </Magnetic>
        }
      />
      <StaggerContainer className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        {snippets.map((s) => (
          <StaggerItem key={s.id}>
            <Link to={`/app/code/snippets/${s.id}`}>
              <TiltCard tiltMax={3.5}>
                <Spotlight>
                  <motion.div
                    className="card h-full"
                    whileTap={{ scale: 0.985 }}
                    transition={springs.snappy}
                  >
                    <div className="h-display text-sm">{s.title}</div>
                    <div className="dim mono text-[10px] mt-1.5 text-textDim">{s.desc}</div>
                    <div className="flex gap-1.5 mt-2.5">
                      <span className="tech-pill">{s.lang}</span>
                      <span className="tech-pill">v{s.versions[0].v}</span>
                      <span className={`badge ${s.isPublic ? 'strong' : ''}`}>{s.isPublic ? 'PUBLIC' : 'PRIVATE'}</span>
                    </div>
                    <div className="text-textDim text-[10px] mt-3">Updated {s.updated}</div>
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

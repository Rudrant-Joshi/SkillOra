import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { PageHeader } from '../../components/ui/Primitives';
import { StaggerContainer, StaggerItem } from '../../components/animations/Reveal';
import { ProgressBar } from '../../components/ui/AnimatedNumber';
import Spotlight from '../../components/motion/Spotlight';
import TiltCard from '../../components/motion/TiltCard';
import { jobsData } from '../../data/social';
import { springs } from '../../lib/motionConfig';

export default function Jobs() {
  return (
    <div>
      <PageHeader title="Jobs" subtitle="Roles matched to your evidence-backed skill profile." />
      <StaggerContainer className="flex flex-col gap-3">
        {jobsData.map((j) => (
          <StaggerItem key={j.id}>
            <Link to={`/app/jobs/${j.id}`}>
              <TiltCard tiltMax={2.5}>
                <Spotlight>
                  <motion.div
                    className="card-flat flex flex-col sm:flex-row sm:items-center gap-4"
                    whileTap={{ scale: 0.99 }}
                    transition={springs.snappy}
                  >
                    <div className="flex-1">
                      <div className="h-display text-base">{j.title}</div>
                      <div className="text-textDim text-xs mt-1">{j.company} · {j.loc} · {j.type}</div>
                      <div className="flex gap-1.5 mt-2">
                        <span className="tech-pill">{j.salary}</span>
                        <span className="tech-pill">{j.posted}</span>
                      </div>
                    </div>
                    <div className="w-full sm:w-40">
                      <div className="flex justify-between text-[11px] mb-1">
                        <span>Match</span>
                        <span className={j.match >= 70 ? 'text-green' : 'text-textDim'}>{j.match}%</span>
                      </div>
                      <ProgressBar pct={j.match} tone={j.match < 50 ? 'red' : j.match < 70 ? 'amber' : ''} />
                    </div>
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

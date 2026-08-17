import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { PageHeader } from '../../components/ui/Primitives';
import { StaggerContainer, StaggerItem } from '../../components/animations/Reveal';
import Spotlight from '../../components/motion/Spotlight';
import TiltCard from '../../components/motion/TiltCard';
import Magnetic from '../../components/motion/Magnetic';
import { assessmentsData } from '../../data/recruiter';
import { springs } from '../../lib/motionConfig';

const STATUS_TONE = { 'NOT STARTED': '', COMPLETED: 'strong', EXPIRED: 'gap' };

export default function Assessments() {
  return (
    <div>
      <PageHeader title="Assessments" subtitle="Company and self-verify skill assessments." />
      <StaggerContainer className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {assessmentsData.map((a) => (
          <StaggerItem key={a.id}>
            <TiltCard tiltMax={3.5}>
              <Spotlight>
                <motion.div
                  className="card"
                  whileTap={{ scale: 0.985 }}
                  transition={springs.snappy}
                >
                  <div className="flex justify-between items-start">
                    <div className="h-display text-sm">{a.title}</div>
                    <span className={`badge ${STATUS_TONE[a.status]}`}>{a.status}</span>
                  </div>
                  <div className="text-textDim text-[11px] mt-1.5">{a.company} · {a.duration} min · {a.qcount} questions</div>
                  <div className="flex gap-1.5 flex-wrap mt-2.5">
                    {a.skills.map((s) => (
                      <span key={s} className="tech-pill">{s}</span>
                    ))}
                  </div>
                  {a.status === 'COMPLETED' ? (
                    <div className="mt-3.5 text-green mono text-sm">SCORE: {a.score}%</div>
                  ) : a.status === 'NOT STARTED' ? (
                    <Magnetic strength={0.15}>
                      <Link to={`/app/assessments/${a.id}/take`} className="btn-primary w-full justify-center mt-3.5">
                        START ASSESSMENT
                      </Link>
                    </Magnetic>
                  ) : (
                    <div className="mt-3.5 text-textMute mono text-[11px]">Assessment window closed</div>
                  )}
                </motion.div>
              </Spotlight>
            </TiltCard>
          </StaggerItem>
        ))}
      </StaggerContainer>
    </div>
  );
}

import { useState } from 'react';
import { motion } from 'framer-motion';
import { PageHeader } from '../../components/ui/Primitives';
import { StaggerContainer, StaggerItem } from '../../components/animations/Reveal';
import { ProgressBar } from '../../components/ui/AnimatedNumber';
import { gaps } from '../../data/skills';
import { springs } from '../../lib/motionConfig';

const ROLES = ['Backend Developer', 'Full Stack Developer', 'AI/ML Engineer', 'DevOps Engineer'];

export default function Gaps() {
  const [role, setRole] = useState(ROLES[0]);
  return (
    <div>
      <PageHeader
        title="Skill Gaps"
        subtitle="See what you need for your target role."
        actions={
          <select className="field-input w-[220px] m-0" value={role} onChange={(e) => setRole(e.target.value)}>
            {ROLES.map((r) => (
              <option key={r}>{r}</option>
            ))}
          </select>
        }
      />
      <StaggerContainer className="flex flex-col gap-2.5">
        {gaps.map((g) => (
          <StaggerItem key={g.name}>
            <motion.div
              className="skill-row cursor-default"
              whileHover={{ x: 2 }}
              transition={springs.snappy}
            >
              <div className="flex-1 min-w-0">
                <div className="flex justify-between items-center">
                  <span className="skill-name">{g.name}</span>
                  <span className="text-textDim text-[11px]">{g.current}% → {g.target}%</span>
                </div>
                <div className="mt-2">
                  <ProgressBar pct={g.current} tone="amber" />
                </div>
              </div>
              <span className={`badge ${g.cls}`}>{g.priority}</span>
            </motion.div>
          </StaggerItem>
        ))}
      </StaggerContainer>
    </div>
  );
}

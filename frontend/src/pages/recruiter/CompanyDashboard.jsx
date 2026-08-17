import { motion } from 'framer-motion';
import { PageHeader, Card } from '../../components/ui/Primitives';
import { AnimatedNumber } from '../../components/ui/AnimatedNumber';
import { Reveal, StaggerContainer, StaggerItem } from '../../components/animations/Reveal';
import { campaignsData, candidatesData } from '../../data/recruiter';
import { springs } from '../../lib/motionConfig';

export default function CompanyDashboard() {
  const activeCampaigns = campaignsData.filter((c) => c.state === 'Active').length;
  const totalInvited = campaignsData.reduce((s, c) => s + c.invited, 0);
  const totalCompleted = campaignsData.reduce((s, c) => s + c.completed, 0);

  return (
    <div>
      <PageHeader title="Recruiter Dashboard" subtitle="Evidence-backed hiring pipeline overview." />
      <StaggerContainer className="grid grid-cols-2 md:grid-cols-4 gap-4" stagger={0.06}>
        {[
          { label: 'Active Campaigns', value: activeCampaigns, tone: 'text-green' },
          { label: 'Candidates Invited', value: totalInvited, tone: '' },
          { label: 'Assessments Completed', value: totalCompleted, tone: '' },
          { label: 'Open Roles', value: 4, tone: '' },
        ].map((s) => (
          <StaggerItem key={s.label}>
            <Card>
              <div className="eyebrow">{s.label}</div>
              <div className={`big-num text-3xl ${s.tone}`}><AnimatedNumber value={s.value} /></div>
            </Card>
          </StaggerItem>
        ))}
      </StaggerContainer>

      <div className="divider" />
      <Reveal>
        <div className="text-xs tracking-widest uppercase text-textDim mb-4">Top Candidates</div>
      </Reveal>
      <StaggerContainer className="flex flex-col gap-2.5">
        {candidatesData.slice(0, 4).map((c) => (
          <StaggerItem key={c.name}>
            <motion.div
              className="skill-row cursor-default"
              whileHover={{ x: 2 }}
              transition={springs.snappy}
            >
              <div>
                <div className="skill-name">{c.name}</div>
                <div className="text-textDim text-[10px] mt-1">{c.skills}</div>
              </div>
              <span className="badge strong">{c.score}%</span>
            </motion.div>
          </StaggerItem>
        ))}
      </StaggerContainer>
    </div>
  );
}

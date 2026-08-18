import { PageHeader, Card } from '../../components/ui/Primitives';
import { AnimatedNumber } from '../../components/ui/AnimatedNumber';
import { Reveal, StaggerContainer, StaggerItem } from '../../components/animations/Reveal';
import { campaignsData, candidatesData } from '../../data/recruiter';

export default function CompanyDashboard() {
  const activeCampaigns = campaignsData.filter((c) => c.state === 'Active').length;
  const totalInvited = campaignsData.reduce((s, c) => s + c.invited, 0);
  const totalCompleted = campaignsData.reduce((s, c) => s + c.completed, 0);

  return (
    <div>
      <PageHeader title="Recruiter Dashboard" subtitle="Evidence-backed hiring pipeline overview." />
      <StaggerContainer className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StaggerItem>
          <Card>
            <div className="eyebrow">Active Campaigns</div>
            <div className="big-num text-green text-3xl"><AnimatedNumber value={activeCampaigns} /></div>
          </Card>
        </StaggerItem>
        <StaggerItem>
          <Card>
            <div className="eyebrow">Candidates Invited</div>
            <div className="big-num text-3xl"><AnimatedNumber value={totalInvited} /></div>
          </Card>
        </StaggerItem>
        <StaggerItem>
          <Card>
            <div className="eyebrow">Assessments Completed</div>
            <div className="big-num text-3xl"><AnimatedNumber value={totalCompleted} /></div>
          </Card>
        </StaggerItem>
        <StaggerItem>
          <Card>
            <div className="eyebrow">Open Roles</div>
            <div className="big-num text-3xl"><AnimatedNumber value={4} /></div>
          </Card>
        </StaggerItem>
      </StaggerContainer>

      <div className="divider" />
      <Reveal>
        <div className="text-xs tracking-widest uppercase text-textDim mb-4">Top Candidates</div>
      </Reveal>
      <StaggerContainer className="flex flex-col gap-2.5">
        {candidatesData.slice(0, 4).map((c) => (
          <StaggerItem key={c.name}>
            <div className="skill-row cursor-default">
              <div>
                <div className="skill-name">{c.name}</div>
                <div className="text-textDim text-[10px] mt-1">{c.skills}</div>
              </div>
              <span className="badge strong">{c.score}%</span>
            </div>
          </StaggerItem>
        ))}
      </StaggerContainer>
    </div>
  );
}

import { PageHeader, Card } from '../../components/ui/Primitives';
import { Reveal, StaggerContainer, StaggerItem } from '../../components/animations/Reveal';
import { AnimatedNumber, ProgressBar } from '../../components/ui/AnimatedNumber';
import { campaignsData } from '../../data/recruiter';

const funnel = [
  { label: 'Invited', pct: 100 },
  { label: 'Started', pct: 74 },
  { label: 'Completed', pct: 58 },
  { label: 'Shortlisted', pct: 21 },
  { label: 'Interviewed', pct: 10 },
  { label: 'Selected', pct: 4 },
];

export default function CompanyAnalytics() {
  const totalInvited = campaignsData.reduce((s, c) => s + c.invited, 0);
  const totalSelected = campaignsData.reduce((s, c) => s + c.selected, 0);

  return (
    <div>
      <PageHeader title="Analytics" subtitle="Hiring funnel and campaign performance." />
      <StaggerContainer className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StaggerItem>
          <Card>
            <div className="eyebrow">Total Invited</div>
            <div className="big-num text-3xl"><AnimatedNumber value={totalInvited} /></div>
          </Card>
        </StaggerItem>
        <StaggerItem>
          <Card>
            <div className="eyebrow">Conversion Rate</div>
            <div className="big-num text-green text-3xl"><AnimatedNumber value={4} suffix="%" /></div>
          </Card>
        </StaggerItem>
        <StaggerItem>
          <Card>
            <div className="eyebrow">Avg. Time to Hire</div>
            <div className="big-num text-3xl"><AnimatedNumber value={18} suffix="d" /></div>
          </Card>
        </StaggerItem>
        <StaggerItem>
          <Card>
            <div className="eyebrow">Selected</div>
            <div className="big-num text-3xl"><AnimatedNumber value={totalSelected} /></div>
          </Card>
        </StaggerItem>
      </StaggerContainer>
      <div className="divider" />
      <Reveal>
        <div className="text-xs tracking-widest uppercase text-textDim mb-4">Hiring Funnel</div>
      </Reveal>
      <StaggerContainer className="flex flex-col gap-4">
        {funnel.map((f) => (
          <StaggerItem key={f.label}>
            <div>
              <div className="flex justify-between text-xs mb-1.5">
                <span>{f.label}</span>
                <span className="text-textDim">{f.pct}%</span>
              </div>
              <ProgressBar pct={f.pct} />
            </div>
          </StaggerItem>
        ))}
      </StaggerContainer>
    </div>
  );
}

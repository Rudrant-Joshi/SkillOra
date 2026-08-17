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
      <StaggerContainer className="grid grid-cols-2 md:grid-cols-4 gap-4" stagger={0.06}>
        {[
          { label: 'Total Invited', value: totalInvited, tone: '' },
          { label: 'Conversion Rate', value: 4, suffix: '%', tone: 'text-green' },
          { label: 'Avg. Time to Hire', value: 18, suffix: 'd', tone: '' },
          { label: 'Selected', value: totalSelected, tone: '' },
        ].map((s) => (
          <StaggerItem key={s.label}>
            <Card>
              <div className="eyebrow">{s.label}</div>
              <div className={`big-num text-3xl ${s.tone}`}><AnimatedNumber value={s.value} suffix={s.suffix || ''} /></div>
            </Card>
          </StaggerItem>
        ))}
      </StaggerContainer>
      <div className="divider" />
      <Reveal>
        <div className="text-xs tracking-widest uppercase text-textDim mb-4">Hiring Funnel</div>
      </Reveal>
      <div className="flex flex-col gap-4">
        {funnel.map((f, i) => (
          <Reveal key={f.label} delay={i * 0.06}>
            <div>
              <div className="flex justify-between text-xs mb-1.5">
                <span>{f.label}</span>
                <span className="text-textDim">{f.pct}%</span>
              </div>
              <ProgressBar pct={f.pct} />
            </div>
          </Reveal>
        ))}
      </div>
    </div>
  );
}

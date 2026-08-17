import { PageHeader } from '../../components/ui/Primitives';
import { StaggerContainer, StaggerItem } from '../../components/animations/Reveal';
import { applicationsData } from '../../data/social';

const STAGE_TONE = { Applied: '', 'Technical Assessment': 'warn', Interview: 'strong', Offer: 'strong', Rejected: 'gap' };

export default function Applications() {
  return (
    <div>
      <PageHeader title="Applications" subtitle="Track the status of every job you've applied to." />
      <StaggerContainer className="flex flex-col gap-2.5">
        {applicationsData.map((a, i) => (
          <StaggerItem key={i}>
            <div className="skill-row cursor-default">
              <div>
                <div className="skill-name">{a.job}</div>
                <div className="text-textDim text-[10px] mt-1">{a.company} · Applied {a.applied}</div>
              </div>
              <span className={`badge ${STAGE_TONE[a.stage] || ''}`}>{a.stage.toUpperCase()}</span>
            </div>
          </StaggerItem>
        ))}
      </StaggerContainer>
    </div>
  );
}

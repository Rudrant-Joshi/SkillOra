import { PageHeader, Button } from '../../components/ui/Primitives';
import { StaggerContainer, StaggerItem } from '../../components/animations/Reveal';
import { assessmentsData } from '../../data/recruiter';

const STATUS_TONE = { 'NOT STARTED': '', COMPLETED: 'strong', EXPIRED: 'gap' };

export default function Assessments() {
  return (
    <div>
      <PageHeader title="Assessments" subtitle="Company and self-verify skill assessments." />
      <StaggerContainer className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {assessmentsData.map((a) => (
          <StaggerItem key={a.id}>
            <div className="card">
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
                <div className="mt-3.5 text-green mono text-sm font-bold">SCORE: {a.score}%</div>
              ) : a.status === 'NOT STARTED' ? (
                <div className="mt-3.5">
                  <Button to={`/app/assessments/${a.id}/take`} tone="primary" className="w-full justify-center">
                    START ASSESSMENT
                  </Button>
                </div>
              ) : (
                <div className="mt-3.5 text-textMute mono text-[11px]">Assessment window closed</div>
              )}
            </div>
          </StaggerItem>
        ))}
      </StaggerContainer>
    </div>
  );
}

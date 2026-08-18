import { PageHeader, Card, Button, EmptyState } from '../../components/ui/Primitives';
import { ProgressBar } from '../../components/ui/AnimatedNumber';
import { Reveal, StaggerContainer, StaggerItem } from '../../components/animations/Reveal';
import { jobsData } from '../../data/social';
import { useToast } from '../../context/ToastContext';

export default function JobDetail() {
  const { id } = useParams();
  const job = jobsData.find((j) => j.id === id);
  const [applied, setApplied] = useState(false);
  const { showToast } = useToast();

  if (!job) {
    return (
      <div>
        <PageHeader title="Job Not Found" />
        <EmptyState>This job posting doesn't exist in this demo dataset.</EmptyState>
      </div>
    );
  }

  const handleApply = () => {
    setApplied(true);
    showToast(`Applied to ${job.title} at ${job.company}`);
  };

  return (
    <div>
      <PageHeader
        title={job.title}
        subtitle={`${job.company} · ${job.loc} · ${job.type} · ${job.salary}`}
        actions={
          <Button tone="primary" onClick={handleApply} disabled={applied}>
            {applied ? '✓ APPLIED' : 'APPLY NOW'}
          </Button>
        }
      />
      <Reveal>
        <Card hover>
          <div className="flex justify-between items-center mb-3 font-mono">
            <div className="eyebrow m-0 text-white/90">Overall Match</div>
            <span className={`badge ${job.match >= 70 ? 'strong' : job.match >= 50 ? 'warn' : 'gap'}`}>{job.match}% MATCH</span>
          </div>
          <ProgressBar pct={job.match} tone={job.match < 50 ? 'red' : job.match < 70 ? 'amber' : ''} />
        </Card>
      </Reveal>

      <div className="divider" />
      <Reveal>
        <div className="text-xs tracking-widest uppercase text-textDim mb-4">Requirement Breakdown</div>
      </Reveal>
      <StaggerContainer className="flex flex-col gap-3">
        {job.req.map((r) => {
          const met = r.have >= r.need;
          return (
            <StaggerItem key={r.s}>
              <div className="skill-row cursor-default">
                <div className="flex-1 min-w-0">
                  <div className="flex justify-between text-[11px] mb-1.5">
                    <span>{r.s}</span>
                    <span className="text-textDim">You: {r.have}% · Need: {r.need}%</span>
                  </div>
                  <ProgressBar pct={r.have} tone={!met ? 'red' : ''} />
                </div>
                <span className={`badge ${met ? 'strong' : 'gap'} ml-3`}>{met ? 'MET' : 'GAP'}</span>
              </div>
            </StaggerItem>
          );
        })}
      </StaggerContainer>
    </div>
  );
}

import { PageHeader, Button } from '../../components/ui/Primitives';
import DataTable from '../../components/ui/DataTable';
import { interviewsData } from '../../data/recruiter';

const STATUS_TONE = { Scheduled: 'strong', Upcoming: 'warn', Completed: '' };

export default function CompanyInterviews() {
  return (
    <div>
      <PageHeader title="Interviews" subtitle="Upcoming and completed candidate interviews." actions={<Button tone="primary">+ SCHEDULE INTERVIEW</Button>} />
      <DataTable
        columns={['Candidate', 'Position', 'Type', 'Date', 'Time', 'Interviewer', 'Status']}
        rows={interviewsData}
        renderRow={(i) => (
          <>
            <td className="px-4 py-3">{i.candidate}</td>
            <td className="px-4 py-3 text-textDim">{i.position}</td>
            <td className="px-4 py-3"><span className="tech-pill">{i.type}</span></td>
            <td className="px-4 py-3 text-textDim">{i.date}</td>
            <td className="px-4 py-3 text-textDim">{i.time}</td>
            <td className="px-4 py-3 text-textDim">{i.interviewers}</td>
            <td className="px-4 py-3"><span className={`badge ${STATUS_TONE[i.status] || ''}`}>{i.status.toUpperCase()}</span></td>
          </>
        )}
      />
    </div>
  );
}

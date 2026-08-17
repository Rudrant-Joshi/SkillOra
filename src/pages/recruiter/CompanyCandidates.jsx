import { Link } from 'react-router-dom';
import { PageHeader } from '../../components/ui/Primitives';
import DataTable from '../../components/ui/DataTable';
import { candidatesData } from '../../data/recruiter';

const STATUS_TONE = { 'Assessment Complete': 'strong', 'In Progress': 'warn', Invited: '' };

export default function CompanyCandidates() {
  return (
    <div>
      <PageHeader title="Candidates" subtitle="Applicant pipeline ranked by verified skill score." />
      <DataTable
        columns={['Candidate', 'Score', 'Skills', 'Status', 'Time Taken', 'Coding', 'AI Score', '']}
        rows={candidatesData}
        renderRow={(c, i) => (
          <>
            <td className="px-4 py-3">{c.name}</td>
            <td className="px-4 py-3 text-green">{c.score}%</td>
            <td className="px-4 py-3 text-textDim">{c.skills}</td>
            <td className="px-4 py-3"><span className={`badge ${STATUS_TONE[c.status] || ''}`}>{c.status.toUpperCase()}</span></td>
            <td className="px-4 py-3 text-textDim">{c.time}</td>
            <td className="px-4 py-3 text-textDim">{c.coding}</td>
            <td className="px-4 py-3 text-textDim">{c.ai}</td>
            <td className="px-4 py-3">
              <Link to={`/recruiter/scorecard/${i}`} className="btn-small">
                SCORECARD →
              </Link>
            </td>
          </>
        )}
      />
    </div>
  );
}

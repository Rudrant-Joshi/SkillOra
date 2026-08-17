import { PageHeader } from '../../components/ui/Primitives';
import DataTable from '../../components/ui/DataTable';
import { teamData } from '../../data/recruiter';

export default function CompanyTeam() {
  return (
    <div>
      <PageHeader title="Team" subtitle="Manage recruiter and admin access." actions={<button className="btn-primary">+ INVITE MEMBER</button>} />
      <DataTable
        columns={['Name', 'Role', 'Email', '']}
        rows={teamData}
        renderRow={(t) => (
          <>
            <td className="px-4 py-3">{t.name}</td>
            <td className="px-4 py-3"><span className="tech-pill">{t.role}</span></td>
            <td className="px-4 py-3 text-textDim">{t.email}</td>
            <td className="px-4 py-3"><button className="btn-small">REMOVE</button></td>
          </>
        )}
      />
    </div>
  );
}

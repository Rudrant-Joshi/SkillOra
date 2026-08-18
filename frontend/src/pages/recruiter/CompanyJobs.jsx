import { PageHeader, Button } from '../../components/ui/Primitives';
import DataTable from '../../components/ui/DataTable';
import { jobsData } from '../../data/social';

export default function CompanyJobs() {
  return (
    <div>
      <PageHeader title="Jobs" subtitle="Manage your company's open roles." actions={<Button tone="primary">+ POST NEW JOB</Button>} />
      <DataTable
        columns={['Role', 'Location', 'Type', 'Salary', 'Posted', 'Status']}
        rows={jobsData}
        renderRow={(j) => (
          <>
            <td className="px-4 py-3">{j.title}</td>
            <td className="px-4 py-3 text-textDim">{j.loc}</td>
            <td className="px-4 py-3 text-textDim">{j.type}</td>
            <td className="px-4 py-3 text-textDim">{j.salary}</td>
            <td className="px-4 py-3 text-textDim">{j.posted}</td>
            <td className="px-4 py-3"><span className="badge strong">OPEN</span></td>
          </>
        )}
      />
    </div>
  );
}

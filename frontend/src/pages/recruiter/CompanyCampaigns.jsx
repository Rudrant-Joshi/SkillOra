import { PageHeader, Button } from '../../components/ui/Primitives';
import DataTable from '../../components/ui/DataTable';
import { campaignsData } from '../../data/recruiter';

const STATE_TONE = { Active: 'strong', Draft: '', Completed: 'warn' };

export default function CompanyCampaigns() {
  return (
    <div>
      <PageHeader title="Hiring Campaigns" subtitle="Track outreach, completion, and conversion by campaign." actions={<Button tone="primary">+ NEW CAMPAIGN</Button>} />
      <DataTable
        columns={['Campaign', 'Job', 'State', 'Invited', 'Started', 'Completed', 'Shortlisted', 'Selected']}
        rows={campaignsData}
        renderRow={(c) => (
          <>
            <td className="px-4 py-3">{c.name}</td>
            <td className="px-4 py-3 text-textDim">{c.job}</td>
            <td className="px-4 py-3"><span className={`badge ${STATE_TONE[c.state]}`}>{c.state.toUpperCase()}</span></td>
            <td className="px-4 py-3 text-textDim">{c.invited}</td>
            <td className="px-4 py-3 text-textDim">{c.started}</td>
            <td className="px-4 py-3 text-textDim">{c.completed}</td>
            <td className="px-4 py-3 text-textDim">{c.shortlisted}</td>
            <td className="px-4 py-3 text-green">{c.selected}</td>
          </>
        )}
      />
    </div>
  );
}

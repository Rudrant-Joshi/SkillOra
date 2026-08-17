import { PageHeader } from '../../components/ui/Primitives';
import DataTable from '../../components/ui/DataTable';
import { questionBankData } from '../../data/recruiter';

const DIFF_TONE = { Easy: 'strong', Medium: 'warn', Hard: 'gap' };

export default function CompanyQuestions() {
  return (
    <div>
      <PageHeader title="Question Bank" subtitle="Reusable questions for building assessments." actions={<button className="btn-primary">+ ADD QUESTION</button>} />
      <DataTable
        columns={['Question', 'Type', 'Topic', 'Skill', 'Difficulty']}
        rows={questionBankData}
        renderRow={(q) => (
          <>
            <td className="px-4 py-3 max-w-[320px]">{q.q}</td>
            <td className="px-4 py-3 text-textDim">{q.type}</td>
            <td className="px-4 py-3 text-textDim">{q.topic}</td>
            <td className="px-4 py-3"><span className="tech-pill">{q.skill}</span></td>
            <td className="px-4 py-3"><span className={`badge ${DIFF_TONE[q.diff]}`}>{q.diff.toUpperCase()}</span></td>
          </>
        )}
      />
    </div>
  );
}

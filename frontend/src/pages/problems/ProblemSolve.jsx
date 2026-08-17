import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { PageHeader, EmptyState } from '../../components/ui/Primitives';
import CodeEditor from '../../components/editors/CodeEditor';
import { ExecutionResult, useExecution } from '../../components/editors/ExecutionPanel';
import { problemsData } from '../../data/code';
import { useDemoState } from '../../context/DemoStateContext';

const LANGS = ['Python', 'JavaScript', 'Java', 'C++', 'C'];

export default function ProblemSolve() {
  const { id } = useParams();
  const problem = problemsData.find((p) => p.id === id);
  const { solved, markSolved } = useDemoState();
  const [lang, setLang] = useState('Python');
  const [code, setCode] = useState(problem?.starter || '');
  const exec = useExecution();

  useEffect(() => {
    setCode(problem?.starter || '');
  }, [problem]);

  if (!problem) {
    return (
      <div>
        <PageHeader title="Problem Not Found" />
        <EmptyState>That problem doesn't exist in this demo set.</EmptyState>
      </div>
    );
  }

  const isSolved = solved.includes(problem.id);

  const handleRun = () => exec.run('run', code);
  const handleSubmit = () => {
    exec.run('submit', code);
  };

  useEffect(() => {
    if (exec.result?.status === 'accepted' && exec.status === 'ACCEPTED') {
      markSolved(problem.id);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [exec.result, exec.status]);

  return (
    <div>
      <PageHeader
        title={problem.title}
        subtitle={problem.tags.join(' · ')}
        actions={<span className={`badge ${problem.diff === 'Easy' ? 'strong' : problem.diff === 'Medium' ? 'warn' : 'gap'}`}>{problem.diff.toUpperCase()}</span>}
      />

      {isSolved && <div className="badge strong mb-4">✓ SOLVED</div>}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <div className="card-flat">
            <div className="eyebrow">Description</div>
            <div className="text-xs leading-relaxed mt-2">{problem.desc}</div>
            <div className="divider-dim" />
            <div className="eyebrow">Example</div>
            <div className="mono text-xs mt-2 bg-surface2 p-3">
              <div>Input: {problem.examples[0].in}</div>
              <div className="text-green mt-1">Output: {problem.examples[0].out}</div>
            </div>
            <div className="divider-dim" />
            <div className="eyebrow">Constraints</div>
            <div className="mono text-xs mt-2 text-textDim">{problem.constraints}</div>
          </div>
        </div>

        <div>
          <div className="flex justify-between items-center mb-2">
            <select className="field-input w-[160px] m-0" value={lang} onChange={(e) => setLang(e.target.value)}>
              {LANGS.map((l) => (
                <option key={l}>{l}</option>
              ))}
            </select>
            <div className="mono text-[11px] flex items-center gap-1.5 text-textDim">
              <span className="status-dot" style={{ background: exec.running ? '#fff' : exec.result?.status === 'accepted' ? 'var(--green)' : '#fff' }} />
              {exec.status || 'IDLE'}
            </div>
          </div>
          <CodeEditor value={code} onChange={setCode} language={lang} originalValue={problem.starter} height={300} />
          <div className="flex gap-2.5 mt-3">
            <button className="btn-secondary flex-1 justify-center" onClick={handleRun} disabled={exec.running}>
              RUN
            </button>
            <button className="btn-primary flex-1 justify-center" onClick={handleSubmit} disabled={exec.running}>
              SUBMIT
            </button>
          </div>
          <div className="card-flat mt-4">
            <ExecutionResult result={exec.result} status={exec.status} text={exec.text} mode="submit" />
          </div>
        </div>
      </div>
    </div>
  );
}

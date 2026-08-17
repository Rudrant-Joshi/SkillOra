import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { PageHeader } from '../../components/ui/Primitives';
import CodeEditor from '../../components/editors/CodeEditor';
import { assessmentsData, examQuestions } from '../../data/recruiter';

export default function ExamTake() {
  const { id } = useParams();
  const assessment = assessmentsData.find((a) => a.id === id);
  const [qIndex, setQIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const navigate = useNavigate();
  const q = examQuestions[qIndex % examQuestions.length];

  const setAnswer = (v) => setAnswers((prev) => ({ ...prev, [qIndex]: v }));

  const next = () => {
    if (qIndex < examQuestions.length - 1) {
      setQIndex(qIndex + 1);
    } else {
      navigate(`/app/assessments/${id}/result`);
    }
  };

  return (
    <div>
      <PageHeader
        title={assessment?.title || 'Assessment'}
        subtitle={`Question ${qIndex + 1} of ${examQuestions.length} · Demo timed assessment (no backend judge)`}
      />
      <div className="progress-track mb-6">
        <div className="progress-fill" style={{ width: `${((qIndex + 1) / examQuestions.length) * 100}%` }} />
      </div>

      <AnimatePresence mode="wait">
        <motion.div key={qIndex} initial={{ opacity: 0, x: 12 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -12 }} transition={{ duration: 0.25 }}>
          <div className="card-flat">
            <div className="badge mb-3">{q.type}</div>
            <div className="text-sm leading-relaxed">{q.q}</div>

            {q.type === 'MCQ' && (
              <div className="flex flex-col gap-2 mt-4">
                {q.options.map((o, i) => (
                  <button
                    key={o}
                    onClick={() => setAnswer(i)}
                    className={`text-left px-4 py-3 border text-xs transition-colors ${
                      answers[qIndex] === i ? 'border-green text-green bg-surface2' : 'border-borderDim hover:border-white/40'
                    }`}
                  >
                    {o}
                  </button>
                ))}
              </div>
            )}

            {(q.type === 'SQL' || q.type === 'CODING') && (
              <div className="mt-4">
                <CodeEditor
                  value={answers[qIndex] ?? q.code}
                  onChange={setAnswer}
                  language={q.type === 'SQL' ? 'SQL' : 'Python'}
                  height={220}
                  originalValue={q.code}
                />
              </div>
            )}
          </div>
        </motion.div>
      </AnimatePresence>

      <div className="flex justify-end mt-5">
        <button className="btn-primary" onClick={next}>
          {qIndex === examQuestions.length - 1 ? 'FINISH ASSESSMENT' : 'NEXT QUESTION →'}
        </button>
      </div>
    </div>
  );
}

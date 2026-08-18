import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { PageHeader } from '../../components/ui/Primitives';
import CodeEditor from '../../components/editors/CodeEditor';
import { api } from '../../lib/api';
import { useAuth } from '../../context/AuthContext';

const QUESTION_TYPES = {
  mcq: 'MCQ',
  multi_select: 'MULTI-SELECT',
  coding: 'CODING',
  sql: 'SQL',
  short_answer: 'SHORT ANSWER',
  system_design: 'SYSTEM DESIGN',
};

export default function ExamTake() {
  const { id } = useParams();
  const [assessment, setAssessment] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [qIndex, setQIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [attemptId, setAttemptId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const { token } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    let cancelled = false;

    async function loadData() {
      setLoading(true);
      setError('');
      try {
        // Start the assessment to get/create an attempt
        const startResult = await api.startAssessment(id);
        setAttemptId(startResult.attempt_id);

        // Fetch questions
        const data = await api.getQuestions(id, startResult.attempt_id);
        if (!cancelled) {
          setAssessment({
            title: data.assessment_title || startResult.assessment_title,
            duration: data.duration_minutes || startResult.duration_minutes,
            isAdaptive: false,
          });
          setQuestions(data.questions || []);
        }
      } catch (err) {
        if (!cancelled) setError(err.message || 'Failed to load assessment');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadData();
    return () => { cancelled = true; };
  }, [id]);

  const setAnswer = (qid, value) => {
    setAnswers((prev) => ({ ...prev, [qid]: value }));
  };

  const next = () => {
    if (qIndex < questions.length - 1) {
      setQIndex(qIndex + 1);
    }
  };

  const prev = () => {
    if (qIndex > 0) setQIndex(qIndex - 1);
  };

  const finish = async () => {
    setSubmitting(true);
    setError('');
    try {
      const answersPayload = questions.map((q) => {
        const ans = answers[q.id];
        const base = {
          question_id: q.id,
          question_type: q.question_type,
          time_spent_seconds: 0,
          compiled: true,
        };
        if (q.question_type === 'mcq' || q.question_type === 'multi_select') {
          return { ...base, submitted_options: Array.isArray(ans) ? ans : [ans] };
        }
        if (q.question_type === 'coding' || q.question_type === 'sql') {
          return { ...base, submitted_code: ans || q.starter_code || '' };
        }
        return { ...base, submitted_answer: ans || '' };
      });

      await api.submitAnswers(attemptId, answersPayload);
      navigate(`/app/assessments/${id}/result?attempt_id=${attemptId}`);
    } catch (err) {
      setError(err.message || 'Failed to submit assessment');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div>
        <PageHeader
          title="Loading Assessment"
          subtitle={assessment?.title || 'Connecting to backend…'}
        />
        <div className="text-textDim">Fetching questions via ML gateway-backed scoring pipeline…</div>
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <PageHeader title={assessment?.title || 'Assessment'} subtitle="Error loading assessment" />
        <div className="text-red mono">{error}</div>
      </div>
    );
  }

  const q = questions[qIndex];
  if (!q) return null;

  return (
    <div>
      <PageHeader
        title={assessment?.title || 'Assessment'}
        subtitle={`Question ${qIndex + 1} of ${questions.length} · ${api.token ? 'Backend connected' : 'Offline mode'}`}
      />
      <div className="progress-track mb-6">
        <div className="progress-fill" style={{ width: `${((qIndex + 1) / questions.length) * 100}%` }} />
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={qIndex}
          initial={{ opacity: 0, x: 12 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -12 }}
          transition={{ duration: 0.25 }}
        >
          <div className="card-flat">
            <div className="badge mb-3">{QUESTION_TYPES[q.question_type] || q.question_type.toUpperCase()}</div>
            <div
              className="text-sm leading-relaxed"
              dangerouslySetInnerHTML={{ __html: q.prompt.replace(/\n/g, '<br/>') }}
            />

            {(q.question_type === 'mcq' || q.question_type === 'multi_select') && (
              <div className="flex flex-col gap-2 mt-4">
                {q.options.map((o, i) => {
                  const selected = answers[q.id];
                  const isSelected =
                    q.question_type === 'mcq'
                      ? selected === i
                      : Array.isArray(selected) && selected.includes(i);
                  return (
                    <button
                      key={i}
                      onClick={() => {
                        if (q.question_type === 'mcq') setAnswer(q.id, i);
                        else {
                          const newSel = Array.isArray(selected) ? [...selected] : [];
                          const idx = newSel.indexOf(i);
                          if (idx >= 0) newSel.splice(idx, 1);
                          else newSel.push(i);
                          setAnswer(q.id, newSel);
                        }
                      }}
                      className={`text-left px-4 py-3 border text-xs transition-colors ${
                        isSelected
                          ? 'border-green text-green bg-surface2'
                          : 'border-borderDim hover:border-white/40'
                      }`}
                    >
                      {o}
                    </button>
                  );
                })}
              </div>
            )}

            {(q.question_type === 'sql' || q.question_type === 'coding') && (
              <div className="mt-4">
                <CodeEditor
                  value={answers[q.id] ?? q.starter_code ?? ''}
                  onChange={(v) => setAnswer(q.id, v)}
                  language={q.question_type === 'sql' ? 'SQL' : 'Python'}
                  height={220}
                  originalValue={q.starter_code ?? ''}
                />
              </div>
            )}

            {q.question_type === 'short_answer' && (
              <textarea
                className="field-input mt-4 w-full"
                rows={4}
                placeholder="Write your answer here…"
                value={answers[q.id] ?? ''}
                onChange={(e) => setAnswer(q.id, e.target.value)}
              />
            )}

            {q.question_type === 'system_design' && (
              <textarea
                className="field-input mt-4 w-full"
                rows={6}
                placeholder="Explain your design approach…"
                value={answers[q.id] ?? ''}
                onChange={(e) => setAnswer(q.id, e.target.value)}
              />
            )}
          </div>
        </motion.div>
      </AnimatePresence>

      <div className="flex justify-between mt-5">
        <button className="btn-secondary" onClick={prev} disabled={qIndex === 0}>
          ← PREVIOUS
        </button>
        <div className="flex gap-3">
          {qIndex < questions.length - 1 ? (
            <button className="btn-primary" onClick={next}>
              NEXT QUESTION →
            </button>
          ) : (
            <button className="btn-primary" onClick={finish} disabled={submitting}>
              {submitting ? 'SUBMITTING…' : 'FINISH ASSESSMENT →'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

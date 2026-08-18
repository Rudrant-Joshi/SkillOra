import { Link, useParams, useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';
import { PageHeader } from '../../components/ui/Primitives';
import { AnimatedNumber } from '../../components/ui/AnimatedNumber';
import { api } from '../../lib/api';
import { springs } from '../../lib/motionConfig';

export default function ExamResult() {
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  const attemptId = searchParams.get('attempt_id');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function fetchResult() {
      if (!attemptId) {
        setLoading(false);
        return;
      }
      try {
        const data = await api.getAttempt(attemptId);
        setResult(data);
      } catch (err) {
        setError(err.message || 'Failed to load results');
      } finally {
        setLoading(false);
      }
    }
    fetchResult();
  }, [attemptId]);

  if (loading) {
    return (
      <div>
        <PageHeader title="Assessment Complete" subtitle="Scoring with ML gateway…" />
        <div className="text-textDim">Backend is evaluating your answers via the ML gateway.</div>
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <PageHeader title="Assessment Complete" subtitle="Error loading results" />
        <div className="text-red mono">{error}</div>
      </div>
    );
  }

  const score = result?.overall_score ?? result?.overall_score ?? 0;
  const rawScore = result?.raw_score ?? 0;
  const mlScore = result?.ml_score ?? 0;
  const questionCount = result?.questions_count ?? 0;
  const dimensionScores = result?.dimension_scores ?? {};
  const skills = result?.skills ?? {};
  const evidence = result?.evidence ?? [];
  const dimensionDetails = result?.dimension_details ?? {};

  const topSkills = Object.entries(skills)
    .sort((a, b) => b[1].level - a[1].level)
    .slice(0, 6);

  return (
    <div>
      <PageHeader title="Assessment Complete" subtitle={result?.assessment_title || 'Results'} />

      {/* Score Panel */}
      <div className="offset-panel">
        <div className="inner p-9 text-center">
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.4 }}
          >
            <div className="eyebrow">Your Score</div>
            <div className="h-display text-green text-6xl mt-2">
              <AnimatedNumber value={score} suffix="%" />
            </div>
            <div className="flex gap-4 justify-center mt-4 text-xs mono">
              <span>Raw: {Math.round(rawScore)}%</span>
              <span>ML: {Math.round(mlScore)}%</span>
              <span>Questions: {questionCount}</span>
            </div>
            <div className="badge strong mt-4">◆ ML-SCORED RESULT</div>
          </motion.div>
        </div>
      </div>

      {/* Dimension Scores */}
      {Object.keys(dimensionScores).length > 0 && (
        <div className="mt-6">
          <h3 className="h-display text-sm mb-3">Dimension Scores</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {Object.entries(dimensionScores).map(([dim, scr]) => {
              const details = dimensionDetails[dim] || {};
              return (
                <div key={dim} className="card-flat p-3 text-center">
                  <div className="text-[11px] text-textDim uppercase">{dim}</div>
                  <div className="h-display text-lg text-green">{Math.round(scr)}%</div>
                  {details.evidence_count !== undefined && (
                    <div className="text-[10px] text-textDim mt-1">{details.evidence_count} evidence</div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Skill Estimates */}
      {topSkills.length > 0 && (
        <div className="mt-6">
          <h3 className="h-display text-sm mb-3">Skill Estimates</h3>
          <div className="space-y-3">
            {topSkills.map(([skill, est]) => (
              <div key={skill} className="card-flat p-3">
                <div className="flex justify-between">
                  <span className="font-medium">{skill}</span>
                  <span className="text-green mono">{Math.round(est.level * 100)}%</span>
                </div>
                <div className="progress-track mt-1.5">
                  <div
                    className="progress-fill bg-green"
                    style={{ width: `${est.level * 100}%` }}
                  />
                </div>
                <div className="flex justify-between text-[10px] text-textDim mt-1">
                  <span>Confidence: {Math.round((est.confidence || 0) * 100)}%</span>
                  <span>{est.evidence_count || 0} evidence</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Evidence */}
      {evidence.length > 0 && (
        <div className="mt-6">
          <h3 className="h-display text-sm mb-3">Evidence</h3>
          <ul className="list-disc list-inside text-sm text-textDim space-y-1">
            {evidence.map((e, i) => (
              <li key={i}>{e}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="flex gap-3 mt-6">
        <Link to="/app/assessments" className="btn-secondary">
          BACK TO ASSESSMENTS
        </Link>
        <Link to="/app/passport" className="btn-primary">
          VIEW SKILL PASSPORT
        </Link>
      </div>
    </div>
  );
}

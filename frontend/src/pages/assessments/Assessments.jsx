import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';
import { PageHeader } from '../../components/ui/Primitives';
import { StaggerContainer, StaggerItem } from '../../components/animations/Reveal';
import Spotlight from '../../components/motion/Spotlight';
import TiltCard from '../../components/motion/TiltCard';
import Magnetic from '../../components/motion/Magnetic';
import { springs } from '../../lib/motionConfig';
import { api } from '../../lib/api';

const STATUS_TONE = { 'NOT STARTED': '', IN_PROGRESS: 'strong', COMPLETED: 'strong', EXPIRED: 'gap' };
const STATUS_LABEL = { 'NOT STARTED': 'NOT STARTED', IN_PROGRESS: 'IN PROGRESS', COMPLETED: 'COMPLETED', EXPIRED: 'EXPIRED' };

export default function Assessments() {
  const [assessments, setAssessments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function fetchAssessments() {
      setLoading(true);
      setError('');
      try {
        const data = await api.listAssessments();
        const now = Date.now();
        const mapped = data.map((a) => {
          const attempts = a.attempts || [];
          const completed = attempts.filter((att) => att.status === 'submitted' || att.status === 'completed');
          let status = 'NOT STARTED';
          let score = null;

          if (completed.length > 0) {
            status = 'COMPLETED';
            score = completed[0].overall_score;
          } else if (attempts.some((att) => att.status === 'in_progress')) {
            status = 'IN_PROGRESS';
          }

          let durationLabel = a.duration_minutes ? `${a.duration_minutes} min` : '—';

          return {
            id: a.id,
            title: a.title,
            company: a.company || '',
            duration: durationLabel,
            qcount: a.total_questions || a.questions?.length || 0,
            skills: a.skills || [],
            status,
            score,
            isAdaptive: a.is_adaptive,
            attemptId: completed.length > 0 ? completed[0].id : (attempts.find((att) => att.status === 'in_progress')?.id || null),
          };
        });
        setAssessments(mapped);
      } catch (err) {
        setError(err.message || 'Failed to load assessments');
      } finally {
        setLoading(false);
      }
    }
    fetchAssessments();
  }, []);

  if (loading) {
    return (
      <div>
        <PageHeader title="Assessments" subtitle="Loading available assessments…" />
        <div className="text-textDim">Connecting to SkillGraph backend…</div>
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <PageHeader title="Assessments" subtitle="Failed to load assessments" />
        <div className="text-red mono">{error}</div>
      </div>
    );
  }

  if (assessments.length === 0) {
    return (
      <div>
        <PageHeader title="Assessments" subtitle="No assessments available." />
        <div className="text-textDim">No active assessments found for your company.</div>
      </div>
    );
  }

  return (
    <div>
      <PageHeader title="Assessments" subtitle="Company and self-verification skill assessments." />
      <StaggerContainer className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {assessments.map((a) => (
          <StaggerItem key={a.id}>
            <TiltCard tiltMax={3.5}>
              <Spotlight>
                <motion.div
                  className="card"
                  whileTap={{ scale: 0.985 }}
                  transition={springs.snappy}
                >
                  <div className="flex justify-between items-start">
                    <div className="h-display text-sm">{a.title}</div>
                    <span className={`badge ${STATUS_TONE[a.status] || ''}`}>{STATUS_LABEL[a.status] || a.status}</span>
                  </div>
                  <div className="text-textDim text-[11px] mt-1.5">{a.company} · {a.duration} · {a.qcount} questions</div>
                  <div className="flex gap-1.5 flex-wrap mt-2.5">
                    {a.skills.map((s) => (
                      <span key={s} className="tech-pill">{s}</span>
                    ))}
                  </div>
                  {a.status === 'COMPLETED' ? (
                    <div className="mt-3.5 text-green mono text-sm">SCORE: {Math.round(a.score)}%</div>
                  ) : a.status === 'IN_PROGRESS' ? (
                    <Magnetic strength={0.15}>
                      <Link to={`/app/assessments/${a.id}/take`} className="btn-primary w-full justify-center mt-3.5">
                        RESUME ASSESSMENT
                      </Link>
                    </Magnetic>
                  ) : a.status === 'NOT STARTED' ? (
                    <Magnetic strength={0.15}>
                      <Link to={`/app/assessments/${a.id}/take`} className="btn-primary w-full justify-center mt-3.5">
                        START ASSESSMENT
                      </Link>
                    </Magnetic>
                  ) : (
                    <div className="mt-3.5 text-textMute mono text-[11px]">Assessment window closed</div>
                  )}
                </motion.div>
              </Spotlight>
            </TiltCard>
          </StaggerItem>
        ))}
      </StaggerContainer>
    </div>
  );
}

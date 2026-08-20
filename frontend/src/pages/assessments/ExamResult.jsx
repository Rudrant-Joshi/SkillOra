import { useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { PageHeader, Button } from '../../components/ui/Primitives';
import { AnimatedNumber } from '../../components/ui/AnimatedNumber';
import { assessmentsData } from '../../data/recruiter';

export default function ExamResult() {
  const { id } = useParams();
  const assessment = assessmentsData.find((a) => a.id === id);
  const score = 78; // deterministic demo score

  return (
    <div>
      <PageHeader title="Assessment Complete" subtitle={assessment?.title} />
      <div className="offset-panel">
        <div className="inner p-9 text-center">
          <motion.div initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ duration: 0.4 }}>
            <div className="eyebrow">Your Score</div>
            <div className="h-display text-green text-6xl mt-2">
              <AnimatedNumber value={score} suffix="%" />
            </div>
            <div className="badge strong mt-4">◆ VERIFIED RESULT · DEMO EXECUTION</div>
          </motion.div>
        </div>
      </div>
      <div className="flex gap-3 mt-6 flex-wrap">
        <Button to="/app/assessments" tone="secondary">
          BACK TO ASSESSMENTS
        </Button>
        <Button to="/app/passport" tone="primary">
          VIEW SKILL PASSPORT
        </Button>
      </div>
    </div>
  );
}

import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center text-center px-5">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
        <div className="h-display text-6xl">404</div>
        <div className="text-textDim text-sm mt-3">This route doesn't exist in the SkillGraph demo.</div>
        <Link to="/" className="btn-primary inline-flex mt-6">
          BACK TO HOME
        </Link>
      </motion.div>
    </div>
  );
}

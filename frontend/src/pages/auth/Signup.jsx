import { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export default function Signup() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    const dest = login({ email: email || 'new-user@demo.dev', role: 'developer' });
    navigate(dest, { replace: true });
  };

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} className="w-[420px] max-w-full offset-panel">
      <div className="inner px-8 sm:px-10 pt-11 pb-9">
        <div className="h-display text-[34px] tracking-tight mb-1">
          SKILL<span className="text-green">GRAPH</span>
        </div>
        <div className="h-display text-[26px] normal-case mb-2.5 leading-tight mt-4">Create your account</div>
        <div className="text-xs text-textDim mb-7 leading-relaxed">Frontend demo — creates a mock developer session, no backend involved.</div>
        <form onSubmit={handleSubmit}>
          <div className="field-label">Full name</div>
          <input className="field-input" style={{ background: '#fff', color: '#000' }} value={name} onChange={(e) => setName(e.target.value)} placeholder="Your name" />
          <div className="field-label">Email</div>
          <input className="field-input" type="email" style={{ background: '#fff', color: '#000' }} value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@company.com" />
          <button type="submit" className="w-full bg-white text-black border-2 border-white font-bold tracking-widest text-[13px] py-4 flex items-center justify-center gap-2.5 transition-transform hover:-translate-y-0.5 hover:bg-green hover:border-green active:translate-y-0 active:scale-[0.99]">
            CREATE ACCOUNT <ArrowRight size={15} />
          </button>
        </form>
        <div className="text-[11px] text-textDim mt-5 text-center">
          Already have an account? <Link to="/login" className="text-green">Sign in</Link>
        </div>
      </div>
    </motion.div>
  );
}

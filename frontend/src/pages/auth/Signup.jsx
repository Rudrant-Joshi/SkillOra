import { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from '../../lib/api';
import { useAuth } from '../../context/AuthContext';
import { springs } from '../../lib/motionConfig';

export default function Signup() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [status, setStatus] = useState('');
  const { login, loading } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password || !name) {
      setStatus('Fill in all fields.');
      return;
    }
    setStatus('Creating account…');
    try {
      await api.signup({ email, password, full_name: name, role: 'candidate' });
      // Auto-login after signup
      const dest = await login({ email, password, role: 'developer' });
      navigate(dest, { replace: true });
    } catch (err) {
      setStatus(err.message || 'Signup failed');
    }
  };

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} className="w-[420px] max-w-full offset-panel">
      <div className="inner px-8 sm:px-10 pt-11 pb-9">
        <div className="h-display text-[34px] tracking-tight mb-1">
          SKILL<span className="text-green">GRAPH</span>
        </div>
        <div className="h-display text-[26px] normal-case mb-2.5 leading-tight mt-4">Create your account</div>
        <div className="text-xs text-textDim mb-7 leading-relaxed">
          Connecting to the real SkillGraph backend for authenticated assessment access.
        </div>
        <form onSubmit={handleSubmit}>
          <div className="field-label">Full name</div>
          <input
            className="field-input"
            style={{ background: '#fff', color: '#000' }}
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Your name"
            required
          />
          <div className="field-label">Email</div>
          <input
            className="field-input"
            type="email"
            style={{ background: '#fff', color: '#000' }}
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@company.com"
            required
          />
          <div className="field-label">Password</div>
          <input
            className="field-input"
            type="password"
            style={{ background: '#fff', color: '#000' }}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            required
            minLength={6}
          />
          <motion.button
            type="submit"
            disabled={loading}
            className="w-full bg-white text-black border-2 border-white font-bold tracking-widest text-[13px] py-4 flex items-center justify-center gap-2.5 transition-transform hover:-translate-y-0.5 hover:bg-green hover:border-green active:translate-y-0 active:scale-[0.99]"
            whileHover={{ y: -2, backgroundColor: '#39FF14', borderColor: '#39FF14' }}
            whileTap={{ scale: 0.98 }}
            transition={springs.snappy}
          >
            {loading ? 'CREATING…' : 'CREATE ACCOUNT'} <ArrowRight size={15} />
          </motion.button>
        </form>
        {status && (
          <motion.div className="text-[11px] text-green mt-4" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.3 }}>
            {status}
          </motion.div>
        )}
        <div className="text-[11px] text-textDim mt-5 text-center">
          Already have an account? <Link to="/login" className="text-green">Sign in</Link>
        </div>
      </div>
    </motion.div>
  );
}

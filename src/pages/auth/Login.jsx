import { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import Magnetic from '../../components/motion/Magnetic';
import { springs, ease } from '../../lib/motionConfig';

const ROLES = [
  { id: 'developer', label: 'Developer' },
  { id: 'recruiter', label: 'Recruiter' },
  { id: 'company', label: 'Company Admin' },
];

export default function Login() {
  const [email, setEmail] = useState('rudrant@demo.dev');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('developer');
  const [status, setStatus] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!email.trim()) {
      setStatus('Enter an email to continue.');
      return;
    }
    setStatus('Validating demo credentials…');
    setTimeout(() => {
      const dest = login({ email, role });
      navigate(dest, { replace: true });
    }, 350);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.97, filter: 'blur(8px)' }}
      animate={{ opacity: 1, y: 0, scale: 1, filter: 'blur(0px)' }}
      transition={{ ...springs.smooth, opacity: { duration: 0.5 }, filter: { duration: 0.5 } }}
      className="w-[420px] max-w-full offset-panel"
    >
      <div className="inner px-8 sm:px-10 pt-11 pb-9">
        <motion.div
          className="h-display text-[34px] tracking-tight mb-1"
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.15, duration: 0.4, ease: ease.out }}
        >
          SKILL<span className="text-green" style={{ textShadow: '0 0 24px rgba(57,255,20,0.3)' }}>GRAPH</span>
        </motion.div>
        <motion.div
          className="text-[11px] tracking-[2px] text-green mb-6 uppercase"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.25, duration: 0.4 }}
        >
          Evidence over claims
        </motion.div>
        <motion.div
          className="h-display text-[26px] normal-case mb-2.5 leading-tight"
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.4, ease: ease.out }}
        >
          Sign in to your account
        </motion.div>
        <motion.div
          className="text-xs text-textDim mb-7 leading-relaxed"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4, duration: 0.4 }}
        >
          Frontend demo — no backend is connected. Any email/password combination signs you into a mock session.
        </motion.div>

        <form onSubmit={handleSubmit}>
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.45, duration: 0.35 }}
          >
            <div className="field-label">Email</div>
            <input
              className="field-input"
              type="email"
              placeholder="you@company.com"
              style={{ background: '#fff', color: '#000' }}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.35 }}
          >
            <div className="field-label">Password</div>
            <input
              className="field-input"
              type="password"
              placeholder="••••••••"
              style={{ background: '#fff', color: '#000' }}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.55, duration: 0.35 }}
          >
            <div className="field-label">Sign in as</div>
            <div className="flex gap-2 mb-1 relative">
              {ROLES.map((r) => (
                <button
                  type="button"
                  key={r.id}
                  onClick={() => setRole(r.id)}
                  className={`relative flex-1 text-center justify-center btn-small ${role === r.id ? 'active' : ''}`}
                >
                  {role === r.id && (
                    <motion.div
                      layoutId="role-indicator"
                      className="absolute inset-0 border border-white/60 bg-white/5"
                      transition={springs.snappy}
                    />
                  )}
                  <span className="relative z-10">{r.label}</span>
                </button>
              ))}
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6, duration: 0.35 }}
          >
            <Magnetic strength={0.15}>
              <motion.button
                type="submit"
                className="btn-solid mt-5 w-full bg-white text-black border-2 border-white font-bold tracking-widest text-[13px] py-4 flex items-center justify-center gap-2.5 relative overflow-hidden"
                whileHover={{ y: -2, backgroundColor: '#39FF14', borderColor: '#39FF14' }}
                whileTap={{ scale: 0.98, y: 0 }}
                transition={springs.snappy}
              >
                <span className="relative z-10 flex items-center gap-2.5">
                  SIGN IN <ArrowRight size={15} />
                </span>
                {/* Shimmer effect */}
                <motion.div
                  className="absolute inset-0 pointer-events-none"
                  style={{
                    background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent)',
                    transform: 'translateX(-100%)',
                  }}
                  animate={{ transform: ['translateX(-100%)', 'translateX(100%)'] }}
                  transition={{ duration: 2.5, repeat: Infinity, repeatDelay: 3, ease: 'linear' }}
                />
              </motion.button>
            </Magnetic>
            <Link to="/signup" className="btn-ghost block text-center border-2 border-borderDim text-white py-3.5 text-xs tracking-wide mt-3 hover:border-white transition-colors">
              CREATE AN ACCOUNT
            </Link>
          </motion.div>
        </form>

        {status && (
          <motion.div
            className="text-[11px] text-green mt-4"
            initial={{ opacity: 0, filter: 'blur(4px)' }}
            animate={{ opacity: 1, filter: 'blur(0px)' }}
            transition={{ duration: 0.3 }}
          >
            {status}
          </motion.div>
        )}
        <motion.div
          className="text-[11px] text-textDim mt-5 text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.7 }}
        >
          Frontend-only demo session · stored in localStorage
        </motion.div>
      </div>
    </motion.div>
  );
}

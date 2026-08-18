import { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

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
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="w-[420px] max-w-full offset-panel"
    >
      <div className="inner px-8 sm:px-10 pt-11 pb-9">
        <div className="h-display text-[34px] tracking-tight mb-1">
          SKILL<span className="text-green">GRAPH</span>
        </div>
        <div className="text-[11px] tracking-[2px] text-green mb-6 uppercase">Evidence over claims</div>
        <div className="h-display text-[26px] normal-case mb-2.5 leading-tight">Sign in to your account</div>
        <div className="text-xs text-textDim mb-7 leading-relaxed">
          Frontend demo — no backend is connected. Any email/password combination signs you into a mock session.
        </div>

        <form onSubmit={handleSubmit}>
          <div className="field-label">Email</div>
          <input
            className="field-input"
            type="email"
            placeholder="you@company.com"
            style={{ background: '#fff', color: '#000' }}
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <div className="field-label">Password</div>
          <input
            className="field-input"
            type="password"
            placeholder="••••••••"
            style={{ background: '#fff', color: '#000' }}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <div className="field-label">Sign in as</div>
          <div className="flex gap-2 mb-1">
            {ROLES.map((r) => (
              <button
                type="button"
                key={r.id}
                onClick={() => setRole(r.id)}
                className={`flex-1 text-center justify-center btn-small ${role === r.id ? 'active' : ''}`}
              >
                {r.label}
              </button>
            ))}
          </div>

          <button type="submit" className="btn-solid mt-5 w-full bg-white text-black border-2 border-white font-bold tracking-widest text-[13px] py-4 flex items-center justify-center gap-2.5 transition-transform hover:-translate-y-0.5 hover:bg-green hover:border-green active:translate-y-0 active:scale-[0.99]">
            SIGN IN <ArrowRight size={15} />
          </button>
          <Link to="/signup" className="btn-ghost block text-center border-2 border-borderDim text-white py-3.5 text-xs tracking-wide mt-3 hover:border-white transition-colors">
            CREATE AN ACCOUNT
          </Link>
        </form>

        {status && <div className="text-[11px] text-green mt-4">{status}</div>}
        <div className="text-[11px] text-textDim mt-5 text-center">Frontend-only demo session · stored in localStorage</div>
      </div>
    </motion.div>
  );
}

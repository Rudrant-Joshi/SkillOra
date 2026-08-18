import { Outlet } from 'react-router-dom';

export default function AuthLayout() {
  return (
    <div
      className="min-h-screen flex items-center justify-center px-5 py-10"
      style={{
        background:
          'linear-gradient(var(--border-dim) 1px, transparent 1px) 0 0/48px 48px, linear-gradient(90deg, var(--border-dim) 1px, transparent 1px) 0 0/48px 48px, #000',
      }}
    >
      <Outlet />
    </div>
  );
}

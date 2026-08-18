import { useState } from 'react';
import { PageHeader } from '../../components/ui/Primitives';
import { StaggerContainer, StaggerItem } from '../../components/animations/Reveal';
import { useDemoState } from '../../context/DemoStateContext';

export default function Network() {
  const { network, toggleFollow } = useDemoState();
  const [search, setSearch] = useState('');

  const filtered = network.filter(
    (n) => n.name.toLowerCase().includes(search.toLowerCase()) || n.role.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div>
      <PageHeader
        title="Network"
        subtitle="Connect with other verified developers."
        actions={<input className="field-input w-[240px] m-0" placeholder="Search developers…" value={search} onChange={(e) => setSearch(e.target.value)} />}
      />
      <StaggerContainer className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        {filtered.map((n) => (
          <StaggerItem key={n.name}>
            <div className="card">
              <div className="h-display text-sm">{n.name}</div>
              <div className="dim text-[11px] mt-1 text-textDim">{n.role}</div>
              <div className="flex gap-1.5 flex-wrap mt-2.5">
                {n.skills.map((s) => (
                  <span key={s} className="tech-pill">{s}</span>
                ))}
              </div>
              <div className="flex justify-between items-center mt-3.5">
                <span className="badge strong">{n.conf}% CONF</span>
                <span className="text-textDim text-[10px]">{n.verified} verified</span>
              </div>
              <button
                className={`btn-small w-full justify-center mt-3.5 ${n.following ? 'active' : ''}`}
                onClick={() => toggleFollow(n.name)}
              >
                {n.following ? 'FOLLOWING' : 'FOLLOW'}
              </button>
            </div>
          </StaggerItem>
        ))}
      </StaggerContainer>
    </div>
  );
}

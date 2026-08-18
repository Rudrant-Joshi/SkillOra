import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { PageHeader } from '../../components/ui/Primitives';
import { Reveal } from '../../components/animations/Reveal';
import { skills } from '../../data/skills';
import { ease } from '../../lib/motion';

const CATS = ['all', 'lang', 'fw', 'tool', 'db', 'concept'];
const CAT_LABEL = { all: 'ALL', lang: 'LANGUAGES', fw: 'FRAMEWORKS', tool: 'TOOLS', db: 'DATABASES', concept: 'CONCEPTS' };

function layout(list) {
  const cx = 400, cy = 260, r = 190;
  return list.map((s, i) => {
    const angle = (i / list.length) * Math.PI * 2 - Math.PI / 2;
    return { ...s, x: cx + r * Math.cos(angle), y: cy + r * Math.sin(angle) };
  });
}

export default function SkillGraphView() {
  const [filter, setFilter] = useState('all');
  const [selected, setSelected] = useState(null);
  const [hovered, setHovered] = useState(null);
  const filtered = filter === 'all' ? skills : skills.filter((s) => s.cat === filter);
  const nodes = layout(filtered);
  const cx = 400, cy = 260;
  const emphasized = hovered || (selected && selected.name);

  return (
    <div>
      <PageHeader
        title="SkillGraph"
        subtitle="Your evidence network — every skill traced to real project work."
        actions={CATS.map((c) => (
          <motion.button
            key={c}
            className={`btn-small ${filter === c ? 'active' : ''}`}
            onClick={() => {
              setFilter(c);
              setSelected(null);
            }}
            whileTap={{ scale: 0.96 }}
          >
            {CAT_LABEL[c]}
          </motion.button>
        ))}
      />
      <Reveal variant="scale" className="card-flat p-0 overflow-hidden">
        <svg viewBox="0 0 800 520" className="w-full h-[420px] sm:h-[520px]">
          <motion.circle
            cx={cx}
            cy={cy}
            r="34"
            fill="#111"
            stroke="#39FF14"
            strokeWidth="2"
            initial={{ scale: 0.7, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.4, ease: ease.out }}
          />
          <text x={cx} y={cy + 4} textAnchor="middle" fill="#39FF14" fontSize="11" fontFamily="Space Mono, monospace">
            YOU
          </text>

          {/* Connections "draw" in from center to each node */}
          {nodes.map((n, i) => {
            const dimmed = emphasized && n.name !== emphasized;
            return (
              <motion.line
                key={`l-${n.name}`}
                x1={cx}
                y1={cy}
                x2={n.x}
                y2={n.y}
                stroke={emphasized === n.name ? '#39FF14' : '#242424'}
                strokeWidth={emphasized === n.name ? 2 : 1.5}
                initial={{ pathLength: 0, opacity: 0 }}
                animate={{ pathLength: 1, opacity: dimmed ? 0.25 : 1 }}
                transition={{ pathLength: { duration: 0.5, delay: i * 0.04, ease: ease.out }, opacity: { duration: 0.25 } }}
              />
            );
          })}

          {nodes.map((n, i) => {
            const isSelected = selected?.name === n.name;
            const dimmed = emphasized && n.name !== emphasized;
            return (
              <motion.g
                key={n.name}
                initial={{ opacity: 0, scale: 0.6 }}
                animate={{ opacity: dimmed ? 0.35 : 1, scale: isSelected ? 1.08 : 1 }}
                transition={{ opacity: { duration: 0.25 }, scale: { type: 'spring', stiffness: 400, damping: 24, delay: dimmed ? 0 : i * 0.05 } }}
                onClick={() => setSelected(n)}
                onMouseEnter={() => setHovered(n.name)}
                onMouseLeave={() => setHovered(null)}
                className="cursor-pointer"
                style={{ transformOrigin: `${n.x}px ${n.y}px` }}
              >
                <circle
                  cx={n.x}
                  cy={n.y}
                  r={18 + n.pct / 10}
                  fill={n.badge === 'gap' ? '#111' : '#0A0A0A'}
                  stroke={isSelected || emphasized === n.name ? '#39FF14' : n.badge === 'strong' ? '#39FF14' : n.badge === 'warn' ? '#8A8A8A' : '#4A4A4A'}
                  strokeWidth={isSelected ? 3 : 2}
                />
                <text x={n.x} y={n.y - (24 + n.pct / 10)} textAnchor="middle" fill="#fff" fontSize="11" fontFamily="Space Mono, monospace">
                  {n.name}
                </text>
                <text x={n.x} y={n.y + 4} textAnchor="middle" fill={n.badge === 'strong' ? '#39FF14' : '#8A8A8A'} fontSize="10" fontFamily="Space Mono, monospace">
                  {n.pct}%
                </text>
              </motion.g>
            );
          })}
        </svg>
      </Reveal>
      <div className="dim mono text-[11px] mt-3.5 text-textDim">CLICK A SKILL NODE TO VIEW EVIDENCE · HOVER FOR QUICK STATS</div>

      <AnimatePresence mode="wait">
        {selected && (
          <motion.div
            key={selected.name}
            initial={{ opacity: 0, y: 10, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -6, scale: 0.98 }}
            transition={{ duration: 0.25, ease: ease.out }}
            className="card-flat mt-4"
          >
            <div className="flex justify-between items-start">
              <div className="h-display text-lg">{selected.name}</div>
              <span className={`badge ${selected.badge}`}>{selected.status}</span>
            </div>
            <div className="text-textDim text-xs mt-2">{selected.projects} projects · {selected.evidence} evidence points</div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

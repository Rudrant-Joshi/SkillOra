import { useState, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { PageHeader } from '../../components/ui/Primitives';
import { skills } from '../../data/skills';
import { springs, ease, duration } from '../../lib/motionConfig';
import { isTouchDevice } from '../../lib/motionConfig';

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

  const isTouch = isTouchDevice();

  return (
    <div>
      <PageHeader
        title="SkillGraph"
        subtitle="Your evidence network — every skill traced to real project work."
        actions={CATS.map((c) => (
          <button
            key={c}
            className={`relative btn-small ${filter === c ? 'active' : ''}`}
            onClick={() => { setFilter(c); setSelected(null); setHovered(null); }}
          >
            {filter === c && (
              <motion.div
                layoutId="skillgraph-filter"
                className="absolute inset-0 border border-white/60 bg-white/5"
                transition={springs.snappy}
              />
            )}
            <span className="relative z-10">{CAT_LABEL[c]}</span>
          </button>
        ))}
      />
      <motion.div
        className="card-flat p-0 overflow-hidden"
        initial={{ opacity: 0, scale: 0.98 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, ease: ease.out }}
      >
        <svg viewBox="0 0 800 520" className="w-full h-[420px] sm:h-[520px]">
          {/* Grid lines for background depth */}
          <motion.g
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.15 }}
            transition={{ duration: 1, delay: 0.2 }}
          >
            <circle cx={cx} cy={cy} r="100" fill="none" stroke="#242424" strokeWidth="0.5" strokeDasharray="4 4" />
            <circle cx={cx} cy={cy} r="190" fill="none" stroke="#242424" strokeWidth="0.5" strokeDasharray="4 4" />
          </motion.g>

          {/* Core node with pulsing glow */}
          <motion.g
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.1, ...springs.bouncy }}
            style={{ transformOrigin: `${cx}px ${cy}px` }}
          >
            <motion.circle
              cx={cx} cy={cy} r="38"
              fill="#111"
              stroke="#39FF14"
              strokeWidth="2"
              animate={{
                filter: [
                  'drop-shadow(0 0 4px rgba(57,255,20,0.3))',
                  'drop-shadow(0 0 12px rgba(57,255,20,0.15))',
                  'drop-shadow(0 0 4px rgba(57,255,20,0.3))',
                ],
              }}
              transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
            />
            <text x={cx} y={cy + 4} textAnchor="middle" fill="#39FF14" fontSize="12" fontFamily="Space Mono, monospace" fontWeight="bold">
              YOU
            </text>
          </motion.g>

          {/* Edges — path drawing animation */}
          {nodes.map((n, i) => {
            const isConnectedToHovered = hovered && hovered.name === n.name;
            const isHoveredOther = hovered && hovered.name !== n.name;
            return (
              <motion.line
                key={`l-${n.name}`}
                x1={cx} y1={cy} x2={n.x} y2={n.y}
                strokeWidth="1.5"
                initial={{ pathLength: 0, opacity: 0 }}
                animate={{
                  pathLength: 1,
                  opacity: isConnectedToHovered ? 0.8 : isHoveredOther ? 0.1 : 0.3,
                  stroke: isConnectedToHovered ? '#39FF14' : '#242424',
                }}
                transition={{
                  pathLength: { delay: 0.2 + i * 0.06, duration: 0.5, ease: ease.out },
                  opacity: { duration: 0.3 },
                  stroke: { duration: 0.3 },
                }}
              />
            );
          })}

          {/* Skill nodes */}
          {nodes.map((n, i) => {
            const isSelected = selected?.name === n.name;
            const isHoveredNode = hovered?.name === n.name;
            const isOtherHovered = hovered && hovered.name !== n.name;
            const baseR = 18 + n.pct / 10;

            return (
              <motion.g
                key={n.name}
                initial={{ opacity: 0, scale: 0.3 }}
                animate={{
                  opacity: isOtherHovered ? 0.35 : 1,
                  scale: 1,
                }}
                transition={{
                  opacity: { duration: 0.3 },
                  scale: { delay: 0.3 + i * 0.06, ...springs.bouncy },
                }}
                onClick={() => setSelected(n)}
                onMouseEnter={!isTouch ? () => setHovered(n) : undefined}
                onMouseLeave={!isTouch ? () => setHovered(null) : undefined}
                className="cursor-pointer"
                style={{ transformOrigin: `${n.x}px ${n.y}px` }}
              >
                {/* Glow ring on hover/select */}
                {(isHoveredNode || isSelected) && (
                  <motion.circle
                    cx={n.x} cy={n.y}
                    r={baseR + 6}
                    fill="none"
                    stroke="#39FF14"
                    strokeWidth="1"
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 0.4, scale: 1 }}
                    transition={springs.snappy}
                    style={{ transformOrigin: `${n.x}px ${n.y}px` }}
                  />
                )}
                <motion.circle
                  cx={n.x} cy={n.y}
                  r={baseR}
                  fill={n.badge === 'gap' ? '#111' : '#0A0A0A'}
                  stroke={n.badge === 'strong' ? '#39FF14' : n.badge === 'warn' ? '#8A8A8A' : '#4A4A4A'}
                  strokeWidth={isSelected ? 2.5 : 2}
                  animate={{
                    r: isHoveredNode ? baseR + 3 : baseR,
                    filter: isHoveredNode
                      ? 'drop-shadow(0 0 8px rgba(57,255,20,0.3))'
                      : 'drop-shadow(0 0 0px transparent)',
                  }}
                  transition={springs.snappy}
                />
                <text
                  x={n.x} y={n.y - (24 + n.pct / 10)}
                  textAnchor="middle" fill="#fff" fontSize="11" fontFamily="Space Mono, monospace"
                >
                  {n.name}
                </text>
                <text
                  x={n.x} y={n.y + 4}
                  textAnchor="middle"
                  fill={n.badge === 'strong' ? '#39FF14' : '#8A8A8A'}
                  fontSize="10" fontFamily="Space Mono, monospace"
                >
                  {n.pct}%
                </text>
              </motion.g>
            );
          })}
        </svg>
      </motion.div>
      <motion.div
        className="dim mono text-[11px] mt-3.5 text-textDim"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
      >
        CLICK A SKILL NODE TO VIEW EVIDENCE · HOVER FOR QUICK STATS
      </motion.div>

      {/* Detail panel */}
      <AnimatePresence mode="wait">
        {selected && (
          <motion.div
            key={selected.name}
            initial={{ opacity: 0, y: 14, scale: 0.98, filter: 'blur(4px)' }}
            animate={{ opacity: 1, y: 0, scale: 1, filter: 'blur(0px)' }}
            exit={{ opacity: 0, y: -8, scale: 0.98, filter: 'blur(2px)' }}
            transition={springs.smooth}
            className="card-flat mt-4"
          >
            <div className="flex justify-between items-start">
              <div>
                <div className="h-display text-lg">{selected.name}</div>
                <div className="text-textDim text-xs mt-1">{selected.cat?.toUpperCase()}</div>
              </div>
              <motion.span
                className={`badge ${selected.badge}`}
                initial={{ scale: 0.8 }}
                animate={{ scale: 1 }}
                transition={springs.snappy}
              >
                {selected.status}
              </motion.span>
            </div>
            <motion.div
              className="text-textDim text-xs mt-2"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.15 }}
            >
              {selected.projects} projects · {selected.evidence} evidence points
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

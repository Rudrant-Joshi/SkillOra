import { Reveal } from '../../components/animations/Reveal';
import { ProgressBar } from '../../components/ui/AnimatedNumber';

const dimensions = [
  { name: 'Architecture', pct: 78 },
  { name: 'Code Quality', pct: 74 },
  { name: 'Testing', pct: 41 },
  { name: 'Documentation', pct: 58 },
  { name: 'Security', pct: 69 },
  { name: 'Performance', pct: 66 },
];

export default function Xray() {
  return (
    <div>
      <Reveal>
        <div className="flex justify-between items-start flex-wrap gap-4">
          <div>
            <div className="h-display text-2xl">E-Commerce API</div>
            <div className="mono dim text-[11px] mt-1.5 text-textDim">github.com/rudrant/ecommerce-api</div>
            <div className="flex gap-2 mt-3 flex-wrap">
              {['PYTHON', 'FASTAPI', 'POSTGRESQL', 'DOCKER'].map((t) => (
                <span key={t} className="tech-pill">{t}</span>
              ))}
            </div>
          </div>
          <div className="flex gap-2.5">
            <button className="btn-small">RE-ANALYZE</button>
            <button className="btn-small">VIEW REPOSITORY</button>
          </div>
        </div>
        <div className="divider" />
      </Reveal>

      <div className="grid grid-cols-1 lg:grid-cols-[1fr_1.4fr] gap-4 items-start">
        <Reveal delay={0.05}>
          <div className="offset-panel">
            <div className="inner p-7">
              <div className="eyebrow">Project Health</div>
              <div className="big-num text-[64px]">
                72<span className="dim text-[22px] text-textDim">/100</span>
              </div>
              <div className="badge strong mt-2.5">◆ GOOD</div>
              <div className="mono dim text-[11px] mt-4 cursor-pointer hover:text-white transition-colors text-textDim">WHY THIS SCORE? →</div>
            </div>
          </div>
        </Reveal>
        <Reveal delay={0.1}>
          <div className="card-flat">
            <div className="eyebrow">Health Dimensions</div>
            <div className="flex flex-col gap-3 mt-3">
              {dimensions.map((d) => (
                <div key={d.name}>
                  <div className="flex justify-between text-[11px] mb-1.5">
                    <span>{d.name}</span>
                    <span className="text-textDim">{d.pct}%</span>
                  </div>
                  <ProgressBar pct={d.pct} tone={d.pct < 50 ? 'amber' : ''} />
                </div>
              ))}
            </div>
          </div>
        </Reveal>
      </div>

      <div className="divider" />
      <Reveal>
        <div className="text-xs tracking-widest uppercase text-textDim mb-4">Architecture</div>
        <div className="card-flat flex flex-col items-center gap-0 py-9">
          {['CLIENT', 'API GATEWAY — FASTAPI', 'SERVICES', 'POSTGRESQL'].map((node, i) => (
            <div key={node} className="flex flex-col items-center">
              <div className={`px-5 py-2.5 border text-xs tracking-wide ${i === 1 ? 'border-green text-green' : 'border-borderDim'}`}>{node}</div>
              {i < 3 && <div className="w-px h-6 bg-borderDim" />}
            </div>
          ))}
        </div>
      </Reveal>

      <div className="divider" />
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Reveal>
          <div className="card-flat">
            <div className="eyebrow text-green">Strengths</div>
            <div className="mono text-xs leading-loose">
              <div>✓ Clean API structure</div>
              <div>✓ Good separation of concerns</div>
              <div>✓ Consistent error handling</div>
            </div>
          </div>
        </Reveal>
        <Reveal delay={0.05}>
          <div className="card-flat">
            <div className="eyebrow">Warnings</div>
            <div className="mono text-xs leading-loose">
              <div>⚠ Limited automated testing</div>
              <div>⚠ Documentation incomplete</div>
              <div>⚠ No caching layer</div>
            </div>
          </div>
        </Reveal>
      </div>
    </div>
  );
}

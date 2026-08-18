import { useState } from 'react';
import { motion } from 'framer-motion';
import { Reveal, StaggerContainer, StaggerItem, SequencedGroup, SequencedItem, LaserDivider } from '../../components/animations/Reveal';
import { TiltCard } from '../../components/animations/TiltCard';
import { PointerGlow } from '../../components/animations/PointerGlow';
import { Button } from '../../components/ui/Primitives';
import { AnimatedNumber, ProgressBar } from '../../components/ui/AnimatedNumber';
import { skills, badgesForPassport } from '../../data/skills';
import VerifyModal from '../../components/modals/VerifyModal';

const SKILL_COLOR_MAP = {
  strong: {
    text: 'text-green',
    badge: 'strong',
    tone: '',
    status: 'STRONG EVIDENCE',
    dot: 'bg-green shadow-[0_0_8px_#39ff14]',
  },
  warn: {
    text: 'text-amber-400',
    badge: 'warn',
    tone: 'amber',
    status: 'DEVELOPING',
    dot: 'bg-amber-400 shadow-[0_0_8px_#ffb800]',
  },
  gap: {
    text: 'text-red-400',
    badge: 'gap',
    tone: 'red',
    status: 'NEEDS IMPROVEMENT',
    dot: 'bg-red-400 shadow-[0_0_8px_#ff4d4f]',
  },
};

export default function Passport() {
  const [verifyOpen, setVerifyOpen] = useState(false);

  return (
    <div>
      <SequencedGroup gap={0.07}>
        <SequencedItem>
          <div className="h-display text-2xl">Digital Skill Passport</div>
        </SequencedItem>
        <SequencedItem distance={6}>
          <div className="dim text-xs mt-1.5 text-textDim">Your cryptographically verifiable evidence-backed developer profile.</div>
        </SequencedItem>
        <LaserDivider />
      </SequencedGroup>

      <Reveal delay={0.05} variant="scale">
        <TiltCard maxTilt={1} className="relative rounded-sm border border-borderDim bg-[#0a0a0a] shadow-[0_24px_60px_-15px_rgba(0,0,0,0.9),0_0_30px_-8px_rgba(57,255,20,0.06)] overflow-hidden">
          <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-green/60 to-transparent" />
          <PointerGlow>
            <div className="p-8 sm:p-10 relative z-10 bg-black/40">
              <div className="flex justify-between items-start flex-wrap gap-5">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-green animate-pulse shadow-[0_0_8px_#39ff14]" />
                    <span className="mono text-[10px] tracking-[3px] text-green font-bold uppercase">VERIFIED DEVELOPER PASSPORT</span>
                  </div>
                  <div className="h-display text-3xl sm:text-4xl mt-2 tracking-tight text-white">RUDRANT JOSHI</div>
                  <div className="mono text-xs mt-1 text-textDim font-medium tracking-wide">BACKEND & DISTRIBUTED SYSTEMS DEVELOPER</div>
                </div>
                <div className="text-right">
                  <div className="eyebrow text-textDim">Skill Confidence</div>
                  <div className="h-display text-green text-4xl sm:text-5xl drop-shadow-[0_0_12px_rgba(57,255,20,0.35)]">
                    <AnimatedNumber value={82} suffix="%" />
                  </div>
                  <span className="badge strong mt-2">◆ TIER 1 VERIFIED</span>
                </div>
              </div>

              <LaserDivider />
              <div className="flex justify-between items-center flex-wrap gap-2">
                <div className="eyebrow text-white/90">Skill Confidence Breakdown</div>
                <div className="flex items-center gap-3 text-[10px] font-mono">
                  <span className="flex items-center gap-1 text-green"><span className="w-1.5 h-1.5 rounded-full bg-green" /> Strong (&gt;75%)</span>
                  <span className="flex items-center gap-1 text-amber-400"><span className="w-1.5 h-1.5 rounded-full bg-amber-400" /> Developing</span>
                  <span className="flex items-center gap-1 text-red-400"><span className="w-1.5 h-1.5 rounded-full bg-red-400" /> Needs Improvement</span>
                </div>
              </div>
              <div className="dim mono text-[10px] mt-1 text-textDim">
                PROJECT EVIDENCE · ASSESSMENT VERIFIED · COMMITS ANALYZED — SHOWN SEPARATELY, NEVER MERGED SILENTLY
              </div>

              <StaggerContainer className="flex flex-col gap-3.5 mt-4" stagger={0.05}>
                {skills.slice(0, 6).map((s) => {
                  const conf = SKILL_COLOR_MAP[s.badge] || SKILL_COLOR_MAP.strong;
                  return (
                    <StaggerItem key={s.name}>
                      <div className="p-3 bg-surface2/60 border border-borderDim hover:border-white/30 transition-all rounded-sm">
                        <div className="flex justify-between items-center text-xs mb-2 font-mono">
                          <div className="flex items-center gap-2">
                            <span className={`w-1.5 h-1.5 rounded-full ${conf.dot}`} />
                            <span className="font-bold text-white tracking-wide">{s.name}</span>
                            <span className="text-[9px] uppercase px-1.5 py-0.5 border border-borderDim text-textDim tracking-wider">{s.cat}</span>
                          </div>
                          <div className="flex items-center gap-3">
                            <span className={`text-[10px] font-semibold tracking-wider ${conf.text}`}>
                              {conf.status}
                            </span>
                            <span className={`font-bold ${conf.text} min-w-[36px] text-right`}>{s.pct}%</span>
                          </div>
                        </div>
                        <ProgressBar pct={s.pct} tone={conf.tone} />
                      </div>
                    </StaggerItem>
                  );
                })}
              </StaggerContainer>

              <LaserDivider />
              <div className="eyebrow text-white/90">Verified Improvements</div>
              <StaggerContainer className="flex flex-wrap gap-2.5 mt-2" stagger={0.06}>
                {['Testing (+39%)', 'Docker (+55%)', 'API Security (+23%)', 'CI/CD Pipeline (+40%)'].map((item) => (
                  <StaggerItem key={item} direction="left" distance={10}>
                    <div className="inline-flex items-center gap-2 px-3.5 py-2 bg-surface2 border border-borderDim hover:border-green/40 text-white font-mono text-xs tracking-wide transition-colors">
                      <span className="text-green font-bold">✓</span> {item}
                    </div>
                  </StaggerItem>
                ))}
              </StaggerContainer>

              <LaserDivider />
              <div className="eyebrow text-white/90">Verified Assessment Badges</div>
              <StaggerContainer className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-3" stagger={0.05}>
                {badgesForPassport.map((b) => (
                  <StaggerItem key={b} scale={0.9} direction="none">
                    <motion.div
                      className="card text-center relative overflow-hidden group"
                      whileHover={{ y: -5, borderColor: 'var(--green)' }}
                      transition={{ duration: 0.18 }}
                    >
                      <div className="absolute top-0 right-0 left-0 h-[2px] bg-gradient-to-r from-transparent via-green/50 to-transparent" />
                      <motion.div
                        className="w-10 h-10 mx-auto rounded-full bg-surface2 border border-green/40 flex items-center justify-center text-green text-lg font-bold shadow-[0_0_12px_rgba(57,255,20,0.15)]"
                        initial={{ scale: 0, opacity: 0 }}
                        whileInView={{ scale: 1, opacity: 1 }}
                        viewport={{ once: true }}
                        transition={{ type: 'spring', stiffness: 400, damping: 20, delay: 0.15 }}
                      >
                        ✓
                      </motion.div>
                      <div className="h-display text-sm mt-3 text-white">{b}</div>
                      <div className="text-textDim font-mono text-[10px] mt-1 tracking-wider uppercase">Verified by System</div>
                    </motion.div>
                  </StaggerItem>
                ))}
              </StaggerContainer>

              <LaserDivider />
              <StaggerContainer className="flex gap-3 flex-wrap items-center" stagger={0.05}>
                <StaggerItem>
                  <Button tone="primary" magnetic>SHARE PASSPORT</Button>
                </StaggerItem>
                <StaggerItem>
                  <Button tone="secondary">COPY LINK</Button>
                </StaggerItem>
                <StaggerItem>
                  <Button tone="secondary" onClick={() => setVerifyOpen(true)}>
                    PREVIEW PUBLIC VERIFICATION →
                  </Button>
                </StaggerItem>
                <StaggerItem>
                  <Button tone="secondary">DOWNLOAD</Button>
                </StaggerItem>
              </StaggerContainer>
            </div>
          </PointerGlow>
        </TiltCard>
      </Reveal>

      <VerifyModal open={verifyOpen} onClose={() => setVerifyOpen(false)} />
    </div>
  );
}

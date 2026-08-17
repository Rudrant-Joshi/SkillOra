import { Link } from 'react-router-dom';
import { useState } from 'react';
import { motion } from 'framer-motion';
import { Reveal, StaggerContainer, StaggerItem } from '../../components/animations/Reveal';
import { AnimatedNumber, ProgressBar } from '../../components/ui/AnimatedNumber';
import Spotlight from '../../components/motion/Spotlight';
import Magnetic from '../../components/motion/Magnetic';
import TiltCard from '../../components/motion/TiltCard';
import { skills, badgesForPassport } from '../../data/skills';
import { springs, ease } from '../../lib/motionConfig';
import VerifyModal from '../../components/modals/VerifyModal';

export default function Passport() {
  const [verifyOpen, setVerifyOpen] = useState(false);

  return (
    <div>
      <Reveal>
        <div className="h-display text-2xl">Digital Skill Passport</div>
        <div className="dim text-xs mt-1.5 text-textDim">Your verified developer profile.</div>
        <div className="divider" />
      </Reveal>

      <Reveal delay={0.05}>
        <TiltCard tiltMax={3} perspective={1000}>
          <div className="offset-panel">
            <Spotlight color="rgba(57,255,20,0.06)" size={400}>
              <div className="inner p-8 sm:p-10">
                <motion.div
                  className="flex justify-between items-start flex-wrap gap-5"
                  initial={{ opacity: 0, y: 12 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.4, ease: ease.out }}
                >
                  <div>
                    <div className="mono dim text-[10px] tracking-[3px] text-textDim">VERIFIED DEVELOPER PASSPORT</div>
                    <div className="h-display text-3xl mt-1.5">RUDRANT JOSHI</div>
                    <div className="mono dim text-xs mt-1 text-textDim">BACKEND DEVELOPER</div>
                  </div>
                  <div className="text-right">
                    <div className="eyebrow">Skill Confidence</div>
                    <div className="h-display text-green text-4xl">
                      <AnimatedNumber value={82} suffix="%" />
                    </div>
                  </div>
                </motion.div>

                <div className="divider" />
                <Reveal delay={0.1}>
                  <div className="eyebrow">Skill Confidence Breakdown</div>
                  <div className="dim mono text-[10px] mt-1 text-textDim">PROJECT EVIDENCE · ASSESSMENT VERIFIED · SELF-REPORTED — SHOWN SEPARATELY, NEVER MERGED SILENTLY</div>
                </Reveal>
                <div className="flex flex-col gap-2.5 mt-3.5">
                  {skills.slice(0, 6).map((s, i) => (
                    <Reveal key={s.name} delay={0.12 + i * 0.05}>
                      <div>
                        <div className="flex justify-between text-[11px] mb-1">
                          <span>{s.name}</span>
                          <span className="text-textDim">{s.pct}%</span>
                        </div>
                        <ProgressBar pct={s.pct} tone={s.badge === 'gap' ? 'red' : s.badge === 'warn' ? 'amber' : ''} />
                      </div>
                    </Reveal>
                  ))}
                </div>

                <div className="divider" />
                <Reveal delay={0.15}>
                  <div className="eyebrow">Verified Improvements</div>
                  <div className="mono text-xs leading-loose mt-1.5">
                    {['Testing', 'Docker', 'API Security'].map((item, i) => (
                      <motion.div
                        key={item}
                        className="text-green"
                        initial={{ opacity: 0, x: -8 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.2 + i * 0.1, duration: 0.3, ease: ease.out }}
                      >
                        ✓ {item}
                      </motion.div>
                    ))}
                  </div>
                </Reveal>

                <div className="divider" />
                <Reveal delay={0.2}>
                  <div className="eyebrow">Verified Assessment Badges</div>
                </Reveal>
                <StaggerContainer className="grid grid-cols-2 sm:grid-cols-3 gap-4 mt-3" stagger={0.08}>
                  {badgesForPassport.map((b) => (
                    <StaggerItem key={b}>
                      <motion.div
                        className="card text-center"
                        whileHover={{ y: -3 }}
                        transition={springs.snappy}
                      >
                        <motion.div
                          className="text-green text-lg"
                          initial={{ scale: 0 }}
                          whileInView={{ scale: 1 }}
                          viewport={{ once: true }}
                          transition={{ ...springs.bouncy, delay: 0.3 }}
                        >
                          ✓
                        </motion.div>
                        <div className="h-display text-xs mt-2">{b}</div>
                      </motion.div>
                    </StaggerItem>
                  ))}
                </StaggerContainer>

                <div className="divider" />
                <motion.div
                  className="flex gap-3 flex-wrap"
                  initial={{ opacity: 0, y: 10 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.3, duration: 0.4 }}
                >
                  <Magnetic strength={0.2}>
                    <button className="btn-primary">SHARE PASSPORT</button>
                  </Magnetic>
                  <button className="btn-secondary">COPY LINK</button>
                  <button className="btn-secondary" onClick={() => setVerifyOpen(true)}>
                    PREVIEW PUBLIC VERIFICATION →
                  </button>
                  <button className="btn-secondary">DOWNLOAD</button>
                </motion.div>
              </div>
            </Spotlight>
          </div>
        </TiltCard>
      </Reveal>

      <VerifyModal open={verifyOpen} onClose={() => setVerifyOpen(false)} />
    </div>
  );
}

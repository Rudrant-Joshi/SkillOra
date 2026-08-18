import { motion } from 'framer-motion';
import { AnimatedNumber } from './AnimatedNumber';
import { Reveal, SequencedGroup, SequencedItem } from '../animations/Reveal';
import { PointerGlow } from '../animations/PointerGlow';
import { TiltCard } from '../animations/TiltCard';
import { Magnetic } from '../animations/Magnetic';
import { ease, press, cardHover, cardHoverFeatured } from '../../lib/motion';
import { useReducedMotion } from '../../hooks/useReducedMotion';

/**
 * Card — the base interactive surface used throughout the app.
 * `featured` opts a card into the premium pointer-glow + 3D tilt treatment;
 * reserve that for hero/flagship surfaces, not every card.
 *
 * Hover is intentionally heavy: a real lift, a scale bump, and a glowing
 * shadow, driven by spring physics so it feels tactile rather than a fade.
 * Clicking a card fires a quick vibration so the click is unmistakable.
 */
export function Card({ children, className = '', hover = true, featured = false, glow = false, onClick, ...rest }) {
  const reduced = useReducedMotion();
  const content = (
    <motion.div
      className={`card ${featured ? 'card-featured' : ''} ${className}`}
      whileHover={hover && !reduced ? (featured ? cardHoverFeatured : cardHover) : undefined}
      whileTap={!reduced ? { scale: 0.97 } : undefined}
      onClick={onClick}
      transition={{ duration: 0.18, ease: ease.out }}
      style={{ willChange: hover ? 'transform' : undefined }}
      {...rest}
    >
      {children}
    </motion.div>
  );

  if (featured && !reduced) {
    return (
      <TiltCard maxTilt={2.5}>
        <PointerGlow>{content}</PointerGlow>
      </TiltCard>
    );
  }
  if (glow && !reduced) {
    return <PointerGlow>{content}</PointerGlow>;
  }
  return content;
}

/** Motion-aware button — heavy press/hover feedback + optional magnetic pull for primary CTAs. */
export function Button({ children, tone = 'primary', magnetic = false, className = '', as: Comp = 'button', ...rest }) {
  const toneClass = tone === 'primary' ? 'btn-primary' : tone === 'secondary' ? 'btn-secondary' : 'btn-small';
  const el = (
    <motion.div
      whileHover={{ scale: 1.05, y: -3 }}
      whileTap={{ scale: 0.92 }}
      transition={{ type: 'spring', stiffness: 420, damping: 22 }}
      className="inline-block"
    >
      <Comp className={`${toneClass} ${className}`} {...rest}>
        {children}
      </Comp>
    </motion.div>
  );
  return magnetic ? <Magnetic className="inline-block">{el}</Magnetic> : el;
}

export function StatCard({ label, value, suffix = '', tone = '', delay = 0 }) {
  return (
    <Reveal delay={delay} variant="scale">
      <Card>
        <div className="eyebrow">{label}</div>
        <div className={`big-num text-3xl ${tone}`}>
          <AnimatedNumber value={value} suffix={suffix} />
        </div>
      </Card>
    </Reveal>
  );
}

export function Badge({ children, tone = '' }) {
  return (
    <motion.span initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.2 }} className={`badge ${tone}`}>
      {children}
    </motion.span>
  );
}

/** Page header — label / title / subtitle / actions assemble in sequence. */
export function PageHeader({ title, subtitle, actions }) {
  return (
    <SequencedGroup gap={0.07}>
      <div className="flex justify-between items-start flex-wrap gap-4">
        <div>
          <SequencedItem direction="up" distance={8}>
            <div className="h-display text-2xl md:text-[26px]">{title}</div>
          </SequencedItem>
          {subtitle && (
            <SequencedItem direction="up" distance={6}>
              <div className="dim text-xs mt-1.5 text-textDim">{subtitle}</div>
            </SequencedItem>
          )}
        </div>
        {actions && (
          <SequencedItem direction="up" distance={4}>
            <div className="flex gap-2.5 flex-wrap">{actions}</div>
          </SequencedItem>
        )}
      </div>
      <div className="divider" />
    </SequencedGroup>
  );
}

export function EmptyState({ children }) {
  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.3 }} className="card-flat text-center py-8">
      <div className="dim mono text-xs text-textDim">{children}</div>
    </motion.div>
  );
}

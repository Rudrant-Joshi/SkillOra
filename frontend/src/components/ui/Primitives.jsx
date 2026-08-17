import { motion } from 'framer-motion';
import { AnimatedNumber } from './AnimatedNumber';
import { Reveal } from '../animations/Reveal';
import TiltCard from '../motion/TiltCard';
import AnimatedText from '../motion/AnimatedText';
import { springs } from '../../lib/motionConfig';

export function Card({ children, className = '', hover = true, tilt = true, ...rest }) {
  const cardContent = (
    <motion.div
      className={`card ${className}`}
      whileTap={hover ? { scale: 0.985 } : undefined}
      transition={springs.snappy}
      {...rest}
    >
      {children}
    </motion.div>
  );

  if (tilt && hover) {
    return (
      <TiltCard tiltMax={3.5}>
        {cardContent}
      </TiltCard>
    );
  }

  return cardContent;
}

export function StatCard({ label, value, suffix = '', tone = '', delay = 0 }) {
  return (
    <Reveal delay={delay} mode="scale">
      <TiltCard tiltMax={4}>
        <motion.div
          className="card"
          whileTap={{ scale: 0.985 }}
          transition={springs.snappy}
        >
          <div className="eyebrow">{label}</div>
          <div className={`big-num text-3xl ${tone}`}>
            <AnimatedNumber value={value} suffix={suffix} />
          </div>
        </motion.div>
      </TiltCard>
    </Reveal>
  );
}

export function Badge({ children, tone = '' }) {
  return <span className={`badge ${tone}`}>{children}</span>;
}

export function PageHeader({ title, subtitle, actions }) {
  return (
    <Reveal>
      <div className="flex justify-between items-start flex-wrap gap-4">
        <div>
          <AnimatedText
            text={title}
            mode="words"
            className="h-display text-2xl md:text-[26px]"
            stagger={0.05}
          />
          {subtitle && (
            <motion.div
              className="dim text-xs mt-1.5 text-textDim"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3, duration: 0.4 }}
            >
              {subtitle}
            </motion.div>
          )}
        </div>
        {actions && (
          <motion.div
            className="flex gap-2.5 flex-wrap"
            initial={{ opacity: 0, x: 10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2, duration: 0.35 }}
          >
            {actions}
          </motion.div>
        )}
      </div>
      <div className="divider" />
    </Reveal>
  );
}

export function EmptyState({ children }) {
  return (
    <motion.div
      className="card-flat text-center py-8"
      initial={{ opacity: 0, scale: 0.96 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4 }}
    >
      <motion.div
        className="dim mono text-xs text-textDim"
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        {children}
      </motion.div>
    </motion.div>
  );
}

import { motion } from 'framer-motion';
import { springs, ease, duration, prefersReducedMotion } from '../../lib/motionConfig';

/**
 * Kinetic typography — animated text reveals.
 * Modes: 'words' | 'chars' | 'lines' | 'blur'
 * Reserved for page titles, hero sections, and milestone headings.
 */
export default function AnimatedText({
  text,
  mode = 'words',
  className = '',
  as: Tag = 'div',
  delay = 0,
  stagger: staggerDelay = 0.04,
  once = true,
  ...rest
}) {
  if (prefersReducedMotion()) {
    return <Tag className={className} {...rest}>{text}</Tag>;
  }

  if (mode === 'blur') {
    return (
      <motion.div
        initial={{ opacity: 0, filter: 'blur(10px)' }}
        whileInView={{ opacity: 1, filter: 'blur(0px)' }}
        viewport={{ once, margin: '-40px' }}
        transition={{ duration: duration.slow, delay, ease: ease.out }}
        className={className}
        {...rest}
      >
        {text}
      </motion.div>
    );
  }

  const units = mode === 'chars'
    ? text.split('').map((c, i) => ({ text: c, key: `${c}-${i}` }))
    : text.split(' ').map((w, i) => ({ text: w, key: `${w}-${i}` }));

  return (
    <Tag className={className} {...rest}>
      <motion.span
        initial="hidden"
        whileInView="show"
        viewport={{ once, margin: '-40px' }}
        variants={{
          hidden: {},
          show: {
            transition: {
              staggerChildren: staggerDelay,
              delayChildren: delay,
            },
          },
        }}
        style={{ display: 'inline' }}
      >
        {units.map(({ text: t, key }) => (
          <motion.span
            key={key}
            variants={{
              hidden: {
                opacity: 0,
                y: mode === 'chars' ? 10 : 14,
                filter: 'blur(4px)',
              },
              show: {
                opacity: 1,
                y: 0,
                filter: 'blur(0px)',
              },
            }}
            transition={{
              duration: duration.normal,
              ease: ease.out,
            }}
            style={{
              display: 'inline-block',
              whiteSpace: t === ' ' ? 'pre' : 'normal',
            }}
          >
            {t}{mode === 'words' ? '\u00A0' : ''}
          </motion.span>
        ))}
      </motion.span>
    </Tag>
  );
}

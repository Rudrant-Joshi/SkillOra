import { motion } from 'framer-motion';
import { Reveal } from '../animations/Reveal';
import { ease, duration } from '../../lib/motionConfig';

export default function DataTable({ columns, rows, renderRow }) {
  return (
    <Reveal>
      <div className="border border-borderDim overflow-x-auto">
        <table className="w-full text-xs min-w-[600px]">
          <thead>
            <motion.tr
              className="border-b border-borderDim text-textDim uppercase tracking-wide text-[10px]"
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ duration: duration.normal }}
            >
              {columns.map((c) => (
                <th key={c} className="text-left px-4 py-3 font-normal">{c}</th>
              ))}
            </motion.tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <motion.tr
                key={i}
                initial={{ opacity: 0, y: 8 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: duration.normal, delay: 0.1 + i * 0.04, ease: ease.out }}
                className="border-b border-borderDim last:border-none hover:bg-surface2 transition-colors group"
                style={{ transition: 'background-color 0.2s ease' }}
              >
                {renderRow(row, i)}
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
    </Reveal>
  );
}

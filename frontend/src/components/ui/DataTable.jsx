import { motion } from 'framer-motion';

export default function DataTable({ columns, rows, renderRow }) {
  return (
    <div className="border border-borderDim overflow-x-auto">
      <table className="w-full text-xs min-w-[600px]">
        <thead>
          <tr className="border-b border-borderDim text-textDim uppercase tracking-wide text-[10px]">
            {columns.map((c) => (
              <th key={c} className="text-left px-4 py-3 font-normal">{c}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <motion.tr
              key={i}
              initial={{ opacity: 0, y: 8 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.3, delay: Math.min(i * 0.04, 0.4), ease: [0.16, 1, 0.3, 1] }}
              whileHover={{ backgroundColor: 'rgba(255,255,255,0.03)' }}
              className="border-b border-borderDim last:border-none hover:bg-surface2 transition-colors"
            >
              {renderRow(row, i)}
            </motion.tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

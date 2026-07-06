import { motion } from 'framer-motion';

export default function StatsCard({ label, value, icon, index }) {
  return (
    <motion.div
      className="glass-card"
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3, delay: index * 0.1 }}
      style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}
    >
      <div>
        <p className="text-muted mb-2" style={{ fontSize: '0.875rem', fontWeight: 500 }}>{label}</p>
        <p className="text-h2">{value}</p>
      </div>
      <div style={{ padding: '0.75rem', background: 'var(--light-bg)', borderRadius: 'var(--radius-md)' }}>
        {icon}
      </div>
    </motion.div>
  );
}

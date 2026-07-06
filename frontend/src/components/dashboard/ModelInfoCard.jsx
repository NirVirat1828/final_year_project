import { motion } from 'framer-motion';
import { Cpu } from 'lucide-react';

export default function ModelInfoCard({ version }) {
  return (
    <motion.div
      className="glass-card"
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3, delay: 0.2 }}
      style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}
    >
      <div>
        <p className="text-muted mb-2" style={{ fontSize: '0.875rem', fontWeight: 500 }}>Model Version</p>
        <p className="text-h2 text-dark-slate">{version}</p>
      </div>
      <div style={{ padding: '0.75rem', background: 'var(--light-bg)', borderRadius: 'var(--radius-md)' }}>
        <Cpu size={24} className="text-dark-slate" />
      </div>
    </motion.div>
  );
}

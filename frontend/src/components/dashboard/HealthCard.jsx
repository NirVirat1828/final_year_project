import { motion } from 'framer-motion';
import { Server, Activity } from 'lucide-react';

export default function HealthCard({ status }) {
  const isOnline = status === 'Online';
  
  return (
    <motion.div
      className="glass-card"
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3, delay: 0.4 }}
      style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}
    >
      <div>
        <p className="text-muted mb-2" style={{ fontSize: '0.875rem', fontWeight: 500 }}>Backend Status</p>
        <div className="flex items-center gap-2">
          <p className="text-h2" style={{ color: isOnline ? 'var(--success-green)' : '#ef4444' }}>
            {status || 'Offline'}
          </p>
          {isOnline && <span className="relative flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75" style={{ backgroundColor: 'var(--success-green)' }}></span>
            <span className="relative inline-flex rounded-full h-3 w-3" style={{ backgroundColor: 'var(--success-green)' }}></span>
          </span>}
        </div>
      </div>
      <div style={{ padding: '0.75rem', background: 'var(--light-bg)', borderRadius: 'var(--radius-md)' }}>
        <Server size={24} className={isOnline ? "text-success-green" : "text-muted"} />
      </div>
    </motion.div>
  );
}

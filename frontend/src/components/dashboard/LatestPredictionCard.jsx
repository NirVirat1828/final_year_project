import { motion } from 'framer-motion';
import { ArrowRight, Tag } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function LatestPredictionCard({ prediction }) {
  const hasPrediction = prediction && prediction.id;

  return (
    <motion.div
      className="glass-card"
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3, delay: 0.3 }}
      style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}
    >
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div>
          <p className="text-muted mb-2" style={{ fontSize: '0.875rem', fontWeight: 500 }}>Latest Prediction</p>
          {hasPrediction ? (
            <div className="flex flex-col">
              <p className="text-h3" style={{ color: 'var(--primary-orange)' }}>#{prediction.id}</p>
              <span className={`grade-badge grade-${prediction.grade?.toLowerCase() || 'default'} mt-2`} style={{ alignSelf: 'flex-start', padding: '2px 8px', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 'bold' }}>
                Grade {prediction.grade}
              </span>
            </div>
          ) : (
            <p className="text-h3 text-muted">None</p>
          )}
        </div>
        <div style={{ padding: '0.75rem', background: 'var(--light-bg)', borderRadius: 'var(--radius-md)' }}>
          <Tag size={24} className="text-primary-orange" />
        </div>
      </div>
      
      {hasPrediction && (
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1rem' }}>
          <Link to={`/history/${prediction.id}`} className="text-muted hover:text-white transition-colors" title="View Latest">
            <ArrowRight size={20} />
          </Link>
        </div>
      )}
    </motion.div>
  );
}

import { motion } from 'framer-motion';
import { BookOpen, CheckCircle, Search } from 'lucide-react';

const findings = [
  {
    id: 1,
    title: 'Raw Preprocessing Superiority',
    desc: 'Contrary to initial hypotheses, raw data preprocessing consistently outperformed advanced techniques and feature engineering.',
    evidence: 'Raw data achieved a 78.05% accuracy peak vs 75.12% for advanced.'
  },
  {
    id: 2,
    title: 'LDA Classification Dominance',
    desc: 'Linear Discriminant Analysis proved highly effective for this dataset due to the linear separability of the freshness classes.',
    evidence: 'LDA maintained the highest F1 score (77.8%) across all folds.'
  },
  {
    id: 3,
    title: 'Regression Limitations',
    desc: 'While classification yielded strong results, predicting exact shelf-life days (regression) showed higher variance, especially for borderline "Mid" fruits.',
    evidence: 'R² maxed out at 0.86, with noticeable errors around the 5-7 day mark.'
  }
];

export default function ResearchFindings() {
  return (
    <div className="flex flex-col gap-8">
      {/* Banner */}
      <section className="glass-card bg-gradient-dark" style={{ color: 'white' }}>
        <h1 className="text-h1 text-white flex items-center gap-4 mb-4"><BookOpen className="text-primary-orange" size={32} /> Research Summary</h1>
        <p style={{ fontSize: '1.125rem', opacity: 0.9, maxWidth: '800px', lineHeight: 1.6 }}>
          This project successfully developed an AI-powered system capable of determining fruit freshness using non-destructive sensor data. The research indicates that simpler linear models paired with raw data provide the most robust production-ready pipeline.
        </p>
      </section>

      {/* Findings Cards */}
      <section className="flex flex-col gap-6">
        <h2 className="text-h2">Key Conclusions</h2>
        {findings.map((finding, idx) => (
          <motion.div
            key={finding.id}
            className="glass-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.15 }}
            style={{ borderLeft: '4px solid var(--primary-orange)' }}
          >
            <div className="flex items-center gap-4 mb-2">
              <span style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', width: '32px', height: '32px', borderRadius: '50%', backgroundColor: 'rgba(255,140,66,0.1)', color: 'var(--primary-orange)', fontWeight: 'bold' }}>{finding.id}</span>
              <h3 className="text-h2" style={{ fontSize: '1.25rem' }}>{finding.title}</h3>
            </div>
            <p className="text-muted mb-4" style={{ fontSize: '1.05rem', lineHeight: 1.6, marginLeft: '3rem' }}>{finding.desc}</p>
            <div style={{ marginLeft: '3rem', padding: '1rem', backgroundColor: 'var(--light-bg)', borderRadius: 'var(--radius-sm)', display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
              <Search size={18} className="text-success-green" style={{ marginTop: '0.125rem' }} />
              <div>
                <p style={{ fontWeight: 600, fontSize: '0.875rem', marginBottom: '0.25rem' }}>Supporting Evidence</p>
                <p style={{ fontSize: '0.875rem' }}>{finding.evidence}</p>
              </div>
            </div>
          </motion.div>
        ))}
      </section>

      {/* Final Thoughts */}
      <section className="glass-card" style={{ display: 'flex', alignItems: 'center', gap: '1rem', border: '1px solid var(--success-green)' }}>
        <CheckCircle className="text-success-green" size={32} />
        <div>
          <h3 className="text-h3 mb-1">Project Complete</h3>
          <p className="text-muted">The Food Freshness Intelligence System meets all final-year project requirements and demonstrates a viable path to commercial application.</p>
        </div>
      </section>
    </div>
  );
}

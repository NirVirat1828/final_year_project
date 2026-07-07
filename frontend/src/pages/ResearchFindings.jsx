import { motion } from 'framer-motion';
import { BookOpen, CheckCircle, Search, Cpu, TrendingUp, AlertTriangle, Sparkles, Award } from 'lucide-react';

const findings = [
  {
    id: 1,
    title: 'Raw Preprocessing Superiority',
    desc: 'Contrary to initial hypotheses, raw data preprocessing consistently outperformed advanced techniques and complex feature engineering.',
    evidence: 'Raw data achieved a 78.05% accuracy peak vs 75.12% for advanced methods, while also reducing latency.',
    icon: <Cpu size={24} style={{ color: 'white' }} />,
    bgStart: '#FF9F5F',
    bgEnd: '#E67A32',
    shadow: 'rgba(255, 140, 66, 0.4)'
  },
  {
    id: 2,
    title: 'LDA Classification Dominance',
    desc: 'Linear Discriminant Analysis proved highly effective for this dataset due to the inherent linear separability of the 4 freshness classes.',
    evidence: 'LDA maintained the highest F1 score (77.8%) across all k-folds, outperforming complex non-linear models.',
    icon: <TrendingUp size={24} style={{ color: 'white' }} />,
    bgStart: '#5D9CEC',
    bgEnd: '#3498DB',
    shadow: 'rgba(52, 152, 219, 0.4)'
  },
  {
    id: 3,
    title: 'Regression Limitations',
    desc: 'While classification yielded strong reliable results, predicting exact continuous shelf-life days (regression) showed higher variance.',
    evidence: 'R² maxed out at 0.86, with noticeable errors around the critical 5-7 day borderline mark for "Mid" fruits.',
    icon: <AlertTriangle size={24} style={{ color: 'white' }} />,
    bgStart: '#FC6E51',
    bgEnd: '#E74C3C',
    shadow: 'rgba(231, 76, 60, 0.4)'
  }
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.15
    }
  }
};

const itemVariants = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 300, damping: 24 } }
};

export default function ResearchFindings() {
  return (
    <div className="flex flex-col gap-8 pb-8">
      {/* Hero Banner */}
      <motion.section 
        initial={{ opacity: 0, scale: 0.98 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="glass-card bg-gradient-dark"
        style={{ 
          position: 'relative',
          overflow: 'hidden',
          padding: '2.5rem',
          border: '1px solid rgba(255, 255, 255, 0.1)'
        }}
      >
        {/* Abstract Background Shapes */}
        <div style={{ position: 'absolute', top: '-40px', right: '-40px', width: '300px', height: '300px', borderRadius: '50%', background: 'radial-gradient(circle, rgba(255,140,66,0.15) 0%, rgba(0,0,0,0) 70%)', pointerEvents: 'none' }}></div>
        <div style={{ position: 'absolute', bottom: '-40px', left: '-40px', width: '250px', height: '250px', borderRadius: '50%', background: 'radial-gradient(circle, rgba(52,152,219,0.1) 0%, rgba(0,0,0,0) 70%)', pointerEvents: 'none' }}></div>
        
        <div style={{ position: 'relative', zIndex: 10, display: 'flex', alignItems: 'center', gap: '2rem' }}>
          <div style={{ flex: 1 }}>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', padding: '0.25rem 0.75rem', marginBottom: '1.5rem', borderRadius: '2rem', background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.1)' }}>
              <Sparkles size={14} className="text-primary-orange" />
              <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'white', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Final Analysis</span>
            </div>
            <h1 className="text-h1 text-white flex items-center gap-4 mb-4">
              Research <span className="text-gradient">Conclusions</span>
            </h1>
            <p style={{ fontSize: '1.125rem', color: 'rgba(255,255,255,0.85)', maxWidth: '800px', lineHeight: 1.6 }}>
              This project successfully developed an AI-powered system capable of determining fruit freshness using non-destructive sensor data. Extensive benchmarking reveals that <strong>simpler linear models paired with raw data preprocessing</strong> provide the most robust, low-latency production pipeline.
            </p>
          </div>
          <div style={{ display: 'none', '@media (min-width: 768px)': { display: 'flex' }, alignItems: 'center', justifyContent: 'center', width: '180px', height: '180px', borderRadius: '1.5rem', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', transform: 'rotate(3deg)', transition: 'transform 0.5s ease', ':hover': { transform: 'rotate(0)' } }}>
            <BookOpen size={80} className="text-primary-orange" style={{ opacity: 0.8 }} />
          </div>
        </div>
      </motion.section>

      {/* Findings Grid */}
      <section className="flex flex-col gap-4">
        <h2 className="text-h2 flex items-center gap-2 mb-2">
          <Award className="text-primary-orange" /> Key Discoveries
        </h2>
        
        <motion.div 
          className="grid-cols-3"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {findings.map((finding) => (
            <motion.div
              key={finding.id}
              variants={itemVariants}
              whileHover={{ y: -8, transition: { duration: 0.2 } }}
              className="glass-card"
              style={{ display: 'flex', flexDirection: 'col', position: 'relative', overflow: 'hidden', padding: '1.5rem', display: 'flex', flexDirection: 'column' }}
            >
              {/* Top Accent Line */}
              <div 
                style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '4px', background: `linear-gradient(90deg, ${finding.bgStart}, ${finding.bgEnd})`, opacity: 0.8 }}
              ></div>
              
              <div className="flex items-center gap-4 mb-4" style={{ marginTop: '0.5rem' }}>
                <div 
                  style={{ 
                    display: 'flex', alignItems: 'center', justifyContent: 'center', 
                    width: '48px', height: '48px', borderRadius: '12px', 
                    background: `linear-gradient(135deg, ${finding.bgStart}, ${finding.bgEnd})`,
                    boxShadow: `0 8px 16px -4px ${finding.shadow}`,
                    flexShrink: 0
                  }}
                >
                  {finding.icon}
                </div>
                <h3 className="text-h3" style={{ lineHeight: 1.2 }}>{finding.title}</h3>
              </div>
              
              <p className="text-muted" style={{ marginBottom: '1.5rem', flexGrow: 1, fontSize: '0.95rem' }}>
                {finding.desc}
              </p>
              
              <div style={{ marginTop: 'auto', padding: '1rem', background: 'var(--light-bg)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)' }}>
                <div className="flex items-center gap-2 mb-2">
                  <Search size={16} className="text-success-green" />
                  <span style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--dark-slate)' }}>Empirical Evidence</span>
                </div>
                <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', fontStyle: 'italic' }}>
                  "{finding.evidence}"
                </p>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </section>

      {/* Final Thoughts */}
      <motion.section 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="glass-card"
        style={{ marginTop: '1rem', position: 'relative', overflow: 'hidden', border: '1px solid rgba(46, 204, 113, 0.3)' }}
      >
        <div style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: '8px', background: 'var(--success-green)' }}></div>
        <div className="flex items-center gap-6" style={{ paddingLeft: '1rem' }}>
          <div style={{ flexShrink: 0, background: 'rgba(46, 204, 113, 0.1)', padding: '1rem', borderRadius: '50%', border: '1px solid rgba(46, 204, 113, 0.2)' }}>
            <CheckCircle className="text-success-green" size={36} />
          </div>
          <div>
            <h3 className="text-h2 mb-2">Project Success</h3>
            <p className="text-muted" style={{ fontSize: '1.05rem', maxWidth: '900px' }}>
              The Food Freshness Intelligence System meets all final-year project requirements, successfully marrying hardware sensor integration with robust machine learning to demonstrate a highly viable path toward commercial application.
            </p>
          </div>
        </div>
      </motion.section>
    </div>
  );
}

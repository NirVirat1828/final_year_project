import { motion } from 'framer-motion';
import { ArrowRight, Brain, FlaskConical, TrendingUp, Trophy } from 'lucide-react';
import { Link } from 'react-router-dom';

const kpis = [
  { label: 'Best Classification Accuracy', value: '78.05%', icon: <Trophy size={24} className="text-primary-orange" /> },
  { label: 'Best Regression R² Score', value: '0.86', icon: <TrendingUp size={24} className="text-success-green" /> },
  { label: 'Algorithms Tested', value: '9', icon: <Brain size={24} className="text-dark-slate" /> },
  { label: 'Experiment Configurations', value: '18', icon: <FlaskConical size={24} className="text-primary-orange" /> }
];

const winners = [
  { rank: 'Gold', model: 'LDA + Raw', metric: 'Accuracy: 78.05%', color: 'linear-gradient(135deg, #FFD700, #FDB931)' },
  { rank: 'Silver', model: 'Random Forest + Raw', metric: 'Accuracy: 77.32%', color: 'linear-gradient(135deg, #E0E0E0, #BDBDBD)' },
  { rank: 'Bronze', model: 'SVM + Raw', metric: 'Accuracy: 76.83%', color: 'linear-gradient(135deg, #CD7F32, #A0522D)' }
];

const quickNav = [
  { path: '/tournament', label: 'Tournament Arena', desc: 'View complete model leaderboards.' },
  { path: '/classification', label: 'Classification Dashboard', desc: 'Deep dive into classification metrics.' },
  { path: '/regression', label: 'Regression Dashboard', desc: 'Explore regression model performance.' },
  { path: '/prediction', label: 'Live Prediction', desc: 'Test models with new sensor data.' }
];

export default function ExecutiveDashboard() {
  return (
    <div className="flex flex-col gap-8" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Hero Banner */}
      <motion.section
        className="glass-card bg-gradient-dark"
        style={{ color: 'white', position: 'relative', overflow: 'hidden' }}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div style={{ position: 'relative', zIndex: 2 }}>
          <h1 className="text-h1" style={{ color: 'white', marginBottom: '0.5rem' }}>Food Freshness Intelligence System</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '1.125rem' }}>AI-Powered Fruit Freshness Classification and Shelf-Life Prediction Platform</p>
        </div>
        {/* Animated Background Graphic placeholder */}
        <div style={{ position: 'absolute', top: '-50%', right: '-10%', width: '300px', height: '300px', background: 'radial-gradient(circle, rgba(255,140,66,0.3) 0%, rgba(0,0,0,0) 70%)', borderRadius: '50%', filter: 'blur(40px)' }} />
      </motion.section>

      {/* KPI Cards Grid */}
      <section className="grid-cols-4">
        {kpis.map((kpi, idx) => (
          <motion.div
            key={idx}
            className="glass-card"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3, delay: idx * 0.1 }}
            style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}
          >
            <div>
              <p className="text-muted mb-2" style={{ fontSize: '0.875rem', fontWeight: 500 }}>{kpi.label}</p>
              <p className="text-h2">{kpi.value}</p>
            </div>
            <div style={{ padding: '0.75rem', background: 'var(--light-bg)', borderRadius: 'var(--radius-md)' }}>
              {kpi.icon}
            </div>
          </motion.div>
        ))}
      </section>

      {/* Tournament Winners */}
      <section>
        <h2 className="text-h2 mb-4">Tournament Winners</h2>
        <div className="grid-cols-3">
          {winners.map((winner, idx) => (
            <motion.div
              key={idx}
              className="glass-card"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.4, delay: 0.2 + idx * 0.1 }}
              style={{ borderTop: `4px solid transparent`, borderImage: `${winner.color} 1` }}
            >
              <div style={{ display: 'inline-block', padding: '0.25rem 0.75rem', background: winner.color, color: 'white', borderRadius: '9999px', fontSize: '0.75rem', fontWeight: 'bold', marginBottom: '1rem' }}>
                {winner.rank}
              </div>
              <h3 className="text-h3 mb-2">{winner.model}</h3>
              <p className="text-muted">{winner.metric}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Quick Navigation Cards */}
      <section>
        <h2 className="text-h2 mb-4">Quick Navigation</h2>
        <div className="grid-cols-4">
          {quickNav.map((nav, idx) => (
            <Link key={idx} to={nav.path} style={{ textDecoration: 'none' }}>
              <motion.div
                className="glass-card"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                style={{ cursor: 'pointer', height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}
              >
                <div>
                  <h3 className="text-h3 mb-2" style={{ color: 'var(--primary-orange)' }}>{nav.label}</h3>
                  <p className="text-muted" style={{ fontSize: '0.875rem' }}>{nav.desc}</p>
                </div>
                <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1rem' }}>
                  <ArrowRight size={20} color="var(--primary-orange)" />
                </div>
              </motion.div>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}

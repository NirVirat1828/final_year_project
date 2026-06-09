import { useState } from 'react';
import { motion } from 'framer-motion';
import { Swords, CheckCircle2 } from 'lucide-react';
import { ResponsiveContainer, Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Tooltip, Legend } from 'recharts';

const models = ['Linear Discriminant Analysis', 'Random Forest', 'Support Vector Machine', 'Gradient Boosting', 'Logistic Regression'];

const mockComparisonData = [
  { metric: 'Accuracy', A: 78.05, B: 77.32, fullMark: 100 },
  { metric: 'Precision', A: 75.1, B: 74.2, fullMark: 100 },
  { metric: 'Recall', A: 76.5, B: 75.9, fullMark: 100 },
  { metric: 'F1 Score', A: 77.8, B: 76.5, fullMark: 100 },
  { metric: 'Speed (inv)', A: 90, B: 65, fullMark: 100 }, // Scaled so higher is better
  { metric: 'Robustness', A: 82, B: 88, fullMark: 100 },
];

export default function ModelBattleArena() {
  const [modelA, setModelA] = useState(models[0]);
  const [modelB, setModelB] = useState(models[1]);

  return (
    <div className="flex flex-col gap-8" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <h1 className="text-h1 flex items-center gap-4"><Swords className="text-primary-orange" size={32} /> Model Battle Arena</h1>

      {/* Model Selectors */}
      <section className="glass-card flex justify-between items-center bg-gradient-dark" style={{ padding: '2rem' }}>
        <div style={{ flex: 1 }}>
          <label className="text-muted mb-2" style={{ display: 'block', color: 'rgba(255,255,255,0.7)' }}>Corner A (Orange)</label>
          <select 
            className="btn w-full" 
            style={{ padding: '0.75rem', fontSize: '1.125rem', backgroundColor: 'var(--primary-orange)', color: 'white', border: 'none' }}
            value={modelA}
            onChange={(e) => setModelA(e.target.value)}
          >
            {models.map(m => <option key={m} value={m}>{m}</option>)}
          </select>
        </div>
        
        <div style={{ padding: '0 3rem' }}>
          <p className="text-h1" style={{ color: 'white', fontStyle: 'italic', opacity: 0.5 }}>VS</p>
        </div>
        
        <div style={{ flex: 1 }}>
          <label className="text-muted mb-2" style={{ display: 'block', color: 'rgba(255,255,255,0.7)' }}>Corner B (Green)</label>
          <select 
            className="btn w-full" 
            style={{ padding: '0.75rem', fontSize: '1.125rem', backgroundColor: 'var(--success-green)', color: 'white', border: 'none' }}
            value={modelB}
            onChange={(e) => setModelB(e.target.value)}
          >
            {models.map(m => <option key={m} value={m}>{m}</option>)}
          </select>
        </div>
      </section>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
        {/* Radar Chart */}
        <section className="glass-card flex flex-col justify-center" style={{ minHeight: '400px' }}>
          <h2 className="text-h3 mb-4 text-center">Performance Radar</h2>
          <ResponsiveContainer width="100%" height={350}>
            <RadarChart cx="50%" cy="50%" outerRadius="80%" data={mockComparisonData}>
              <PolarGrid stroke="var(--border-color)" />
              <PolarAngleAxis dataKey="metric" tick={{ fill: 'var(--text-secondary)', fontSize: 12 }} />
              <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: 'transparent' }} stroke="transparent" />
              <Radar name={modelA} dataKey="A" stroke="var(--primary-orange)" fill="var(--primary-orange)" fillOpacity={0.4} />
              <Radar name={modelB} dataKey="B" stroke="var(--success-green)" fill="var(--success-green)" fillOpacity={0.4} />
              <Tooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: 'var(--shadow-md)' }} />
              <Legend wrapperStyle={{ paddingTop: '20px' }} />
            </RadarChart>
          </ResponsiveContainer>
        </section>

        {/* Comparison Metrics and Winner Analysis */}
        <section className="flex flex-col gap-6">
          <div className="glass-card">
            <h2 className="text-h3 mb-4">Direct Comparison</h2>
            <div className="table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Metric</th>
                    <th style={{ color: 'var(--primary-orange)' }}>{modelA}</th>
                    <th style={{ color: 'var(--success-green)' }}>{modelB}</th>
                  </tr>
                </thead>
                <tbody>
                  {mockComparisonData.map((row, idx) => (
                    <tr key={idx}>
                      <td style={{ fontWeight: 500 }}>{row.metric}</td>
                      <td style={{ fontWeight: row.A > row.B ? 'bold' : 'normal' }}>{row.A}</td>
                      <td style={{ fontWeight: row.B > row.A ? 'bold' : 'normal' }}>{row.B}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <motion.div 
            className="glass-card bg-gradient-primary" 
            style={{ color: 'white' }}
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle2 size={24} />
              <h2 className="text-h2 text-white">Winner Analysis</h2>
            </div>
            <p style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '0.5rem' }}>{modelA} dominates by 1.2% overall</p>
            <p style={{ opacity: 0.9, lineHeight: 1.6 }}>
              While {modelB} shows slightly better robustness, {modelA} is significantly faster during training and prediction phases while maintaining a higher accuracy and F1 score. Recommended for production deployment.
            </p>
          </motion.div>
        </section>
      </div>
    </div>
  );
}

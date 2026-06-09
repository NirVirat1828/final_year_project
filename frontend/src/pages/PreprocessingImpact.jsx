import { useState } from 'react';
import { motion } from 'framer-motion';
import { GitMerge, ArrowRight, Lightbulb } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from 'recharts';

const pipelineOptions = ['Raw Data', 'Advanced Processing', 'Feature Engineering'];

const impactData = [
  { metric: 'Accuracy', Raw: 78.05, Advanced: 75.12, Engineered: 73.5 },
  { metric: 'Precision', Raw: 76.5, Advanced: 74.2, Engineered: 72.8 },
  { metric: 'Recall', Raw: 77.2, Advanced: 75.5, Engineered: 74.1 },
  { metric: 'F1 Score', Raw: 76.8, Advanced: 74.8, Engineered: 73.4 }
];

export default function PreprocessingImpact() {
  const [selectedPipeline, setSelectedPipeline] = useState(pipelineOptions[0]);

  return (
    <div className="flex flex-col gap-8">
      <h1 className="text-h1 flex items-center gap-4"><GitMerge className="text-primary-orange" size={32} /> Preprocessing Impact Analysis</h1>

      <section className="glass-card flex items-center gap-4">
        <span className="text-muted" style={{ fontWeight: 500 }}>Select Pipeline Layer:</span>
        {pipelineOptions.map((option) => (
          <button 
            key={option}
            className={`btn ${selectedPipeline === option ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => setSelectedPipeline(option)}
          >
            {option}
          </button>
        ))}
      </section>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: '2rem' }}>
        <section className="glass-card flex flex-col gap-6">
          <h2 className="text-h2">Impact Comparison</h2>
          <div style={{ height: '400px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={impactData} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border-color)" />
                <XAxis dataKey="metric" tick={{ fill: 'var(--text-secondary)' }} axisLine={false} tickLine={false} />
                <YAxis domain={[60, 85]} tick={{ fill: 'var(--text-secondary)' }} axisLine={false} tickLine={false} />
                <Tooltip cursor={{ fill: 'transparent' }} contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: 'var(--shadow-md)' }} />
                <Legend wrapperStyle={{ paddingTop: '20px' }} />
                <Bar dataKey="Raw" fill="var(--primary-orange)" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Advanced" fill="var(--success-green)" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Engineered" fill="var(--dark-slate-light)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="flex flex-col gap-6">
          <motion.div 
            className="glass-card bg-gradient-dark" 
            style={{ color: 'white', flex: 1 }}
            initial={{ x: 20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
          >
            <div className="flex items-center gap-2 mb-4">
              <Lightbulb className="text-primary-orange" size={24} />
              <h2 className="text-h2 text-white" style={{ fontSize: '1.25rem' }}>Research Insights</h2>
            </div>
            <div className="flex flex-col gap-4">
              <div style={{ padding: '1rem', background: 'rgba(255,255,255,0.1)', borderRadius: 'var(--radius-md)' }}>
                <p style={{ fontWeight: 600, color: 'var(--primary-orange)', marginBottom: '0.25rem' }}>Key Finding</p>
                <p style={{ fontSize: '0.875rem', lineHeight: 1.6 }}>Raw preprocessing outperformed advanced preprocessing across all major metrics.</p>
              </div>
              <div style={{ padding: '1rem', background: 'rgba(255,255,255,0.1)', borderRadius: 'var(--radius-md)' }}>
                <p style={{ fontWeight: 600, color: 'var(--success-green)', marginBottom: '0.25rem' }}>Observation</p>
                <p style={{ fontSize: '0.875rem', lineHeight: 1.6 }}>Feature engineering introduced noise, reducing the F1 score by ~3.4% compared to raw sensor data.</p>
              </div>
            </div>
          </motion.div>
        </section>
      </div>
    </div>
  );
}

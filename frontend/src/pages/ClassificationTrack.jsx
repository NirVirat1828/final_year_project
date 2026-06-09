import { useState } from 'react';
import { motion } from 'framer-motion';
import { PieChart as PieChartIcon, Activity } from 'lucide-react';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend } from 'recharts';

const models = ['Linear Discriminant Analysis', 'Random Forest', 'Support Vector Machine'];

const classDistData = [
  { name: 'Fresh', value: 412 },
  { name: 'Mid', value: 430 },
  { name: 'Spoiled', value: 406 }
];
const COLORS = ['#2ECC71', '#F59E0B', '#EF4444'];

const predictionSamples = [
  { id: 1042, actual: 'Fresh', predicted: 'Fresh', confidence: 96 },
  { id: 1043, actual: 'Mid', predicted: 'Fresh', confidence: 52 },
  { id: 1044, actual: 'Spoiled', predicted: 'Spoiled', confidence: 89 },
  { id: 1045, actual: 'Mid', predicted: 'Mid', confidence: 78 }
];

export default function ClassificationTrack() {
  const [selectedModel, setSelectedModel] = useState(models[0]);

  return (
    <div className="flex flex-col gap-8">
      <div className="flex justify-between items-center">
        <h1 className="text-h1 flex items-center gap-4"><PieChartIcon className="text-primary-orange" size={32} /> Classification Track</h1>
        <select 
          className="btn btn-outline" 
          value={selectedModel} 
          onChange={(e) => setSelectedModel(e.target.value)}
          style={{ padding: '0.5rem 1rem' }}
        >
          {models.map(m => <option key={m} value={m}>{m}</option>)}
        </select>
      </div>

      {/* Metric Cards */}
      <section className="grid-cols-4">
        {[
          { label: 'Accuracy', value: '78.05%' },
          { label: 'Precision', value: '76.50%' },
          { label: 'Recall', value: '77.20%' },
          { label: 'F1 Score', value: '76.80%' }
        ].map((kpi, idx) => (
          <motion.div key={idx} className="glass-card" initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: idx * 0.1 }}>
            <p className="text-muted mb-2" style={{ fontSize: '0.875rem' }}>{kpi.label}</p>
            <p className="text-h2 text-primary-orange">{kpi.value}</p>
          </motion.div>
        ))}
      </section>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2rem' }}>
        {/* Confusion Matrix Placeholder */}
        <section className="glass-card flex flex-col gap-4">
          <h2 className="text-h3">Confusion Matrix</h2>
          <div className="flex items-center justify-center bg-gradient-dark" style={{ height: '300px', borderRadius: 'var(--radius-md)', color: 'white', opacity: 0.9 }}>
            <div className="flex flex-col items-center gap-2">
              <Activity size={32} className="text-primary-orange" />
              <p>Interactive Confusion Matrix Heatmap</p>
              <p className="text-muted" style={{ fontSize: '0.75rem' }}>Hover to reveal True Positive / False Positive rates.</p>
            </div>
          </div>
        </section>

        {/* Class Distribution */}
        <section className="glass-card flex flex-col gap-4">
          <h2 className="text-h3">Class Distribution</h2>
          <div style={{ height: '300px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={classDistData} cx="50%" cy="50%" innerRadius={60} outerRadius={90} paddingAngle={5} dataKey="value">
                  {classDistData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: 'var(--shadow-md)' }} />
                <Legend wrapperStyle={{ paddingTop: '20px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </section>
      </div>

      {/* Prediction Samples */}
      <section className="glass-card">
        <h2 className="text-h3 mb-4">Prediction Samples</h2>
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Sample ID</th>
                <th>Actual Class</th>
                <th>Predicted Class</th>
                <th>Confidence</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {predictionSamples.map((row) => (
                <tr key={row.id}>
                  <td style={{ fontWeight: 500 }}>#{row.id}</td>
                  <td>{row.actual}</td>
                  <td style={{ fontWeight: 600 }}>{row.predicted}</td>
                  <td>{row.confidence}%</td>
                  <td>
                    {row.actual === row.predicted ? (
                      <span className="status-badge success">Correct</span>
                    ) : (
                      <span className="status-badge" style={{ backgroundColor: 'rgba(239, 68, 68, 0.1)', color: '#EF4444' }}>Incorrect</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

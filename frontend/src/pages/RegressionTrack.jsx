import { useState } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, Activity } from 'lucide-react';
import { ResponsiveContainer, ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

const models = ['Random Forest Regressor', 'Support Vector Regressor', 'Linear Regression'];

const scatterData = [
  { actual: 12.4, predicted: 12.1 },
  { actual: 10.1, predicted: 9.8 },
  { actual: 5.2, predicted: 6.0 },
  { actual: 11.8, predicted: 11.5 },
  { actual: 8.9, predicted: 9.2 },
  { actual: 15.0, predicted: 14.8 },
  { actual: 7.4, predicted: 7.9 },
  { actual: 13.2, predicted: 13.0 }
];

export default function RegressionTrack() {
  const [selectedModel, setSelectedModel] = useState(models[0]);

  return (
    <div className="flex flex-col gap-8">
      <div className="flex justify-between items-center">
        <h1 className="text-h1 flex items-center gap-4"><TrendingUp className="text-primary-orange" size={32} /> Regression Track</h1>
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
          { label: 'R² Score', value: '0.86' },
          { label: 'RMSE', value: '1.24' },
          { label: 'MAE', value: '0.98' },
          { label: 'MSE', value: '1.54' }
        ].map((kpi, idx) => (
          <motion.div key={idx} className="glass-card" initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: idx * 0.1 }}>
            <p className="text-muted mb-2" style={{ fontSize: '0.875rem' }}>{kpi.label}</p>
            <p className="text-h2 text-success-green">{kpi.value}</p>
          </motion.div>
        ))}
      </section>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2rem' }}>
        {/* Actual vs Predicted Scatter Plot */}
        <section className="glass-card flex flex-col gap-4">
          <h2 className="text-h3">Actual vs Predicted (Folic Acid)</h2>
          <div style={{ height: '350px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
                <XAxis type="number" dataKey="actual" name="Actual" unit="mg" stroke="var(--text-secondary)" />
                <YAxis type="number" dataKey="predicted" name="Predicted" unit="mg" stroke="var(--text-secondary)" />
                <Tooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: 'var(--shadow-md)' }} />
                <Legend wrapperStyle={{ paddingTop: '20px' }} />
                <Scatter name="Predictions" data={scatterData} fill="var(--primary-orange)" />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </section>

        {/* Residual Plot Placeholder */}
        <section className="glass-card flex flex-col gap-4">
          <h2 className="text-h3">Residual Distribution</h2>
          <div className="flex items-center justify-center bg-gradient-dark" style={{ height: '350px', borderRadius: 'var(--radius-md)', color: 'white', opacity: 0.9 }}>
            <div className="flex flex-col items-center gap-2">
              <Activity size={32} className="text-success-green" />
              <p>Residuals Histogram</p>
              <p className="text-muted" style={{ fontSize: '0.75rem' }}>Displays prediction errors.</p>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

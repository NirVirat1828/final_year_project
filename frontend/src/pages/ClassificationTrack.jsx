import { useState } from 'react';
import { motion } from 'framer-motion';
import { PieChart as PieChartIcon, Grid } from 'lucide-react';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend } from 'recharts';

const models = ['Linear Discriminant Analysis', 'Random Forest', 'Support Vector Machine'];

const modelData = {
  'Linear Discriminant Analysis': {
    kpis: [
      { label: 'Accuracy', value: '76.45%' },
      { label: 'Precision', value: '75.20%' },
      { label: 'Recall', value: '75.90%' },
      { label: 'F1 Score', value: '75.50%' }
    ],
    classDist: [
      { name: 'Fresh', value: 395 },
      { name: 'Mid', value: 420 },
      { name: 'Spoiled', value: 433 }
    ],
    samples: [
      { id: 1042, actual: 'Fresh', predicted: 'Fresh', confidence: 92 },
      { id: 1043, actual: 'Mid', predicted: 'Fresh', confidence: 58 },
      { id: 1044, actual: 'Spoiled', predicted: 'Spoiled', confidence: 81 },
      { id: 1045, actual: 'Mid', predicted: 'Mid', confidence: 71 }
    ],
    matrix: [
      [88, 9, 3],
      [15, 72, 13],
      [4, 12, 84]
    ]
  },
  'Random Forest': {
    kpis: [
      { label: 'Accuracy', value: '86.20%' },
      { label: 'Precision', value: '85.90%' },
      { label: 'Recall', value: '86.50%' },
      { label: 'F1 Score', value: '86.20%' }
    ],
    classDist: [
      { name: 'Fresh', value: 425 },
      { name: 'Mid', value: 400 },
      { name: 'Spoiled', value: 423 }
    ],
    samples: [
      { id: 1042, actual: 'Fresh', predicted: 'Fresh', confidence: 98 },
      { id: 1043, actual: 'Mid', predicted: 'Mid', confidence: 74 },
      { id: 1044, actual: 'Spoiled', predicted: 'Spoiled', confidence: 94 },
      { id: 1045, actual: 'Mid', predicted: 'Mid', confidence: 88 }
    ],
    matrix: [
      [94, 5, 1],
      [6, 86, 8],
      [2, 7, 91]
    ]
  },
  'Support Vector Machine': {
    kpis: [
      { label: 'Accuracy', value: '82.10%' },
      { label: 'Precision', value: '81.40%' },
      { label: 'Recall', value: '82.30%' },
      { label: 'F1 Score', value: '81.80%' }
    ],
    classDist: [
      { name: 'Fresh', value: 410 },
      { name: 'Mid', value: 415 },
      { name: 'Spoiled', value: 423 }
    ],
    samples: [
      { id: 1042, actual: 'Fresh', predicted: 'Fresh', confidence: 95 },
      { id: 1043, actual: 'Mid', predicted: 'Fresh', confidence: 61 },
      { id: 1044, actual: 'Spoiled', predicted: 'Spoiled', confidence: 87 },
      { id: 1045, actual: 'Mid', predicted: 'Mid', confidence: 79 }
    ],
    matrix: [
      [91, 7, 2],
      [10, 80, 10],
      [3, 9, 88]
    ]
  }
};

const COLORS = ['#2ECC71', '#F59E0B', '#EF4444'];
const classes = ['Fresh', 'Mid', 'Spoiled'];

export default function ClassificationTrack() {
  const [selectedModel, setSelectedModel] = useState(models[0]);

  const activeData = modelData[selectedModel];

  return (
    <div className="flex flex-col gap-8">
      <div className="flex justify-between items-center">
        <h1 className="text-h1 flex items-center gap-4"><PieChartIcon className="text-primary-orange" size={32} /> Classification Track</h1>
        <select 
          className="btn btn-outline" 
          value={selectedModel} 
          onChange={(e) => setSelectedModel(e.target.value)}
          style={{ padding: '0.5rem 1rem', outline: 'none' }}
        >
          {models.map(m => <option key={m} value={m}>{m}</option>)}
        </select>
      </div>

      {/* Metric Cards */}
      <section className="grid-cols-4">
        {activeData.kpis.map((kpi, idx) => (
          <motion.div 
            key={selectedModel + idx} 
            className="glass-card" 
            initial={{ y: 15, opacity: 0 }} 
            animate={{ y: 0, opacity: 1 }} 
            transition={{ delay: idx * 0.05 }}
          >
            <p className="text-muted mb-2" style={{ fontSize: '0.875rem' }}>{kpi.label}</p>
            <p className="text-h2 text-primary-orange">{kpi.value}</p>
          </motion.div>
        ))}
      </section>

      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '2rem' }}>
        {/* Real Interactive Confusion Matrix Heatmap */}
        <section className="glass-card flex flex-col gap-4">
          <h2 className="text-h3 flex items-center gap-2">
            <Grid size={18} className="text-primary-orange" />
            Confusion Matrix Heatmap (%)
          </h2>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginTop: '1rem', padding: '1rem', background: 'var(--light-bg)', borderRadius: 'var(--radius-md)' }}>
            {/* Headers row */}
            <div style={{ display: 'grid', gridTemplateColumns: '80px 1fr 1fr 1fr', gap: '0.5rem', textAlign: 'center', fontWeight: 'bold', fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>
              <div></div>
              <div>Predicted Fresh</div>
              <div>Predicted Mid</div>
              <div>Predicted Spoiled</div>
            </div>

            {/* Matrix Rows */}
            {activeData.matrix.map((rowVals, rowIdx) => (
              <div key={rowIdx} style={{ display: 'grid', gridTemplateColumns: '80px 1fr 1fr 1fr', gap: '0.5rem', alignItems: 'center' }}>
                <div style={{ fontWeight: 'bold', fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>
                  Actual {classes[rowIdx]}
                </div>
                {rowVals.map((val, colIdx) => (
                  <motion.div
                    key={colIdx}
                    initial={{ scale: 0.95, opacity: 0.5 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ duration: 0.2 }}
                    style={{
                      height: '60px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '1rem',
                      fontWeight: 600,
                      borderRadius: 'var(--radius-sm)',
                      backgroundColor: `rgba(255, 140, 66, ${val / 100})`,
                      color: val > 45 ? 'white' : 'var(--text-primary)',
                      border: '1px solid rgba(0,0,0,0.05)',
                      boxShadow: val > 70 ? 'var(--shadow-sm)' : 'none'
                    }}
                    title={`Actual ${classes[rowIdx]} predicted as ${classes[colIdx]}: ${val}%`}
                  >
                    {val}%
                  </motion.div>
                ))}
              </div>
            ))}
          </div>
          <span className="text-muted" style={{ fontSize: '0.75rem', fontStyle: 'italic', textAlign: 'center' }}>
            Note: Deeper shades indicate higher classification correctness.
          </span>
        </section>

        {/* Class Distribution Pie Chart */}
        <section className="glass-card flex flex-col gap-4">
          <h2 className="text-h3">Class Distribution</h2>
          <div style={{ height: '300px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie 
                  data={activeData.classDist} 
                  cx="50%" 
                  cy="50%" 
                  innerRadius={60} 
                  outerRadius={90} 
                  paddingAngle={5} 
                  dataKey="value"
                  animationDuration={600}
                >
                  {activeData.classDist.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid var(--border-color)', boxShadow: 'var(--shadow-md)' }} />
                <Legend wrapperStyle={{ paddingTop: '20px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </section>
      </div>

      {/* Prediction Samples list */}
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
              {activeData.samples.map((row) => (
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

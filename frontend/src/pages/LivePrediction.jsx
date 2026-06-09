import { useState } from 'react';
import { motion } from 'framer-motion';
import { Upload, Play, AlertCircle, Clock, Activity } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';

const sensors = [
  { id: 'folicAcid', label: 'Folic Acid (mg)' },
  { id: 'vitC', label: 'Vitamin C (mg)' },
  { id: 'pH', label: 'pH Level' },
  { id: 'moisture', label: 'Moisture (%)' },
  { id: 'firmness', label: 'Firmness (N)' },
  { id: 'brix', label: 'Brix (°Bx)' },
  { id: 'weight', label: 'Weight (g)' },
  { id: 'colorRed', label: 'Color Red (R)' },
  { id: 'colorGreen', label: 'Color Green (G)' },
  { id: 'colorBlue', label: 'Color Blue (B)' },
  { id: 'ethylene', label: 'Ethylene (ppm)' }
];

const featureContributions = [
  { name: 'pH Level', value: 0.85, positive: false },
  { name: 'Folic Acid', value: 0.62, positive: true },
  { name: 'Firmness', value: 0.54, positive: true },
  { name: 'Moisture', value: 0.31, positive: false }
];

export default function LivePrediction() {
  const [method, setMethod] = useState('manual');
  const [isPredicting, setIsPredicting] = useState(false);
  const [result, setResult] = useState(null);

  const handlePredict = () => {
    setIsPredicting(true);
    // Simulate network request
    setTimeout(() => {
      setResult({
        grade: 'Fresh',
        shelfLife: '14 Days',
        confidence: 94,
        folicAcidPred: '12.4 mg'
      });
      setIsPredicting(false);
    }, 1500);
  };

  return (
    <div className="flex flex-col gap-8" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <h1 className="text-h1">Live Prediction Engine</h1>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
        {/* Input Section */}
        <section className="glass-card flex flex-col gap-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-h2">Input Data</h2>
            <div style={{ display: 'flex', gap: '0.5rem', background: 'var(--light-bg)', padding: '0.25rem', borderRadius: 'var(--radius-lg)' }}>
              <button 
                className={`btn whitespace-nowrap ${method === 'manual' ? 'btn-primary' : 'btn-outline'}`}
                style={{ padding: '0.25rem 1rem', border: 'none' }}
                onClick={() => setMethod('manual')}
              >
                Manual Input
              </button>
              <button 
                className={`btn whitespace-nowrap ${method === 'csv' ? 'btn-primary' : 'btn-outline'}`}
                style={{ padding: '0.25rem 1rem', border: 'none' }}
                onClick={() => setMethod('csv')}
              >
                <Upload size={16} /> CSV Upload
              </button>
            </div>
          </div>

          {method === 'manual' ? (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1rem' }}>
              {sensors.map((sensor) => (
                <div key={sensor.id}>
                  <label className="text-muted mb-2" style={{ display: 'block', fontSize: '0.875rem' }}>{sensor.label}</label>
                  <input 
                    type="number" 
                    placeholder="0.00" 
                    style={{ width: '100%', padding: '0.5rem 1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', outline: 'none' }}
                  />
                </div>
              ))}
            </div>
          ) : (
            <div style={{ padding: '3rem 2rem', border: '2px dashed var(--border-color)', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
              <Upload size={32} style={{ color: 'var(--text-secondary)', margin: '0 auto 1rem' }} />
              <p className="text-h3 mb-2">Drag & Drop CSV File</p>
              <p className="text-muted">or click to browse</p>
            </div>
          )}

          <button 
            className="btn btn-primary w-full" 
            style={{ padding: '1rem', fontSize: '1.125rem', marginTop: '1rem' }}
            onClick={handlePredict}
            disabled={isPredicting}
          >
            {isPredicting ? <span className="animate-pulse">Analyzing Data...</span> : <><Play size={20} /> Run Prediction</>}
          </button>
        </section>

        {/* Results Section */}
        <section className="flex flex-col gap-6">
          {result ? (
            <motion.div 
              className="glass-card" 
              initial={{ opacity: 0, scale: 0.95 }} 
              animate={{ opacity: 1, scale: 1 }}
              style={{ borderTop: '4px solid var(--success-green)' }}
            >
              <h2 className="text-h2 mb-6">Prediction Results</h2>
              
              <div style={{ display: 'flex', gap: '2rem', marginBottom: '2rem' }}>
                {/* Confidence Gauge Placeholder */}
                <div style={{ width: '120px', height: '120px', borderRadius: '50%', border: '8px solid var(--success-green)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column' }}>
                  <span className="text-h2">{result.confidence}%</span>
                  <span className="text-muted" style={{ fontSize: '0.75rem' }}>Confidence</span>
                </div>
                
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '1rem', justifyContent: 'center' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>
                    <span className="text-muted">Freshness Grade</span>
                    <span className="text-h3" style={{ color: 'var(--success-green)' }}>{result.grade}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>
                    <span className="text-muted">Estimated Shelf Life</span>
                    <span className="text-h3">{result.shelfLife}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span className="text-muted">Predicted Folic Acid</span>
                    <span className="text-h3">{result.folicAcidPred}</span>
                  </div>
                </div>
              </div>

              {/* Feature Contribution */}
              <div>
                <h3 className="text-h3 mb-4">Feature Contributions</h3>
                <div style={{ height: '200px' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={featureContributions} layout="vertical" margin={{ left: 40 }}>
                      <XAxis type="number" hide />
                      <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: 'var(--text-secondary)' }} />
                      <Tooltip cursor={{ fill: 'transparent' }} contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: 'var(--shadow-md)' }} />
                      <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                        {featureContributions.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.positive ? 'var(--success-green)' : 'var(--primary-orange)'} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </motion.div>
          ) : (
            <div className="glass-card flex items-center justify-center" style={{ height: '100%', minHeight: '400px', flexDirection: 'column', color: 'var(--text-secondary)' }}>
              <Activity size={48} style={{ marginBottom: '1rem', opacity: 0.5 }} />
              <p className="text-h3">Awaiting Data Input</p>
              <p className="text-muted">Fill out the form and run prediction.</p>
            </div>
          )}

          {/* History Timeline */}
          <div className="glass-card">
            <h3 className="text-h3 mb-4 flex items-center gap-2"><Clock size={18} /> Recent Predictions</h3>
            <div className="flex flex-col gap-4">
              {[1, 2, 3].map((item) => (
                <div key={item} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.75rem', backgroundColor: 'var(--light-bg)', borderRadius: 'var(--radius-sm)' }}>
                  <div>
                    <p style={{ fontWeight: 500 }}>Batch #{1000 + item}</p>
                    <p className="text-muted" style={{ fontSize: '0.75rem' }}>10 mins ago</p>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <p style={{ color: 'var(--success-green)', fontWeight: 600 }}>Fresh</p>
                    <p className="text-muted" style={{ fontSize: '0.75rem' }}>92% Conf.</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

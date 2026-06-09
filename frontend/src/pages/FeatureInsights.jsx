import { useState } from 'react';
import { motion } from 'framer-motion';
import { Lightbulb, Share2 } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from 'recharts';

const featureImportance = [
  { name: 'pH Level', value: 0.85 },
  { name: 'Folic Acid', value: 0.62 },
  { name: 'Firmness', value: 0.54 },
  { name: 'Moisture', value: 0.31 },
  { name: 'Vitamin C', value: 0.25 },
  { name: 'Brix', value: 0.18 }
];

export default function FeatureInsights() {
  const [selectedFeature, setSelectedFeature] = useState(featureImportance[0].name);

  return (
    <div className="flex flex-col gap-8">
      <h1 className="text-h1 flex items-center gap-4"><Lightbulb className="text-primary-orange" size={32} /> Explainable AI: Feature Insights</h1>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
        {/* Feature Importance Ranking */}
        <section className="glass-card flex flex-col gap-4">
          <h2 className="text-h3">Global Feature Importance</h2>
          <div style={{ height: '350px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={featureImportance} layout="vertical" margin={{ left: 60 }}>
                <XAxis type="number" hide />
                <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: 'var(--text-secondary)' }} />
                <Tooltip cursor={{ fill: 'transparent' }} contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: 'var(--shadow-md)' }} />
                <Bar dataKey="value" radius={[0, 4, 4, 0]} onClick={(data) => setSelectedFeature(data.name)} style={{ cursor: 'pointer' }}>
                  {featureImportance.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.name === selectedFeature ? 'var(--primary-orange)' : 'var(--border-color)'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="flex flex-col gap-6">
          {/* Feature Detail Card */}
          <motion.div 
            className="glass-card" 
            key={selectedFeature}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
          >
            <h2 className="text-h2 mb-4 text-primary-orange">{selectedFeature}</h2>
            <div className="grid-cols-2 mb-6">
              <div style={{ padding: '1rem', background: 'var(--light-bg)', borderRadius: 'var(--radius-sm)' }}>
                <p className="text-muted" style={{ fontSize: '0.75rem' }}>Importance Score</p>
                <p className="text-h3">{featureImportance.find(f => f.name === selectedFeature)?.value.toFixed(2)}</p>
              </div>
              <div style={{ padding: '1rem', background: 'var(--light-bg)', borderRadius: 'var(--radius-sm)' }}>
                <p className="text-muted" style={{ fontSize: '0.75rem' }}>Mean Value</p>
                <p className="text-h3">4.2</p>
              </div>
            </div>
            
            <div className="flex items-center gap-2 mb-2">
              <Lightbulb size={18} className="text-success-green" />
              <h3 className="text-h3">AI Explanation</h3>
            </div>
            <p className="text-muted" style={{ lineHeight: 1.6 }}>
              {selectedFeature} is a highly significant indicator. In our tests, lower {selectedFeature} values strongly correlate with the "Spoiled" classification.
            </p>
          </motion.div>

          {/* Correlation Network Placeholder */}
          <div className="glass-card flex items-center justify-center bg-gradient-dark" style={{ height: '100%', minHeight: '150px', color: 'white', opacity: 0.9 }}>
            <div className="flex flex-col items-center gap-2">
              <Share2 size={32} className="text-primary-orange" />
              <p>Correlation Network Graph</p>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

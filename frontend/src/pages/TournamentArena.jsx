import { useState } from 'react';
import { motion } from 'framer-motion';
import { Filter, Trophy, Medal } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from 'recharts';

const leaderboardData = [
  { rank: 1, model: 'Linear Discriminant Analysis', preprocessing: 'Raw', accuracy: 78.05, f1: 77.8, r2: '-', rmse: '-', track: 'Classification' },
  { rank: 2, model: 'Random Forest', preprocessing: 'Raw', accuracy: 77.32, f1: 76.5, r2: '-', rmse: '-', track: 'Classification' },
  { rank: 3, model: 'Support Vector Machine', preprocessing: 'Raw', accuracy: 76.83, f1: 76.1, r2: '-', rmse: '-', track: 'Classification' },
  { rank: 4, model: 'Gradient Boosting', preprocessing: 'Advanced', accuracy: 75.12, f1: 74.9, r2: '-', rmse: '-', track: 'Classification' },
  { rank: 5, model: 'Logistic Regression', preprocessing: 'Raw', accuracy: 74.39, f1: 74.1, r2: '-', rmse: '-', track: 'Classification' }
];

const chartData = leaderboardData.map(d => ({
  name: d.model,
  Accuracy: d.accuracy
})).reverse();

export default function TournamentArena() {
  const [track, setTrack] = useState('Classification');

  return (
    <div className="flex flex-col gap-8" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div className="flex justify-between items-center">
        <h1 className="text-h1">Tournament Arena</h1>
      </div>

      {/* Filter Bar */}
      <section className="glass-card flex items-center gap-4" style={{ display: 'flex', gap: '1rem' }}>
        <Filter size={20} className="text-muted" />
        <select 
          className="btn btn-outline" 
          value={track} 
          onChange={(e) => setTrack(e.target.value)}
          style={{ padding: '0.5rem 1rem' }}
        >
          <option value="Classification">Classification Track</option>
          <option value="Regression">Regression Track</option>
        </select>
        <select className="btn btn-outline" style={{ padding: '0.5rem 1rem' }}>
          <option>All Preprocessing</option>
          <option>Raw Data</option>
          <option>Advanced</option>
          <option>Engineered</option>
        </select>
        <select className="btn btn-outline" style={{ padding: '0.5rem 1rem' }}>
          <option>All Models</option>
          <option>Ensemble</option>
          <option>Linear</option>
        </select>
      </section>

      {/* Podium Winners */}
      <section style={{ display: 'flex', justifyContent: 'center', alignItems: 'flex-end', height: '280px', gap: '1rem', marginTop: '2rem' }}>
        {/* Silver */}
        <motion.div 
          className="glass-card"
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: '200px', opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          style={{ width: '200px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'flex-start', background: 'linear-gradient(to top, #E0E0E0 0%, transparent 100%)', border: '1px solid #BDBDBD', position: 'relative' }}
        >
          <div style={{ position: 'absolute', top: '-25px', background: '#E0E0E0', borderRadius: '50%', padding: '0.5rem', border: '2px solid white' }}><Medal size={24} color="white" /></div>
          <h3 className="text-h3 mt-6" style={{ marginTop: '2rem', textAlign: 'center' }}>Random Forest</h3>
          <p className="text-h2 mt-2" style={{ color: '#757575' }}>77.32%</p>
          <p className="text-muted text-sm">Silver</p>
        </motion.div>

        {/* Gold */}
        <motion.div 
          className="glass-card"
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: '260px', opacity: 1 }}
          transition={{ duration: 0.6 }}
          style={{ width: '220px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'flex-start', background: 'linear-gradient(to top, #FFD700 0%, transparent 100%)', border: '1px solid #FDB931', position: 'relative', zIndex: 10 }}
        >
           <div style={{ position: 'absolute', top: '-35px', background: '#FFD700', borderRadius: '50%', padding: '1rem', border: '3px solid white', boxShadow: '0 4px 10px rgba(255, 215, 0, 0.5)' }}><Trophy size={32} color="white" /></div>
          <h3 className="text-h3 mt-8" style={{ marginTop: '3rem', textAlign: 'center' }}>LDA</h3>
          <p className="text-h1 mt-2" style={{ color: '#B8860B' }}>78.05%</p>
          <p className="text-muted text-sm">Gold</p>
        </motion.div>

        {/* Bronze */}
        <motion.div 
          className="glass-card"
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: '160px', opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          style={{ width: '200px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'flex-start', background: 'linear-gradient(to top, #CD7F32 0%, transparent 100%)', border: '1px solid #A0522D', position: 'relative' }}
        >
          <div style={{ position: 'absolute', top: '-25px', background: '#CD7F32', borderRadius: '50%', padding: '0.5rem', border: '2px solid white' }}><Medal size={24} color="white" /></div>
          <h3 className="text-h3 mt-6" style={{ marginTop: '2rem', textAlign: 'center' }}>SVM</h3>
          <p className="text-h2 mt-2" style={{ color: '#8B4513' }}>76.83%</p>
          <p className="text-muted text-sm">Bronze</p>
        </motion.div>
      </section>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2rem', marginTop: '2rem' }}>
        {/* Leaderboard Table */}
        <section className="glass-card">
          <h2 className="text-h3 mb-4">Official Rankings</h2>
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Model</th>
                  <th>Preprocessing</th>
                  <th>Accuracy</th>
                  <th>F1 Score</th>
                </tr>
              </thead>
              <tbody>
                {leaderboardData.map((row) => (
                  <tr key={row.rank}>
                    <td style={{ fontWeight: 'bold', color: row.rank === 1 ? '#FFD700' : row.rank === 2 ? '#BDBDBD' : row.rank === 3 ? '#CD7F32' : 'var(--text-secondary)' }}>#{row.rank}</td>
                    <td style={{ fontWeight: 500 }}>{row.model}</td>
                    <td><span className="status-badge" style={{ backgroundColor: 'var(--light-bg)', color: 'var(--text-secondary)' }}>{row.preprocessing}</span></td>
                    <td style={{ fontWeight: 'bold', color: row.rank === 1 ? 'var(--primary-orange)' : 'inherit' }}>{row.accuracy}%</td>
                    <td>{row.f1}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Performance Chart */}
        <section className="glass-card">
          <h2 className="text-h3 mb-4">Performance Gap</h2>
          <div style={{ height: '300px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} layout="vertical" margin={{ left: 80 }}>
                <XAxis type="number" domain={[70, 80]} hide />
                <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: 'var(--text-secondary)' }} />
                <Tooltip cursor={{ fill: 'transparent' }} contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: 'var(--shadow-md)' }} />
                <Bar dataKey="Accuracy" radius={[0, 4, 4, 0]}>
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={index === chartData.length - 1 ? 'var(--primary-orange)' : 'var(--border-color)'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>
      </div>
    </div>
  );
}

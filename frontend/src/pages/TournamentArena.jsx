import { useState } from 'react';
import { motion } from 'framer-motion';
import { Filter, Trophy, Medal } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from 'recharts';

const classificationLeaderboard = [
  { rank: 1, model: 'Linear Discriminant Analysis', preprocessing: 'Raw', accuracy: 78.05, f1: 77.8, type: 'Linear' },
  { rank: 2, model: 'Random Forest', preprocessing: 'Raw', accuracy: 77.32, f1: 76.5, type: 'Ensemble' },
  { rank: 3, model: 'Support Vector Machine', preprocessing: 'Raw', accuracy: 76.83, f1: 76.1, type: 'Kernel' },
  { rank: 4, model: 'Gradient Boosting', preprocessing: 'Advanced', accuracy: 75.12, f1: 74.9, type: 'Ensemble' },
  { rank: 5, model: 'Logistic Regression', preprocessing: 'Raw', accuracy: 74.39, f1: 74.1, type: 'Linear' }
];

const regressionLeaderboard = [
  { rank: 1, model: 'Random Forest Regressor', preprocessing: 'Advanced', r2: 0.89, rmse: 1.15, type: 'Ensemble' },
  { rank: 2, model: 'Support Vector Regressor', preprocessing: 'Raw', r2: 0.84, rmse: 1.38, type: 'Kernel' },
  { rank: 3, model: 'Gradient Boosting Regressor', preprocessing: 'Advanced', r2: 0.81, rmse: 1.52, type: 'Ensemble' },
  { rank: 4, model: 'Linear Regression', preprocessing: 'Raw', r2: 0.73, rmse: 1.95, type: 'Linear' },
  { rank: 5, model: 'Decision Tree Regressor', preprocessing: 'Engineered', r2: 0.69, rmse: 2.12, type: 'Tree' }
];

export default function TournamentArena() {
  const [track, setTrack] = useState('Classification');
  const [preprocessingFilter, setPreprocessingFilter] = useState('All');
  const [modelTypeFilter, setModelTypeFilter] = useState('All');

  // Select base leaderboard list
  const baseData = track === 'Classification' ? classificationLeaderboard : regressionLeaderboard;

  // Filter list
  const filteredData = baseData.filter(d => {
    const matchesPrep = preprocessingFilter === 'All' || 
      (preprocessingFilter === 'Raw' && d.preprocessing === 'Raw') ||
      (preprocessingFilter === 'Advanced' && d.preprocessing === 'Advanced') ||
      (preprocessingFilter === 'Engineered' && d.preprocessing === 'Engineered');
      
    const matchesType = modelTypeFilter === 'All' ||
      (modelTypeFilter === 'Ensemble' && d.type === 'Ensemble') ||
      (modelTypeFilter === 'Linear' && (d.type === 'Linear' || d.type === 'Kernel'));

    return matchesPrep && matchesType;
  });

  // Re-rank items after filtering
  const rankedData = filteredData.map((d, index) => ({
    ...d,
    currentRank: index + 1
  }));

  // Identify podium ranks
  const goldWinner = rankedData[0] || null;
  const silverWinner = rankedData[1] || null;
  const bronzeWinner = rankedData[2] || null;

  // Prepare chart data
  const chartData = rankedData.map(d => ({
    name: d.model,
    Val: track === 'Classification' ? d.accuracy : d.r2
  })).reverse();

  return (
    <div className="flex flex-col gap-8" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div className="flex justify-between items-center">
        <h1 className="text-h1">Tournament Arena</h1>
      </div>

      {/* Filter Bar */}
      <section className="glass-card flex items-center gap-4" style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
        <Filter size={20} className="text-muted" />
        
        <div>
          <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.25rem', fontWeight: 500 }}>Target Track</label>
          <select 
            className="btn btn-outline" 
            value={track} 
            onChange={(e) => {
              setTrack(e.target.value);
              setPreprocessingFilter('All');
              setModelTypeFilter('All');
            }}
            style={{ padding: '0.4rem 0.75rem', outline: 'none' }}
          >
            <option value="Classification">Classification Track</option>
            <option value="Regression">Regression Track</option>
          </select>
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.25rem', fontWeight: 500 }}>Preprocessing</label>
          <select 
            className="btn btn-outline" 
            value={preprocessingFilter}
            onChange={(e) => setPreprocessingFilter(e.target.value)}
            style={{ padding: '0.4rem 0.75rem', outline: 'none' }}
          >
            <option value="All">All Preprocessing</option>
            <option value="Raw">Raw Data Only</option>
            <option value="Advanced">Advanced Only</option>
            <option value="Engineered">Engineered Only</option>
          </select>
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.25rem', fontWeight: 500 }}>Model Class</label>
          <select 
            className="btn btn-outline" 
            value={modelTypeFilter}
            onChange={(e) => setModelTypeFilter(e.target.value)}
            style={{ padding: '0.4rem 0.75rem', outline: 'none' }}
          >
            <option value="All">All Models</option>
            <option value="Ensemble">Ensemble Models</option>
            <option value="Linear">Linear & Kernel Models</option>
          </select>
        </div>
      </section>

      {/* Podium Winners */}
      <section style={{ display: 'flex', justifyContent: 'center', alignItems: 'flex-end', height: '280px', gap: '1rem', marginTop: '2rem' }}>
        {/* Silver (Rank 2) */}
        {silverWinner ? (
          <motion.div 
            className="glass-card"
            key={`silver-${silverWinner.model}`}
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: '200px', opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.15 }}
            style={{ width: '200px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'flex-start', background: 'linear-gradient(to top, #E0E0E0 0%, transparent 100%)', border: '1px solid #BDBDBD', position: 'relative' }}
          >
            <div style={{ position: 'absolute', top: '-25px', background: '#E0E0E0', borderRadius: '50%', padding: '0.5rem', border: '2px solid white' }}><Medal size={24} color="white" /></div>
            <h3 className="text-h3 mt-6" style={{ marginTop: '2rem', textAlign: 'center', fontSize: '0.9375rem' }}>{silverWinner.model}</h3>
            <p className="text-h2 mt-2" style={{ color: '#757575' }}>
              {track === 'Classification' ? `${silverWinner.accuracy}%` : `R²: ${silverWinner.r2}`}
            </p>
            <p className="text-muted text-sm">Silver (Rank #2)</p>
          </motion.div>
        ) : (
          <div style={{ width: '200px', height: '140px', border: '2px dashed var(--border-color)', borderRadius: 'var(--radius-md)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
            No Silver Contender
          </div>
        )}

        {/* Gold (Rank 1) */}
        {goldWinner ? (
          <motion.div 
            className="glass-card"
            key={`gold-${goldWinner.model}`}
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: '260px', opacity: 1 }}
            transition={{ duration: 0.6 }}
            style={{ width: '220px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'flex-start', background: 'linear-gradient(to top, #FFD700 0%, transparent 100%)', border: '1px solid #FDB931', position: 'relative', zIndex: 10 }}
          >
            <div style={{ position: 'absolute', top: '-35px', background: '#FFD700', borderRadius: '50%', padding: '1rem', border: '3px solid white', boxShadow: '0 4px 10px rgba(255, 215, 0, 0.5)' }}><Trophy size={32} color="white" /></div>
            <h3 className="text-h3 mt-8" style={{ marginTop: '3rem', textAlign: 'center', fontSize: '1rem' }}>{goldWinner.model}</h3>
            <p className="text-h1 mt-2" style={{ color: '#B8860B' }}>
              {track === 'Classification' ? `${goldWinner.accuracy}%` : `R²: ${goldWinner.r2}`}
            </p>
            <p className="text-muted text-sm">Gold (Winner)</p>
          </motion.div>
        ) : (
          <div style={{ width: '220px', height: '180px', border: '2px dashed var(--border-color)', borderRadius: 'var(--radius-md)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
            No Gold Contender
          </div>
        )}

        {/* Bronze (Rank 3) */}
        {bronzeWinner ? (
          <motion.div 
            className="glass-card"
            key={`bronze-${bronzeWinner.model}`}
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: '160px', opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            style={{ width: '200px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'flex-start', background: 'linear-gradient(to top, #CD7F32 0%, transparent 100%)', border: '1px solid #A0522D', position: 'relative' }}
          >
            <div style={{ position: 'absolute', top: '-25px', background: '#CD7F32', borderRadius: '50%', padding: '0.5rem', border: '2px solid white' }}><Medal size={24} color="white" /></div>
            <h3 className="text-h3 mt-6" style={{ marginTop: '2rem', textAlign: 'center', fontSize: '0.9375rem' }}>{bronzeWinner.model}</h3>
            <p className="text-h2 mt-2" style={{ color: '#8B4513' }}>
              {track === 'Classification' ? `${bronzeWinner.accuracy}%` : `R²: ${bronzeWinner.r2}`}
            </p>
            <p className="text-muted text-sm">Bronze (Rank #3)</p>
          </motion.div>
        ) : (
          <div style={{ width: '200px', height: '120px', border: '2px dashed var(--border-color)', borderRadius: 'var(--radius-md)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
            No Bronze Contender
          </div>
        )}
      </section>

      <div style={{ display: 'grid', gridTemplateColumns: '1.8fr 1.2fr', gap: '2rem', marginTop: '2rem' }}>
        {/* Leaderboard Table */}
        <section className="glass-card">
          <h2 className="text-h3 mb-4">Official Rankings ({rankedData.length} Models matched)</h2>
          <div className="table-container">
            <table className="data-table">
              <thead>
                {track === 'Classification' ? (
                  <tr>
                    <th>Rank</th>
                    <th>Model</th>
                    <th>Preprocessing</th>
                    <th>Accuracy</th>
                    <th>F1 Score</th>
                  </tr>
                ) : (
                  <tr>
                    <th>Rank</th>
                    <th>Model</th>
                    <th>Preprocessing</th>
                    <th>R² Score</th>
                    <th>RMSE (Days)</th>
                  </tr>
                )}
              </thead>
              <tbody>
                {rankedData.length > 0 ? (
                  rankedData.map((row) => (
                    <tr key={row.model}>
                      <td style={{ fontWeight: 'bold', color: row.currentRank === 1 ? '#FFD700' : row.currentRank === 2 ? '#BDBDBD' : row.currentRank === 3 ? '#CD7F32' : 'var(--text-secondary)' }}>
                        #{row.currentRank}
                      </td>
                      <td style={{ fontWeight: 500 }}>{row.model}</td>
                      <td>
                        <span className="status-badge" style={{ backgroundColor: 'var(--light-bg)', color: 'var(--text-secondary)', fontSize: '0.75rem' }}>
                          {row.preprocessing}
                        </span>
                      </td>
                      {track === 'Classification' ? (
                        <>
                          <td style={{ fontWeight: 'bold', color: row.currentRank === 1 ? 'var(--primary-orange)' : 'inherit' }}>{row.accuracy}%</td>
                          <td>{row.f1}%</td>
                        </>
                      ) : (
                        <>
                          <td style={{ fontWeight: 'bold', color: row.currentRank === 1 ? 'var(--primary-orange)' : 'inherit' }}>{row.r2}</td>
                          <td>{row.rmse} Days</td>
                        </>
                      )}
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={5} style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-secondary)' }}>
                      No models match the selected filter combination.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>

        {/* Performance Chart */}
        <section className="glass-card">
          <h2 className="text-h3 mb-4">Performance Gap ({track === 'Classification' ? 'Accuracy' : 'R² Score'})</h2>
          <div style={{ height: '300px' }}>
            {chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} layout="vertical" margin={{ left: 100, right: 10 }}>
                  <XAxis 
                    type="number" 
                    domain={track === 'Classification' ? [65, 90] : [0.6, 0.95]} 
                    hide 
                  />
                  <YAxis 
                    dataKey="name" 
                    type="category" 
                    axisLine={false} 
                    tickLine={false} 
                    tick={{ fontSize: 10, fill: 'var(--text-secondary)' }} 
                  />
                  <Tooltip cursor={{ fill: 'transparent' }} contentStyle={{ borderRadius: '8px', border: '1px solid var(--border-color)', boxShadow: 'var(--shadow-md)' }} />
                  <Bar dataKey="Val" radius={[0, 4, 4, 0]}>
                    {chartData.map((entry, index) => (
                      <Cell 
                        key={`cell-${index}`} 
                        fill={index === chartData.length - 1 ? 'var(--primary-orange)' : 'var(--border-color)'} 
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px dashed var(--border-color)', borderRadius: 'var(--radius-md)', color: 'var(--text-secondary)' }}>
                No active performance gap.
              </div>
            )}
          </div>
        </section>
      </div>
    </div>
  );
}

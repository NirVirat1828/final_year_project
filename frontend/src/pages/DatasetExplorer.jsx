import { motion } from 'framer-motion';
import { Search, Filter } from 'lucide-react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const summaryStats = [
  { label: 'Total Samples', value: '1,248' },
  { label: 'Total Features', value: '11' },
  { label: 'Fresh Class Count', value: '412' },
  { label: 'Mid Class Count', value: '430' },
  { label: 'Spoiled Class Count', value: '406' }
];

const mockData = [
  { id: 1, folicAcid: 12.4, vitC: 45.2, pH: 3.2, moisture: 88.5, class: 'Fresh' },
  { id: 2, folicAcid: 10.1, vitC: 38.4, pH: 3.5, moisture: 82.1, class: 'Mid' },
  { id: 3, folicAcid: 5.2, vitC: 15.6, pH: 4.1, moisture: 65.3, class: 'Spoiled' },
  { id: 4, folicAcid: 11.8, vitC: 42.1, pH: 3.3, moisture: 86.2, class: 'Fresh' },
  { id: 5, folicAcid: 8.9, vitC: 29.5, pH: 3.8, moisture: 75.8, class: 'Mid' },
];

const classDistData = [
  { name: 'Fresh', value: 412 },
  { name: 'Mid', value: 430 },
  { name: 'Spoiled', value: 406 }
];
const COLORS = ['#2ECC71', '#F59E0B', '#EF4444'];

const featureDistData = [
  { range: '0-5', count: 45 },
  { range: '6-10', count: 120 },
  { range: '11-15', count: 210 },
  { range: '16-20', count: 85 }
];

export default function DatasetExplorer() {
  return (
    <div className="flex flex-col gap-8" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div className="flex justify-between items-center">
        <h1 className="text-h1">Dataset Explorer</h1>
        <button className="btn btn-outline"><Filter size={16} /> Filters</button>
      </div>

      {/* Summary Cards */}
      <section className="grid-cols-5" style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '1rem' }}>
        {summaryStats.map((stat, idx) => (
          <motion.div 
            key={idx} 
            className="glass-card"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
            style={{ textAlign: 'center', padding: '1rem' }}
          >
            <p className="text-h2" style={{ color: 'var(--primary-orange)' }}>{stat.value}</p>
            <p className="text-muted" style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{stat.label}</p>
          </motion.div>
        ))}
      </section>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2rem' }}>
        {/* Interactive Dataset Table */}
        <section className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div className="flex justify-between items-center">
            <h2 className="text-h3">Data Samples</h2>
            <div style={{ position: 'relative' }}>
              <Search size={16} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)' }} />
              <input 
                type="text" 
                placeholder="Search..." 
                style={{ padding: '0.5rem 1rem 0.5rem 2.5rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', outline: 'none' }}
              />
            </div>
          </div>
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Sample ID</th>
                  <th>Folic Acid (mg)</th>
                  <th>Vitamin C (mg)</th>
                  <th>pH Level</th>
                  <th>Moisture (%)</th>
                  <th>Class</th>
                </tr>
              </thead>
              <tbody>
                {mockData.map((row) => (
                  <tr key={row.id}>
                    <td>#{row.id}</td>
                    <td>{row.folicAcid}</td>
                    <td>{row.vitC}</td>
                    <td>{row.pH}</td>
                    <td>{row.moisture}</td>
                    <td>
                      <span className="status-badge" style={{ backgroundColor: row.class === 'Fresh' ? 'rgba(46, 204, 113, 0.1)' : row.class === 'Mid' ? 'rgba(245, 158, 11, 0.1)' : 'rgba(239, 68, 68, 0.1)', color: row.class === 'Fresh' ? '#2ECC71' : row.class === 'Mid' ? '#F59E0B' : '#EF4444' }}>
                        {row.class}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Statistics Panel */}
        <section className="glass-card flex flex-col gap-4">
          <h2 className="text-h3">Feature Inspector</h2>
          <div className="mb-4">
            <label className="text-muted mb-2" style={{ display: 'block', fontSize: '0.875rem' }}>Select Feature</label>
            <select style={{ width: '100%', padding: '0.5rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', outline: 'none' }}>
              <option>Folic Acid</option>
              <option>Vitamin C</option>
              <option>pH Level</option>
              <option>Moisture</option>
            </select>
          </div>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div style={{ padding: '1rem', backgroundColor: 'var(--light-bg)', borderRadius: 'var(--radius-sm)' }}>
              <p className="text-muted" style={{ fontSize: '0.75rem' }}>Mean</p>
              <p className="text-h3">9.68</p>
            </div>
            <div style={{ padding: '1rem', backgroundColor: 'var(--light-bg)', borderRadius: 'var(--radius-sm)' }}>
              <p className="text-muted" style={{ fontSize: '0.75rem' }}>Std Dev</p>
              <p className="text-h3">2.45</p>
            </div>
            <div style={{ padding: '1rem', backgroundColor: 'var(--light-bg)', borderRadius: 'var(--radius-sm)' }}>
              <p className="text-muted" style={{ fontSize: '0.75rem' }}>Variance</p>
              <p className="text-h3">6.02</p>
            </div>
            <div style={{ padding: '1rem', backgroundColor: 'var(--light-bg)', borderRadius: 'var(--radius-sm)' }}>
              <p className="text-muted" style={{ fontSize: '0.75rem' }}>Missing</p>
              <p className="text-h3">0</p>
            </div>
          </div>
        </section>
      </div>

      {/* Visual Analytics */}
      <section className="grid-cols-2">
        <motion.div className="glass-card" initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }}>
          <h2 className="text-h3 mb-4">Class Distribution</h2>
          <div style={{ height: '300px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={classDistData} cx="50%" cy="50%" innerRadius={80} outerRadius={110} paddingAngle={5} dataKey="value">
                  {classDistData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
        
        <motion.div className="glass-card" initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }}>
          <h2 className="text-h3 mb-4">Feature Histogram (Folic Acid)</h2>
          <div style={{ height: '300px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={featureDistData}>
                <XAxis dataKey="range" stroke="var(--text-secondary)" />
                <YAxis stroke="var(--text-secondary)" />
                <Tooltip cursor={{ fill: 'transparent' }} contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: 'var(--shadow-md)' }} />
                <Bar dataKey="count" fill="var(--primary-orange)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      </section>
    </div>
  );
}

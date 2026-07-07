import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Search, Filter, Loader2 } from 'lucide-react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { getDataset } from '../api/dataApi';
import ErrorCard from '../components/ui/ErrorCard';

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
  const [data, setData] = useState([]);
  const [totalRecords, setTotalRecords] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const [selectedFeature, setSelectedFeature] = useState('Peak_0.85V');

  useEffect(() => {
    let mounted = true;
    const fetchRealDataset = async () => {
      try {
        const response = await getDataset(1, 100);
        if (mounted) {
          setData(response.data);
          setTotalRecords(response.total_records);
          setIsLoading(false);
        }
      } catch (err) {
        if (mounted) {
          setError(err.message);
          setIsLoading(false);
        }
      }
    };
    fetchRealDataset();
    return () => { mounted = false; };
  }, []);

  // Update summary stats based on real dataset size
  const summaryStats = [
    { label: 'Total Samples', value: totalRecords > 0 ? totalRecords.toLocaleString() : '-' },
    { label: 'Total Features', value: '11' },
    { label: 'Batches Count', value: '12' }, // Static approximation
    { label: 'Hardware', value: 'E-Tongue' },
    { label: 'Storage Temp', value: '4°C / 20°C' }
  ];

  // Dynamic feature inspector calculations
  let fMean = 0, fStdDev = 0, fVariance = 0, fMissing = 0;
  if (data.length > 0) {
    const validVals = data.map(d => Number(d[selectedFeature])).filter(v => !isNaN(v));
    fMissing = data.length - validVals.length;
    if (validVals.length > 0) {
      fMean = validVals.reduce((a, b) => a + b, 0) / validVals.length;
      fVariance = validVals.reduce((a, b) => a + Math.pow(b - fMean, 2), 0) / validVals.length;
      fStdDev = Math.sqrt(fVariance);
    }
  }

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
            {isLoading ? (
              <div className="flex flex-col items-center justify-center p-8 text-muted">
                <Loader2 className="animate-spin mb-4" size={32} />
                <p>Loading dataset from backend...</p>
              </div>
            ) : error ? (
              <ErrorCard message={error} />
            ) : (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Row ID</th>
                    <th>Peak Voltage (V)</th>
                    <th>Energy</th>
                    <th>Mean</th>
                    <th>DCT_1</th>
                    <th>Age (Days)</th>
                    <th>Folic Acid (uM)</th>
                  </tr>
                </thead>
                <tbody>
                  {data.slice(0, 50).map((row, idx) => (
                    <tr key={idx}>
                      <td>#{idx + 1}</td>
                      <td>{Number(row['Peak_0.85V']).toFixed(4)}</td>
                      <td>{Number(row['Energy']).toFixed(4)}</td>
                      <td>{Number(row['Mean']).toFixed(4)}</td>
                      <td>{Number(row['DCT_1']).toFixed(4)}</td>
                      <td>
                        <span className="status-badge" style={{ backgroundColor: 'rgba(241, 196, 15, 0.1)', color: '#F1C40F' }}>
                          {Number(row['day']).toFixed(1)} days
                        </span>
                      </td>
                      <td>{Number(row['true_conc_uM']).toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </section>

        {/* Statistics Panel */}
        <section className="glass-card flex flex-col gap-4">
          <h2 className="text-h3">Feature Inspector</h2>
          <div className="mb-4">
            <label className="text-muted mb-2" style={{ display: 'block', fontSize: '0.875rem' }}>Select Feature</label>
            <select 
              value={selectedFeature}
              onChange={(e) => setSelectedFeature(e.target.value)}
              style={{ width: '100%', padding: '0.5rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', outline: 'none' }}
            >
              <option value="Peak_0.85V">Peak Voltage (0.85V)</option>
              <option value="Energy">Signal Energy</option>
              <option value="Mean">Mean Current</option>
              <option value="Std_Dev">Standard Deviation</option>
              <option value="Skewness">Skewness</option>
              <option value="Kurtosis">Kurtosis</option>
              <option value="DCT_1">DCT Coefficient 1</option>
            </select>
          </div>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div style={{ padding: '1rem', backgroundColor: 'var(--light-bg)', borderRadius: 'var(--radius-sm)' }}>
              <p className="text-muted" style={{ fontSize: '0.75rem' }}>Mean</p>
              <p className="text-h3">{fMean.toFixed(4)}</p>
            </div>
            <div style={{ padding: '1rem', backgroundColor: 'var(--light-bg)', borderRadius: 'var(--radius-sm)' }}>
              <p className="text-muted" style={{ fontSize: '0.75rem' }}>Std Dev</p>
              <p className="text-h3">{fStdDev.toFixed(4)}</p>
            </div>
            <div style={{ padding: '1rem', backgroundColor: 'var(--light-bg)', borderRadius: 'var(--radius-sm)' }}>
              <p className="text-muted" style={{ fontSize: '0.75rem' }}>Variance</p>
              <p className="text-h3">{fVariance.toFixed(4)}</p>
            </div>
            <div style={{ padding: '1rem', backgroundColor: 'var(--light-bg)', borderRadius: 'var(--radius-sm)' }}>
              <p className="text-muted" style={{ fontSize: '0.75rem' }}>Missing</p>
              <p className="text-h3">{fMissing}</p>
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

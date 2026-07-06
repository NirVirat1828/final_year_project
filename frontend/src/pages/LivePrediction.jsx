import { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { 
  Upload, 
  Play, 
  AlertCircle, 
  Clock, 
  Activity, 
  FileText, 
  Download, 
  Trash2, 
  CheckCircle, 
  Search, 
  Thermometer,
  Settings,
  RefreshCw
} from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from 'recharts';
import { analyzeCsvBatch } from '../api/inferenceApi';

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

export default function LivePrediction() {
  const [method, setMethod] = useState('manual');
  const [isPredicting, setIsPredicting] = useState(false);
  const [result, setResult] = useState(null);

  // CSV upload state
  const [selectedFile, setSelectedFile] = useState(null);
  const [preprocessingStrategy, setPreprocessingStrategy] = useState('raw');
  const [storageTemperature, setStorageTemperature] = useState(4.0);
  const [dragActive, setDragActive] = useState(false);
  const [csvResults, setCsvResults] = useState(null);
  const [csvSummary, setCsvSummary] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  // Filters state
  const [searchQuery, setSearchQuery] = useState('');
  const [gradeFilter, setGradeFilter] = useState('All');

  // Manual input values
  const [manualInputs, setManualInputs] = useState(
    sensors.reduce((acc, sensor) => ({ ...acc, [sensor.id]: '' }), {})
  );

  const handleManualInputChange = (id, val) => {
    setManualInputs(prev => ({ ...prev, [id]: val }));
  };

  const handlePredict = () => {
    setIsPredicting(true);
    // Simulate manual prediction for e-tongue features or mock
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

  // CSV Drag and Drop Handlers
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.name.endsWith('.csv')) {
        setSelectedFile(file);
        setError(null);
      } else {
        setError("Invalid file format. Please upload a .csv file.");
      }
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (file.name.endsWith('.csv')) {
        setSelectedFile(file);
        setError(null);
      } else {
        setError("Invalid file format. Please upload a .csv file.");
      }
    }
  };

  const handleCsvPredict = async () => {
    if (!selectedFile) return;
    setIsPredicting(true);
    setError(null);
    try {
      const response = await analyzeCsvBatch(selectedFile, preprocessingStrategy, storageTemperature);
      setCsvResults(response.predictions);
      setCsvSummary(response);
    } catch (err) {
      console.error(err);
      setError(err instanceof Error ? err.message : "Failed to analyze batch.");
    } finally {
      setIsPredicting(false);
    }
  };

  const clearFile = () => {
    setSelectedFile(null);
    setCsvResults(null);
    setCsvSummary(null);
    setError(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  // Compute stats for CSV results
  const counts = { A: 0, B: 0, C: 0, D: 0 };
  let avgAge = 0;
  let avgShelf = 0;
  let avgFolic = 0;
  let healthScore = 0;

  if (csvResults && csvResults.length > 0) {
    csvResults.forEach(r => {
      const grade = r.results.freshness_grade;
      if (counts[grade] !== undefined) {
        counts[grade]++;
      }
    });

    avgAge = csvResults.reduce((sum, r) => sum + r.logistics.estimated_age_days, 0) / csvResults.length;
    avgShelf = csvResults.reduce((sum, r) => sum + r.logistics.remaining_shelf_life_days, 0) / csvResults.length;
    avgFolic = csvResults.reduce((sum, r) => sum + r.results.folic_acid_uM, 0) / csvResults.length;
    healthScore = ((counts.A + counts.B) / csvResults.length) * 100;
  }

  const chartData = [
    { name: 'Grade A', count: counts.A, fill: '#2ECC71', description: 'Premium' },
    { name: 'Grade B', count: counts.B, fill: '#3498DB', description: 'Good' },
    { name: 'Grade C', count: counts.C, fill: '#FF8C42', description: 'Fair' },
    { name: 'Grade D', count: counts.D, fill: '#E74C3C', description: 'Reject' },
  ];

  // Filtering results
  const filteredResults = csvResults ? csvResults.filter(sample => {
    const matchesSearch = sample.sample_index.toString().includes(searchQuery) ||
                          sample.results.freshness_grade.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesGrade = gradeFilter === 'All' || sample.results.freshness_grade === gradeFilter;
    return matchesSearch && matchesGrade;
  }) : [];

  const handleExportCSV = () => {
    if (!csvResults) return;
    
    const headers = [
      'Sample Index',
      'Freshness Grade',
      'Grade Description',
      'Folic Acid (uM)',
      'Nutritional Status',
      'Estimated Age (Days)',
      'Remaining Shelf Life (Days)',
      'Confidence Score (%)',
      'Lower Bound Shelf Life (Days)',
      'Upper Bound Shelf Life (Days)',
      'Temperature Warning'
    ];
    
    const rows = csvResults.map(sample => [
      sample.sample_index,
      sample.results.freshness_grade,
      `"${sample.results.grade_description}"`,
      sample.results.folic_acid_uM.toFixed(2),
      sample.results.nutritional_status,
      sample.logistics.estimated_age_days.toFixed(1),
      sample.logistics.remaining_shelf_life_days.toFixed(1),
      sample.logistics.confidence_score_percent.toFixed(0),
      sample.logistics.confidence_interval.lower_bound.toFixed(1),
      sample.logistics.confidence_interval.upper_bound.toFixed(1),
      `"${sample.logistics.temperature_warning}"`
    ]);
    
    const csvContent = "data:text/csv;charset=utf-8," 
      + [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
      
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `batch_predictions_${selectedFile?.name.replace('.csv', '') || 'export'}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="flex flex-col gap-8">
      <h1 className="text-h1 flex items-center gap-3">
        <Activity className="text-primary-orange" size={32} /> Live Prediction Engine
      </h1>

      {/* Tabs */}
      <div className="flex justify-between items-center" style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: '1rem' }}>
        <p className="text-muted">Analyze electronic tongue signals to predict storage days, freshness grade, and nutritional status.</p>
        <div style={{ display: 'flex', gap: '0.5rem', background: 'var(--border-color)', padding: '0.25rem', borderRadius: 'var(--radius-md)' }}>
          <button 
            className={`btn whitespace-nowrap ${method === 'manual' ? 'btn-primary' : 'btn-outline'}`}
            style={{ padding: '0.35rem 1.25rem', border: 'none', borderRadius: 'var(--radius-sm)' }}
            onClick={() => setMethod('manual')}
          >
            Manual Input
          </button>
          <button 
            className={`btn whitespace-nowrap ${method === 'csv' ? 'btn-primary' : 'btn-outline'}`}
            style={{ padding: '0.35rem 1.25rem', border: 'none', borderRadius: 'var(--radius-sm)' }}
            onClick={() => setMethod('csv')}
          >
            <Upload size={16} /> CSV Batch Upload
          </button>
        </div>
      </div>

      {method === 'manual' ? (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
          {/* Input Section */}
          <section className="glass-card flex flex-col gap-6">
            <h2 className="text-h2">Input Data</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1rem' }}>
              {sensors.map((sensor) => (
                <div key={sensor.id}>
                  <label className="text-muted mb-2" style={{ display: 'block', fontSize: '0.875rem' }}>{sensor.label}</label>
                  <input 
                    type="number" 
                    placeholder="0.00" 
                    value={manualInputs[sensor.id]}
                    onChange={(e) => handleManualInputChange(sensor.id, e.target.value)}
                    style={{ width: '100%', padding: '0.5rem 1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', outline: 'none' }}
                  />
                </div>
              ))}
            </div>

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
                  <div style={{ width: '120px', height: '120px', borderRadius: '50%', border: '8px solid var(--success-green)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', alignContent: 'center' }}>
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
              </motion.div>
            ) : (
              <div className="glass-card flex items-center justify-center" style={{ height: '100%', minHeight: '400px', flexDirection: 'column', color: 'var(--text-secondary)' }}>
                <Activity size={48} style={{ marginBottom: '1rem', opacity: 0.5 }} />
                <p className="text-h3">Awaiting Data Input</p>
                <p className="text-muted">Fill out the form and run prediction.</p>
              </div>
            )}
          </section>
        </div>
      ) : (
        <div className="flex flex-col gap-6">
          {/* CSV File Upload Setup */}
          {!csvResults ? (
            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2rem' }}>
              <div 
                onDragEnter={handleDrag}
                onDragOver={handleDrag}
                onDragLeave={handleDrag}
                onDrop={handleDrop}
                style={{ 
                  padding: '4rem 2rem', 
                  border: '2px dashed ' + (dragActive ? 'var(--primary-orange)' : 'var(--border-color)'), 
                  borderRadius: 'var(--radius-lg)', 
                  textAlign: 'center',
                  backgroundColor: dragActive ? 'rgba(255, 140, 66, 0.05)' : 'var(--white)',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: 'pointer'
                }}
                onClick={() => fileInputRef.current?.click()}
              >
                <input 
                  type="file" 
                  ref={fileInputRef} 
                  onChange={handleFileChange} 
                  accept=".csv" 
                  style={{ display: 'none' }}
                />
                
                {selectedFile ? (
                  <div className="flex flex-col items-center gap-3">
                    <FileText size={48} className="text-primary-orange" />
                    <p className="text-h3">{selectedFile.name}</p>
                    <p className="text-muted" style={{ fontSize: '0.875rem' }}>
                      {(selectedFile.size / 1024).toFixed(2)} KB
                    </p>
                    <button 
                      className="btn btn-outline" 
                      onClick={(e) => {
                        e.stopPropagation();
                        clearFile();
                      }}
                      style={{ marginTop: '0.5rem', color: 'var(--text-secondary)', padding: '0.25rem 0.75rem' }}
                    >
                      <Trash2 size={14} /> Remove File
                    </button>
                  </div>
                ) : (
                  <>
                    <Upload size={48} style={{ color: 'var(--text-secondary)', marginBottom: '1rem', opacity: 0.7 }} />
                    <p className="text-h3 mb-2">Drag & Drop CSV File</p>
                    <p className="text-muted">or click to browse local files</p>
                    <p className="text-muted" style={{ fontSize: '0.75rem', marginTop: '1rem' }}>
                      Supports e-tongue raw sweeps or engineered features CSV
                    </p>
                  </>
                )}
              </div>

              {/* Upload Parameters Settings */}
              <div className="glass-card flex flex-col gap-6">
                <h3 className="text-h3 flex items-center gap-2" style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: '0.75rem' }}>
                  <Settings size={18} /> Analysis Parameters
                </h3>
                
                <div>
                  <label className="text-muted mb-2" style={{ display: 'flex', fontSize: '0.875rem', fontWeight: 500 }}>
                    Preprocessing Strategy
                  </label>
                  <select 
                    value={preprocessingStrategy} 
                    onChange={(e) => setPreprocessingStrategy(e.target.value)}
                    style={{ width: '100%', padding: '0.5rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', outline: 'none' }}
                  >
                    <option value="raw">Raw Sweep Analysis</option>
                    <option value="advanced">Advanced (Feature Engineering Penalized)</option>
                  </select>
                </div>

                <div>
                  <label className="text-muted mb-2" style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', fontSize: '0.875rem', fontWeight: 500 }}>
                    <Thermometer size={14} /> Storage Temperature (°C)
                  </label>
                  <input 
                    type="number" 
                    value={storageTemperature} 
                    onChange={(e) => setStorageTemperature(parseFloat(e.target.value) || 0)}
                    placeholder="4.0"
                    style={{ width: '100%', padding: '0.5rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', outline: 'none' }}
                  />
                </div>

                {error && (
                  <div style={{ backgroundColor: 'rgba(231, 76, 60, 0.1)', color: '#E74C3C', padding: '0.75rem', borderRadius: 'var(--radius-sm)', fontSize: '0.875rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <AlertCircle size={16} /> {error}
                  </div>
                )}

                <button 
                  className="btn btn-primary w-full"
                  onClick={handleCsvPredict}
                  disabled={!selectedFile || isPredicting}
                  style={{ marginTop: 'auto', padding: '0.75rem' }}
                >
                  {isPredicting ? (
                    <>
                      <RefreshCw size={18} className="animate-spin" />
                      Analyzing Batch...
                    </>
                  ) : (
                    <>
                      <Play size={18} /> Run Batch Analysis
                    </>
                  )}
                </button>
              </div>
            </div>
          ) : (
            /* Results Dashboards and Analytics */
            <div className="flex flex-col gap-6">
              {/* Top Banner Action Panel */}
              <div className="glass-card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem 1.5rem', background: 'linear-gradient(135deg, var(--dark-slate), var(--dark-slate-dark))', color: 'white' }}>
                <div>
                  <h3 className="text-h3" style={{ color: 'white' }}>Batch Analysis Complete</h3>
                  <p style={{ color: 'rgba(255,255,255,0.7)', fontSize: '0.875rem' }}>Processed file: <strong>{selectedFile?.name}</strong></p>
                </div>
                <div className="flex gap-2">
                  <button className="btn btn-outline" onClick={handleExportCSV} style={{ color: 'white', borderColor: 'rgba(255,255,255,0.3)', backgroundColor: 'transparent' }}>
                    <Download size={16} /> Export Results to CSV
                  </button>
                  <button className="btn btn-primary" onClick={clearFile}>
                    <RefreshCw size={16} /> Upload New Batch
                  </button>
                </div>
              </div>

              {/* Summary Stats Grid */}
              <div className="grid-cols-4">
                <div className="glass-card flex flex-col gap-2">
                  <span className="text-muted" style={{ fontSize: '0.875rem' }}>Total Samples</span>
                  <span className="text-h1">{csvSummary?.total_samples}</span>
                  <span className="text-muted" style={{ fontSize: '0.75rem' }}>Measurements analysed</span>
                </div>

                <div className="glass-card flex flex-col gap-2">
                  <span className="text-muted" style={{ fontSize: '0.875rem' }}>Batch Health Score</span>
                  <span className="text-h1" style={{ color: healthScore >= 75 ? 'var(--success-green)' : '#F1C40F' }}>
                    {healthScore.toFixed(1)}%
                  </span>
                  <span className="text-muted" style={{ fontSize: '0.75rem' }}>% graded A or B (Premium/Good)</span>
                </div>

                <div className="glass-card flex flex-col gap-2">
                  <span className="text-muted" style={{ fontSize: '0.875rem' }}>Avg. Remaining Shelf Life</span>
                  <span className="text-h1">{avgShelf.toFixed(1)} Days</span>
                  <span className="text-muted" style={{ fontSize: '0.75rem' }}>Based on storage temp {storageTemperature}°C</span>
                </div>

                <div className="glass-card flex flex-col gap-2">
                  <span className="text-muted" style={{ fontSize: '0.875rem' }}>Avg. Folic Acid</span>
                  <span className="text-h1">{avgFolic.toFixed(1)} µM</span>
                  <span className="text-muted" style={{ fontSize: '0.75rem' }}>Nutritional concentration</span>
                </div>
              </div>

              {/* Chart & Filtering Section */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '2rem' }}>
                {/* Distribution Chart */}
                <div className="glass-card flex flex-col gap-4">
                  <h3 className="text-h3">Grade Distribution</h3>
                  <div style={{ height: '220px', width: '100%', marginTop: '1rem' }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={chartData}>
                        <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                        <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
                        <Tooltip 
                          cursor={{ fill: 'rgba(0,0,0,0.03)' }} 
                          contentStyle={{ borderRadius: '8px', border: '1px solid var(--border-color)' }}
                        />
                        <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                          {chartData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.fill} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Table Data Filtering */}
                <div className="glass-card flex flex-col gap-4">
                  <div className="flex justify-between items-center" style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: '0.75rem' }}>
                    <h3 className="text-h3">Sample Details</h3>
                    
                    <div className="flex gap-2">
                      {/* Search Index */}
                      <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
                        <Search size={14} style={{ position: 'absolute', left: '10px', color: 'var(--text-secondary)' }} />
                        <input 
                          type="text" 
                          placeholder="Search Index/Grade..." 
                          value={searchQuery}
                          onChange={(e) => setSearchQuery(e.target.value)}
                          style={{ padding: '0.35rem 0.75rem 0.35rem 2rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', fontSize: '0.875rem', outline: 'none' }}
                        />
                      </div>
                      
                      {/* Filter Grade */}
                      <select
                        value={gradeFilter}
                        onChange={(e) => setGradeFilter(e.target.value)}
                        style={{ padding: '0.35rem 0.75rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', fontSize: '0.875rem', outline: 'none' }}
                      >
                        <option value="All">All Grades</option>
                        <option value="A">Grade A</option>
                        <option value="B">Grade B</option>
                        <option value="C">Grade C</option>
                        <option value="D">Grade D</option>
                      </select>
                    </div>
                  </div>

                  {/* Scrollable Results Table */}
                  <div className="table-container" style={{ maxHeight: '300px', overflowY: 'auto' }}>
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Sample Index</th>
                          <th>Freshness Grade</th>
                          <th>Storage Age (Days)</th>
                          <th>Remaining Shelf Life</th>
                          <th>Folic Acid</th>
                          <th>Status / Warnings</th>
                        </tr>
                      </thead>
                      <tbody>
                        {filteredResults.length > 0 ? (
                          filteredResults.map((sample) => (
                            <tr key={sample.sample_index}>
                              <td><strong>#{sample.sample_index}</strong></td>
                              <td>
                                <span 
                                  className="status-badge"
                                  style={{
                                    backgroundColor: 
                                      sample.results.freshness_grade === 'A' ? 'rgba(46, 204, 113, 0.15)' :
                                      sample.results.freshness_grade === 'B' ? 'rgba(52, 152, 219, 0.15)' :
                                      sample.results.freshness_grade === 'C' ? 'rgba(255, 140, 66, 0.15)' :
                                      'rgba(231, 76, 60, 0.15)',
                                    color: 
                                      sample.results.freshness_grade === 'A' ? '#2ECC71' :
                                      sample.results.freshness_grade === 'B' ? '#3498DB' :
                                      sample.results.freshness_grade === 'C' ? '#FF8C42' :
                                      '#E74C3C',
                                    fontWeight: 'bold'
                                  }}
                                >
                                  Grade {sample.results.freshness_grade}
                                </span>
                              </td>
                              <td>{sample.logistics.estimated_age_days.toFixed(1)} Days</td>
                              <td>{sample.logistics.remaining_shelf_life_days.toFixed(1)} Days</td>
                              <td>{sample.results.folic_acid_uM.toFixed(1)} µM</td>
                              <td style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={sample.logistics.temperature_warning}>
                                {sample.logistics.temperature_warning}
                              </td>
                            </tr>
                          ))
                        ) : (
                          <tr>
                            <td colSpan={6} style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-secondary)' }}>
                              No matching samples found.
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                  <div className="text-muted" style={{ fontSize: '0.75rem', textAlign: 'right' }}>
                    Showing {filteredResults.length} of {csvResults.length} samples
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

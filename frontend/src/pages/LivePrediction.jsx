import { useState, useRef, useEffect } from 'react';
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
  RefreshCw,
  Cpu,
  StopCircle,
  Wifi,
  WifiOff
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  LineChart,
  Line,
  XAxis, 
  YAxis, 
  Tooltip, 
  Cell, 
  Legend 
} from 'recharts';
import { usePrediction } from '../hooks/usePrediction';
import { explainPrediction, explainPredictionVisualize } from '../api/explainApi';
import InferenceForm from '../components/InferenceForm';
import ResultsDashboard from '../components/ResultsDashboard';
import DecisionDashboard from '../components/decision/DecisionDashboard';
import ErrorCard from '../components/ui/ErrorCard';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import { getDataset } from '../api/dataApi';

const sensors = [
  { id: 'Peak_0.85V', label: 'Peak Voltage (0.85V)' },
  { id: 'Mean', label: 'Mean Current' },
  { id: 'Std_Dev', label: 'Standard Deviation' },
  { id: 'Energy', label: 'Energy' },
  { id: 'Skewness', label: 'Skewness' },
  { id: 'Kurtosis', label: 'Kurtosis' },
  { id: 'DCT_1', label: 'DCT Coefficient 1' },
  { id: 'DCT_2', label: 'DCT Coefficient 2' },
  { id: 'DCT_3', label: 'DCT Coefficient 3' },
  { id: 'DCT_4', label: 'DCT Coefficient 4' },
  { id: 'DCT_5', label: 'DCT Coefficient 5' }
];

export default function LivePrediction() {
  const [method, setMethod] = useState('manual');
  
  const { predict: predictManual, data: manualResult, isLoading: isManualPredicting, error: manualError } = usePrediction();
  const { predict: predictCsv, data: csvResult, isLoading: isCsvPredicting, error: csvError, reset: resetCsv } = usePrediction();

  // CSV upload state
  const [selectedFile, setSelectedFile] = useState(null);
  const [preprocessingStrategy, setPreprocessingStrategy] = useState('raw');
  const [storageTemperature, setStorageTemperature] = useState(4.0);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

  // WebSocket Live Stream state
  const [wsStatus, setWsStatus] = useState('Disconnected');
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamInterval, setStreamInterval] = useState(1000);
  const [wsLog, setWsLog] = useState([]);
  const [wsChartData, setWsChartData] = useState([]);
  const [streamingFile, setStreamingFile] = useState(null);
  const streamFileInputRef = useRef(null);

  // XAI Explanations state
  const [selectedExplanationReadings, setSelectedExplanationReadings] = useState(null);
  const [selectedSampleName, setSelectedSampleName] = useState('');
  const [explainPlotUrl, setExplainPlotUrl] = useState(null);
  const [explainData, setExplainData] = useState(null);
  const [explainModel, setExplainModel] = useState('day');
  const [explainPlotType, setExplainPlotType] = useState('waterfall');
  const [isExplaining, setIsExplaining] = useState(false);

  // Filters state
  const [searchQuery, setSearchQuery] = useState('');
  const [gradeFilter, setGradeFilter] = useState('All');



  const wsRef = useRef(null);
  const timerRef = useRef(null);

  useEffect(() => {
    // Cleanup WebSocket on unmount
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  // Fetch local explanation and SHAP plot image when selection or plot options change
  useEffect(() => {
    if (!selectedExplanationReadings) return;

    const fetchExplanation = async () => {
      setIsExplaining(true);
      try {
        const payload = {
          batch_id: 'xai-local-explain',
          sensor_readings: selectedExplanationReadings,
          preprocessing_strategy: 'raw',
          storage_temperature_c: 4.0
        };

        const explanationText = await explainPrediction(payload);
        setExplainData(explanationText);

        const plotUrl = await explainPredictionVisualize(payload, explainModel, explainPlotType);
        setExplainPlotUrl(prev => {
          if (prev) URL.revokeObjectURL(prev);
          return plotUrl;
        });
      } catch (err) {
        console.error("XAI retrieval failed:", err);
      } finally {
        setIsExplaining(false);
      }
    };

    fetchExplanation();
  }, [selectedExplanationReadings, explainModel, explainPlotType]);

  const handleManualSubmit = async (payload) => {
    try {
      const response = await predictManual(payload, false);
      setSelectedExplanationReadings(payload.sensor_readings);
      setSelectedSampleName(payload.batch_id || "Manual Entry");
    } catch (err) {
      console.error("Manual prediction failed", err);
    }
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
      }
    }
  };

  const handleCsvPredict = async () => {
    if (!selectedFile) return;
    try {
      const response = await predictCsv(selectedFile, true, preprocessingStrategy, storageTemperature);
      if (response?.predictions && response.predictions.length > 0) {
        setSelectedExplanationReadings(response.predictions[0].sensor_readings);
        setSelectedSampleName(`Sample #${response.predictions[0].sample_index}`);
      }
    } catch (err) {
      console.error("Batch analysis failed", err);
    }
  };

  const clearFile = () => {
    setSelectedFile(null);
    resetCsv();
    setSelectedExplanationReadings(null);
    setSelectedSampleName('');
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  // WebSocket Live Streaming methods
  const handleStreamingFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (file.name.endsWith('.csv')) {
        setStreamingFile(file);
        setError(null);
      } else {
        setError("Please select a valid CSV file for streaming.");
      }
    }
  };

  const clearStreamingFile = () => {
    setStreamingFile(null);
    if (streamFileInputRef.current) streamFileInputRef.current.value = '';
  };

  const startStream = () => {
    setError(null);
    
    if (streamingFile) {
      // Parse file rows first
      const reader = new FileReader();
      reader.onload = (event) => {
        const text = event.target.result;
        const lines = text.split('\n').map(l => l.trim()).filter(l => l.length > 0);
        if (lines.length <= 1) {
          setError("CSV file does not contain data rows.");
          return;
        }

        const headers = lines[0].split(',');
        const currentCols = headers.reduce((acc, h, i) => {
          if (h.startsWith('current_')) acc.push(i);
          return acc;
        }, []);

        const engineeredCols = [
          'Peak_0.85V', 'Mean', 'Std_Dev', 'Energy', 'Skewness', 'Kurtosis', 
          'DCT_1', 'DCT_2', 'DCT_3', 'DCT_4', 'DCT_5'
        ].map(colName => headers.indexOf(colName));

        const parsedRows = [];
        for (let i = 1; i < lines.length; i++) {
          const parts = lines[i].split(',');
          if (parts.length < 2) continue;
          
          const numericParts = parts.map(parseFloat);
          if (currentCols.length >= 5) {
            parsedRows.push(currentCols.map(idx => numericParts[idx] || 0.0));
          } else if (engineeredCols.every(idx => idx !== -1)) {
            parsedRows.push(engineeredCols.map(idx => numericParts[idx] || 0.0));
          }
        }
        
        
        initWebSocketConnection(parsedRows);
      };
      reader.readAsText(streamingFile);
    } else {
      // Stream realistic entries by fetching from backend dataset
      getDataset(1, 60).then(response => {
        const rows = response.data.map(row => [
          row['Peak_0.85V'], row.Mean, row.Std_Dev, row.Energy, 
          row.Skewness, row.Kurtosis, row.DCT_1, row.DCT_2, 
          row.DCT_3, row.DCT_4, row.DCT_5
        ].map(val => Number(val) || 0.0));
        
        initWebSocketConnection(rows);
      }).catch(err => {
        setError("Failed to fetch simulated stream data from backend.");
      });
    }
  };

  const initWebSocketConnection = (rows) => {
    setWsStatus('Connecting');
    setWsLog([]);
    setWsChartData([]);

    let wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/api/v1/ws/live-predict`;
    if (window.location.port === '5173') {
      wsUrl = `ws://127.0.0.1:8000/api/v1/ws/live-predict`;
    }

    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setWsStatus('Connected');
        setIsStreaming(true);
        let idx = 0;

        timerRef.current = setInterval(() => {
          if (idx >= rows.length) {
            stopStream();
            return;
          }
          const rowData = rows[idx];
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
              readings: rowData,
              preprocessing_strategy: preprocessingStrategy,
              storage_temperature_c: storageTemperature
            }));
            idx++;
          }
        }, streamInterval);
      };

      ws.onmessage = (event) => {
        const response = JSON.parse(event.data);
        if (response.status === 'success') {
          const newPred = {
            tick: wsChartData.length + 1,
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
            grade: response.results.freshness_grade,
            age: parseFloat(response.logistics.estimated_age_days.toFixed(2)),
            folic: parseFloat(response.results.folic_acid_uM.toFixed(1)),
            shelf: parseFloat(response.logistics.remaining_shelf_life_days.toFixed(1))
          };

          setWsLog(prev => [newPred, ...prev]);
          setWsChartData(prev => {
            const updated = [...prev, newPred];
            if (updated.length > 30) {
              updated.shift();
            }
            return updated;
          });
        } else {
          setError(response.message || "Failed to process streamed measurement.");
        }
      };

      ws.onerror = (err) => {
        console.error("WebSocket error:", err);
        setError("WebSocket connection error.");
        stopStream();
      };

      ws.onclose = () => {
        setWsStatus('Disconnected');
        setIsStreaming(false);
      };
    } catch (e) {
      console.error(e);
      setError("Failed to initialize WebSocket client.");
      setWsStatus('Disconnected');
    }
  };

  const stopStream = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsStreaming(false);
    setWsStatus('Disconnected');
  };

  // Compute stats for CSV results
  const counts = { A: 0, B: 0, C: 0, D: 0 };
  let avgAge = 0;
  let avgShelf = 0;
  let avgFolic = 0;
  let healthScore = 0;

  const csvResults = csvResult?.predictions;

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

  const renderXAIPanel = () => {
    if (!selectedExplanationReadings) return null;

    return (
      <motion.div 
        className="glass-card" 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        style={{ borderTop: '4px solid var(--primary-orange)', marginTop: '1.5rem' }}
      >
        <div className="flex justify-between items-center mb-4" style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: '0.75rem' }}>
          <div>
            <h3 className="text-h3 flex items-center gap-2">
              <Cpu size={18} className="text-primary-orange" />
              AI Decision Explanation: <span style={{ color: 'var(--primary-orange)' }}>{selectedSampleName}</span>
            </h3>
            <p className="text-muted" style={{ fontSize: '0.75rem', marginTop: '0.25rem' }}>
              Local SHAP feature impact contributions detailing exactly why the model made this prediction.
            </p>
          </div>
          <button 
            className="btn btn-outline" 
            onClick={() => {
              setSelectedExplanationReadings(null);
              setSelectedSampleName('');
            }}
            style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
          >
            Clear Explanation
          </button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.2fr', gap: '1.5rem' }}>
          {/* Controls and Stats */}
          <div className="flex flex-col gap-4">
            <div className="flex gap-2">
              <div style={{ flex: 1 }}>
                <label className="text-muted mb-2" style={{ display: 'flex', fontSize: '0.75rem', fontWeight: 500 }}>
                  Target Model
                </label>
                <select
                  value={explainModel}
                  onChange={(e) => setExplainModel(e.target.value)}
                  style={{ width: '100%', padding: '0.4rem 0.5rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', outline: 'none', fontSize: '0.8125rem' }}
                >
                  <option value="day">Storage Age Model (Days)</option>
                  <option value="folic">Nutritional Model (Folic Acid)</option>
                </select>
              </div>

              <div style={{ flex: 1 }}>
                <label className="text-muted mb-2" style={{ display: 'flex', fontSize: '0.75rem', fontWeight: 500 }}>
                  Plot Type
                </label>
                <select
                  value={explainPlotType}
                  onChange={(e) => setExplainPlotType(e.target.value)}
                  style={{ width: '100%', padding: '0.4rem 0.5rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', outline: 'none', fontSize: '0.8125rem' }}
                >
                  <option value="waterfall">Waterfall Plot</option>
                  <option value="bar">Bar Plot</option>
                </select>
              </div>
            </div>

            {/* Top Contributing Features */}
            <div>
              <h4 style={{ fontSize: '0.8125rem', fontWeight: 600, marginBottom: '0.5rem' }}>Top Feature Impact Factors</h4>
              {isExplaining ? (
                <div className="animate-pulse flex flex-col gap-2">
                  <div style={{ height: '24px', backgroundColor: 'var(--border-color)', borderRadius: '4px' }} />
                  <div style={{ height: '24px', backgroundColor: 'var(--border-color)', borderRadius: '4px' }} />
                  <div style={{ height: '24px', backgroundColor: 'var(--border-color)', borderRadius: '4px' }} />
                </div>
              ) : (
                <div className="flex flex-col gap-1.5">
                  {explainData?.explanation?.[`${explainModel}_model`]?.top_features?.map((f, i) => (
                    <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.4rem 0.75rem', backgroundColor: 'var(--light-bg)', borderRadius: 'var(--radius-sm)', fontSize: '0.8125rem', borderLeft: f.impact === 'increase' ? '3px solid var(--success-green)' : f.impact === 'decrease' ? '3px solid var(--primary-orange)' : '3px solid var(--border-color)' }}>
                      <span style={{ fontWeight: 500 }}>{f.rank}. {f.feature_name}</span>
                      <span style={{ 
                        color: f.impact === 'increase' ? 'var(--success-green)' : f.impact === 'decrease' ? 'var(--primary-orange)' : 'var(--text-secondary)',
                        fontWeight: 600 
                      }}>
                        {f.shap_value > 0 ? '+' : ''}{f.shap_value.toFixed(4)}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Plot Visualizer Display */}
          <div className="flex items-center justify-center" style={{ border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)', backgroundColor: '#F8FAFC', minHeight: '200px', padding: '0.5rem', position: 'relative' }}>
            {isExplaining ? (
              <div className="flex flex-col items-center justify-center gap-2 text-muted">
                <RefreshCw size={24} className="animate-spin text-primary-orange" />
                <span style={{ fontSize: '0.8125rem' }}>Generating SHAP plot...</span>
              </div>
            ) : explainPlotUrl ? (
              <img 
                src={explainPlotUrl} 
                alt={`SHAP plot ${explainModel}`}
                style={{ maxWidth: '100%', maxHeight: '200px', objectFit: 'contain', borderRadius: 'var(--radius-sm)' }} 
              />
            ) : (
              <div className="text-muted" style={{ fontSize: '0.8125rem' }}>Failed to render plot image.</div>
            )}
          </div>
        </div>
      </motion.div>
    );
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
            onClick={() => {
              setMethod('manual');
              setSelectedExplanationReadings(null);
              setSelectedSampleName('');
            }}
          >
            Manual Input
          </button>
          <button 
            className={`btn whitespace-nowrap ${method === 'csv' ? 'btn-primary' : 'btn-outline'}`}
            style={{ padding: '0.35rem 1.25rem', border: 'none', borderRadius: 'var(--radius-sm)' }}
            onClick={() => {
              setMethod('csv');
              setSelectedExplanationReadings(null);
              setSelectedSampleName('');
            }}
          >
            <Upload size={16} /> CSV Batch Upload
          </button>
          <button 
            className={`btn whitespace-nowrap ${method === 'websocket' ? 'btn-primary' : 'btn-outline'}`}
            style={{ padding: '0.35rem 1.25rem', border: 'none', borderRadius: 'var(--radius-sm)' }}
            onClick={() => {
              setMethod('websocket');
              setSelectedExplanationReadings(null);
              setSelectedSampleName('');
            }}
          >
            <Cpu size={16} /> WebSocket Live Stream
          </button>
        </div>
      </div>

      {method === 'manual' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
          {/* Input Section */}
          <div className="flex flex-col gap-4">
            <InferenceForm onSubmit={handleManualSubmit} />
            <ErrorCard message={manualError} />
            {isManualPredicting && (
              <div className="glass-card flex items-center justify-center p-4 gap-3">
                <LoadingSpinner />
                <span className="animate-pulse text-primary-orange">Analyzing Data...</span>
              </div>
            )}
          </div>

          {/* Results Section */}
          <section className="flex flex-col gap-6">
            {manualResult ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <ResultsDashboard resultsData={manualResult} />
                {manualResult.business_decision && (
                  <DecisionDashboard decisionData={manualResult.business_decision} />
                )}
                {/* XAI Panel for Manual Input */}
                {renderXAIPanel()}
              </div>
            ) : (
              <div className="glass-card flex items-center justify-center" style={{ height: '100%', minHeight: '400px', flexDirection: 'column', color: 'var(--text-secondary)' }}>
                <Activity size={48} style={{ marginBottom: '1rem', opacity: 0.5 }} />
                <p className="text-h3">Awaiting Data Input</p>
                <p className="text-muted">Fill out the form and run prediction.</p>
              </div>
            )}
          </section>
        </div>
      )}

      {method === 'csv' && (
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

                <ErrorCard message={csvError} />

                <button 
                  className="btn btn-primary w-full"
                  onClick={handleCsvPredict}
                  disabled={!selectedFile || isCsvPredicting}
                  style={{ marginTop: 'auto', padding: '0.75rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}
                >
                  {isCsvPredicting ? (
                    <>
                      <LoadingSpinner size={18} /> Analyzing Batch...
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
                  <div className="table-container" style={{ maxHeight: '250px', overflowY: 'auto' }}>
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
                            <tr 
                              key={sample.sample_index}
                              onClick={() => {
                                setSelectedExplanationReadings(sample.sensor_readings);
                                setSelectedSampleName(`Sample #${sample.sample_index}`);
                              }}
                              style={{ 
                                cursor: 'pointer',
                                backgroundColor: selectedSampleName === `Sample #${sample.sample_index}` ? 'rgba(255, 140, 66, 0.08)' : '' 
                              }}
                            >
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
                  <div className="text-muted" style={{ fontSize: '0.75rem', display: 'flex', justifyContent: 'space-between', marginTop: '0.25rem' }}>
                    <span style={{ fontSize: '0.7rem', fontStyle: 'italic' }}>Tip: Click any row to load its AI explanation details below.</span>
                    <span>Showing {filteredResults.length} of {csvResults.length} samples</span>
                  </div>
                </div>
              </div>

              {/* XAI Panel for CSV Batch List */}
              {renderXAIPanel()}
            </div>
          )}
        </div>
      )}

      {method === 'websocket' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '2rem' }}>
          {/* Connection Controls Panel */}
          <section className="glass-card flex flex-col gap-6">
            <h2 className="text-h2 flex items-center gap-2">
              {wsStatus === 'Connected' ? (
                <Wifi className="text-success-green animate-pulse" size={22} />
              ) : (
                <WifiOff className="text-muted" size={22} />
              )}
              Streaming Panel
            </h2>

            <div style={{ backgroundColor: 'var(--light-bg)', padding: '1rem', borderRadius: 'var(--radius-md)', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <div className="flex justify-between items-center">
                <span className="text-muted" style={{ fontSize: '0.875rem' }}>Socket Connection Status</span>
                <span 
                  className="status-badge"
                  style={{
                    backgroundColor: 
                      wsStatus === 'Connected' ? 'rgba(46, 204, 113, 0.15)' :
                      wsStatus === 'Connecting' ? 'rgba(241, 196, 15, 0.15)' :
                      'rgba(100, 116, 139, 0.15)',
                    color: 
                      wsStatus === 'Connected' ? '#2ECC71' :
                      wsStatus === 'Connecting' ? '#F1C40F' :
                      '#64748B',
                    fontWeight: 'bold'
                  }}
                >
                  {wsStatus}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-muted" style={{ fontSize: '0.875rem' }}>Processed Ticks</span>
                <span className="text-h3">{wsLog.length}</span>
              </div>
            </div>

            {/* Config options */}
            <div className="flex flex-col gap-4">
              <div>
                <label className="text-muted mb-2" style={{ display: 'flex', fontSize: '0.875rem', fontWeight: 500 }}>
                  CSV File to Stream
                </label>
                {streamingFile ? (
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.5rem', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)' }}>
                    <span style={{ fontSize: '0.875rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '140px' }} title={streamingFile.name}>
                      {streamingFile.name}
                    </span>
                    <button onClick={clearStreamingFile} disabled={isStreaming} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#E74C3C' }}>
                      <Trash2 size={14} />
                    </button>
                  </div>
                ) : (
                  <button 
                    className="btn btn-outline w-full"
                    onClick={() => streamFileInputRef.current?.click()}
                    disabled={isStreaming}
                    style={{ borderStyle: 'dashed' }}
                  >
                    <Upload size={14} /> Select CSV File
                  </button>
                )}
                <input 
                  type="file" 
                  ref={streamFileInputRef} 
                  onChange={handleStreamingFileChange} 
                  accept=".csv" 
                  style={{ display: 'none' }}
                />
                {!streamingFile && (
                  <span className="text-muted" style={{ fontSize: '0.7rem', marginTop: '0.25rem', display: 'block' }}>
                    No file selected. System will stream generated e-tongue sweeps.
                  </span>
                )}
              </div>

              <div>
                <label className="text-muted mb-2" style={{ display: 'flex', fontSize: '0.875rem', fontWeight: 500 }}>
                  Streaming Interval
                </label>
                <select
                  value={streamInterval}
                  onChange={(e) => setStreamInterval(parseInt(e.target.value))}
                  disabled={isStreaming}
                  style={{ width: '100%', padding: '0.5rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', outline: 'none' }}
                >
                  <option value={300}>300ms (Fast)</option>
                  <option value={500}>500ms</option>
                  <option value={1000}>1000ms (1 Second)</option>
                  <option value={2000}>2000ms (2 Seconds)</option>
                </select>
              </div>

              <div>
                <label className="text-muted mb-2" style={{ display: 'flex', fontSize: '0.875rem', fontWeight: 500 }}>
                  Preprocessing Strategy
                </label>
                <select 
                  value={preprocessingStrategy} 
                  onChange={(e) => setPreprocessingStrategy(e.target.value)}
                  disabled={isStreaming}
                  style={{ width: '100%', padding: '0.5rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', outline: 'none' }}
                >
                  <option value="raw">Raw Sweep Analysis</option>
                  <option value="advanced">Advanced</option>
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
                  disabled={isStreaming}
                  style={{ width: '100%', padding: '0.5rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', outline: 'none' }}
                />
              </div>
            </div>

            {error && (
              <div style={{ backgroundColor: 'rgba(231, 76, 60, 0.1)', color: '#E74C3C', padding: '0.75rem', borderRadius: 'var(--radius-sm)', fontSize: '0.875rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <AlertCircle size={16} /> {error}
              </div>
            )}

            {isStreaming ? (
              <button 
                className="btn w-full"
                onClick={stopStream}
                style={{ backgroundColor: '#E74C3C', color: 'white', padding: '0.75rem' }}
              >
                <StopCircle size={18} /> Stop Live Stream
              </button>
            ) : (
              <button 
                className="btn btn-primary w-full"
                onClick={startStream}
                style={{ padding: '0.75rem' }}
              >
                <Play size={18} /> Start Live Stream
              </button>
            )}
          </section>

          {/* Real-time Streaming Display Panel */}
          <section className="flex flex-col gap-6">
            <div className="glass-card flex flex-col gap-4">
              <h3 className="text-h3 flex items-center justify-between">
                <span>Real-Time Model Analysis</span>
                {isStreaming && (
                  <span className="flex items-center gap-1 text-success-green" style={{ fontSize: '0.75rem', fontWeight: 500 }}>
                    <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--success-green)' }} className="animate-ping" />
                    LIVE
                  </span>
                )}
              </h3>

              {/* Real-time Line Graph */}
              <div style={{ height: '240px', width: '100%' }}>
                {wsChartData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={wsChartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                      <XAxis dataKey="tick" stroke="var(--text-secondary)" tick={{ fontSize: 10 }} />
                      <YAxis stroke="var(--text-secondary)" tick={{ fontSize: 10 }} />
                      <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid var(--border-color)' }} />
                      <Legend verticalAlign="top" height={36} tick={{ fontSize: 11 }} />
                      <Line type="monotone" name="Estimated Storage Days" dataKey="age" stroke="var(--primary-orange)" strokeWidth={2} activeDot={{ r: 6 }} dot={false} />
                      <Line type="monotone" name="Predicted Folic Acid (µM)" dataKey="folic" stroke="var(--success-green)" strokeWidth={2} activeDot={{ r: 6 }} dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex flex-col items-center justify-center h-full text-muted" style={{ border: '1px dashed var(--border-color)', borderRadius: 'var(--radius-md)' }}>
                    <Activity size={32} className="animate-pulse" style={{ opacity: 0.5, marginBottom: '0.5rem' }} />
                    <p style={{ fontSize: '0.875rem' }}>No active stream. Start stream to display line plot.</p>
                  </div>
                )}
              </div>
            </div>

            {/* Rolling Logs Panel */}
            <div className="glass-card flex flex-col gap-4" style={{ flex: 1 }}>
              <h3 className="text-h3">Live Prediction Logs</h3>
              <div style={{ height: '180px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.5rem', padding: '0.25rem' }}>
                {wsLog.length > 0 ? (
                  wsLog.map((log, index) => (
                    <div 
                      key={index} 
                      style={{ 
                        display: 'flex', 
                        alignItems: 'center', 
                        justifyContent: 'space-between', 
                        padding: '0.6rem 1rem', 
                        backgroundColor: 'var(--light-bg)', 
                        borderRadius: 'var(--radius-sm)',
                        borderLeft: 
                          log.grade === 'A' ? '4px solid #2ECC71' :
                          log.grade === 'B' ? '4px solid #3498DB' :
                          log.grade === 'C' ? '4px solid #FF8C42' :
                          '4px solid #E74C3C'
                      }}
                    >
                      <div className="flex items-center gap-3">
                        <span className="text-muted" style={{ fontSize: '0.75rem', fontWeight: 600 }}>[{log.time}]</span>
                        <span style={{ fontWeight: 500 }}>Sample #{log.index + 1}</span>
                      </div>
                      <div className="flex items-center gap-4">
                        <span style={{ fontSize: '0.875rem' }}>Age: <strong>{log.age.toFixed(1)}d</strong> | Folic: <strong>{log.folic.toFixed(1)}µM</strong></span>
                        <span 
                          className="status-badge"
                          style={{
                            backgroundColor: 
                              log.grade === 'A' ? 'rgba(46, 204, 113, 0.15)' :
                              log.grade === 'B' ? 'rgba(52, 152, 219, 0.15)' :
                              log.grade === 'C' ? 'rgba(255, 140, 66, 0.15)' :
                              'rgba(231, 76, 60, 0.15)',
                            color: 
                              log.grade === 'A' ? '#2ECC71' :
                              log.grade === 'B' ? '#3498DB' :
                              log.grade === 'C' ? '#FF8C42' :
                              '#E74C3C',
                            fontWeight: 'bold',
                            fontSize: '0.7rem'
                          }}
                        >
                          Grade {log.grade}
                        </span>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="flex items-center justify-center h-full text-muted" style={{ fontSize: '0.875rem' }}>
                    Awaiting websocket streaming data...
                  </div>
                )}
              </div>
            </div>
          </section>
        </div>
      )}
    </div>
  );
}

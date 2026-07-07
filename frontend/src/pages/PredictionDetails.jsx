import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, Trash2, Activity, FileText } from 'lucide-react';
import { useHistory } from '../hooks/useHistory';
import DownloadReportButton from '../components/DownloadReportButton';
import ResultsDashboard from '../components/ResultsDashboard';
import DecisionDashboard from '../components/decision/DecisionDashboard';
import SkeletonLoader from '../components/ui/SkeletonLoader';
import ErrorCard from '../components/ui/ErrorCard';
import ConfirmDialog from '../components/ui/ConfirmDialog';

export default function PredictionDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const { fetchById, removePrediction } = useHistory();
  const [prediction, setPrediction] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const [isDeleting, setIsDeleting] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  useEffect(() => {
    let mounted = true;
    const fetchDetails = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await fetchById(id);
        if (mounted) setPrediction(data);
      } catch (err) {
        if (mounted) setError(err instanceof Error ? err.message : 'Failed to load details.');
      } finally {
        if (mounted) setIsLoading(false);
      }
    };
    fetchDetails();
    return () => { mounted = false; };
  }, [id, fetchById]);

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await removePrediction(id);
      navigate('/report'); // Navigate back to history list
    } catch (err) {
      // Error toasted by hook
      setIsDeleting(false);
      setShowConfirm(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex flex-col gap-6 p-4">
        <SkeletonLoader className="h-12 w-1/3" />
        <SkeletonLoader className="h-64 w-full" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col gap-4">
        <Link to="/report" className="flex items-center gap-2 text-muted hover:text-white" style={{ textDecoration: 'none' }}>
          <ArrowLeft size={16} /> Back to History
        </Link>
        <ErrorCard message={error} />
      </div>
    );
  }

  if (!prediction) return null;

  // Parse JSON strings from database
  let requestJson = {};
  let responseJson = {};
  try {
    requestJson = typeof prediction.request_json === 'string' ? JSON.parse(prediction.request_json) : prediction.request_json;
    responseJson = typeof prediction.response_json === 'string' ? JSON.parse(prediction.response_json) : prediction.response_json;
  } catch (e) {
    console.error("Failed to parse prediction JSON", e);
  }

  // Reconstruct response format expected by ResultsDashboard
  const resultsData = {
    results: responseJson.results,
    logistics: responseJson.logistics,
    business_decision: responseJson.business_decision
  };

  const hasShapData = !!responseJson.explanation;
  const sensorReadings = requestJson.sensor_readings || [];

  return (
    <div className="flex flex-col gap-8">
      {/* Header & Actions */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link to="/report" className="btn btn-outline" style={{ padding: '0.5rem', borderRadius: '50%' }} title="Back to History">
            <ArrowLeft size={18} />
          </Link>
          <h1 className="text-h1 m-0 flex items-center gap-3">
            Prediction #{prediction.id}
          </h1>
        </div>
        
        <div className="flex items-center gap-3">
          <DownloadReportButton id={prediction.id} label="Download PDF" />
          <button 
            className="btn btn-outline flex items-center gap-2" 
            style={{ color: '#ef4444', borderColor: 'rgba(239, 68, 68, 0.2)' }}
            onClick={() => setShowConfirm(true)}
            disabled={isDeleting}
          >
            <Trash2 size={16} />
            Delete
          </button>
        </div>
      </div>

      <ConfirmDialog 
        isOpen={showConfirm}
        title="Delete Prediction"
        message={`Are you sure you want to permanently delete Prediction #${id}?`}
        confirmText="Delete"
        isDestructive={true}
        isLoading={isDeleting}
        onConfirm={handleDelete}
        onCancel={() => setShowConfirm(false)}
      />

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: '2rem' }}>
        {/* Main Content */}
        <div className="flex flex-col gap-8">
          {/* Section 1: Prediction Summary (reusing ResultsDashboard) */}
          <ResultsDashboard resultsData={resultsData} />
          
          {resultsData.business_decision && (
            <DecisionDashboard decisionData={resultsData.business_decision} />
          )}

          {/* Section 2: Sensor Readings */}
          <section className="glass-card">
            <h2 className="text-h2 flex items-center gap-2 mb-4">
              <Activity size={24} className="text-primary-orange" /> Sensor Readings
            </h2>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)' }}>
                    <th style={{ padding: '0.75rem 0' }}>Sensor #</th>
                    <th style={{ padding: '0.75rem' }}>Value</th>
                  </tr>
                </thead>
                <tbody>
                  {sensorReadings.map((val, idx) => (
                    <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                      <td style={{ padding: '0.75rem 0', color: 'var(--text-muted)' }}>Sensor {idx + 1}</td>
                      <td style={{ padding: '0.75rem', fontWeight: 500 }}>{Number(val).toFixed(4)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
          
          {/* Optional SHAP Section */}
          {hasShapData && (
            <section className="glass-card" style={{ borderTop: '4px solid var(--primary-orange)' }}>
              <h2 className="text-h2 flex items-center gap-2 mb-4">
                <FileText size={24} className="text-primary-orange" /> Top Influential Features
              </h2>
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)' }}>
                      <th style={{ padding: '0.75rem 0' }}>Feature</th>
                      <th style={{ padding: '0.75rem', textAlign: 'right' }}>SHAP Value</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(responseJson.explanation.top_features_day)
                      .sort(([, a], [, b]) => Math.abs(b) - Math.abs(a))
                      .slice(0, 5)
                      .map(([feature, val]) => (
                      <tr key={feature} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                        <td style={{ padding: '0.75rem 0' }}>{feature}</td>
                        <td style={{ padding: '0.75rem', textAlign: 'right', fontWeight: 500, color: val > 0 ? '#10b981' : '#ef4444' }}>
                          {val > 0 ? '+' : ''}{Number(val).toFixed(4)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          )}
        </div>

        {/* Sidebar Metadata */}
        <div className="flex flex-col gap-6">
          <section className="glass-card">
            <h3 className="text-h3 mb-4">Metadata</h3>
            <div className="flex flex-col gap-4 text-sm">
              <div>
                <p className="text-muted" style={{ fontSize: '0.75rem', marginBottom: '0.25rem' }}>Batch ID</p>
                <p style={{ fontWeight: 500 }}>{prediction.batch_id}</p>
              </div>
              <div>
                <p className="text-muted" style={{ fontSize: '0.75rem', marginBottom: '0.25rem' }}>Generated</p>
                <p style={{ fontWeight: 500 }}>{new Date(prediction.created_at).toLocaleString()}</p>
              </div>
              <div>
                <p className="text-muted" style={{ fontSize: '0.75rem', marginBottom: '0.25rem' }}>Model Version</p>
                <p style={{ fontWeight: 500 }}>{prediction.model_version || 'v1.0.0'}</p>
              </div>
              <div>
                <p className="text-muted" style={{ fontSize: '0.75rem', marginBottom: '0.25rem' }}>Inference Latency</p>
                <p style={{ fontWeight: 500 }}>{prediction.processing_latency_ms ? `${prediction.processing_latency_ms.toFixed(2)} ms` : 'N/A'}</p>
              </div>
              <div>
                <p className="text-muted" style={{ fontSize: '0.75rem', marginBottom: '0.25rem' }}>Storage Temp</p>
                <p style={{ fontWeight: 500 }}>{requestJson.storage_temperature_c}°C</p>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}

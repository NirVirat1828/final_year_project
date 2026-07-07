import { motion } from 'framer-motion';
import { BarChart3, AlertCircle } from 'lucide-react';
import { useHistory } from '../hooks/useHistory';

import FreshnessDistributionChart from '../components/analytics/FreshnessDistributionChart';
import PredictionsByDayChart from '../components/analytics/PredictionsByDayChart';
import AverageConfidenceChart from '../components/analytics/AverageConfidenceChart';
import EndpointUsageChart from '../components/analytics/EndpointUsageChart';
import ErrorCard from '../components/ui/ErrorCard';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import EmptyState from '../components/ui/EmptyState';
import { useEffect, useMemo } from 'react';

export default function AnalyticsDashboard() {
  const { data: history, isLoading, error, fetchHistory } = useHistory();

  useEffect(() => {
    // Backend limits page_size to 100 (le=100 in endpoints.py)
    fetchHistory(1, 100);
  }, [fetchHistory]);

  // Compute Aggregations
  const { freshnessData, daysData, confidenceData, endpointData } = useMemo(() => {
    if (!history.length) return { freshnessData: [], daysData: [], confidenceData: [], endpointData: [] };

    const freshnessCounts = {};
    const daysCounts = {};
    const confidenceSums = {};
    const endpointCounts = { 'Live API': 0, 'CSV Batch': 0 };

    history.forEach(record => {
      // Freshness Distribution
      const grade = record.freshness_grade || 'Unknown';
      freshnessCounts[grade] = (freshnessCounts[grade] || 0) + 1;

      // Confidence Sums (for averaging)
      if (!confidenceSums[grade]) confidenceSums[grade] = { sum: 0, count: 0 };
      confidenceSums[grade].sum += record.confidence || 0;
      confidenceSums[grade].count += 1;

      // Predictions by Day
      const dateStr = new Date(record.created_at).toLocaleDateString();
      daysCounts[dateStr] = (daysCounts[dateStr] || 0) + 1;

      // Endpoint Usage (derive from batch_id)
      const batchId = record.batch_id || '';
      if (batchId.toLowerCase().includes('csv')) {
        endpointCounts['CSV Batch'] += 1;
      } else {
        endpointCounts['Live API'] += 1;
      }
    });

    // Format for Recharts
    const mappedFreshness = Object.keys(freshnessCounts).map(key => ({
      name: key,
      value: freshnessCounts[key]
    }));

    // Sort days chronologically
    const mappedDays = Object.keys(daysCounts)
      .map(key => ({ date: key, count: daysCounts[key] }))
      .sort((a, b) => new Date(a.date) - new Date(b.date));

    const mappedConfidence = Object.keys(confidenceSums).map(key => ({
      name: key,
      avgConfidence: confidenceSums[key].sum / confidenceSums[key].count
    }));

    const mappedEndpoints = [
      { name: 'Live API', value: endpointCounts['Live API'] },
      { name: 'CSV Batch', value: endpointCounts['CSV Batch'] }
    ].filter(e => e.value > 0);

    return { 
      freshnessData: mappedFreshness, 
      daysData: mappedDays, 
      confidenceData: mappedConfidence, 
      endpointData: mappedEndpoints 
    };
  }, [history]);

  return (
    <div className="flex flex-col gap-8">
      <div className="flex items-center justify-between">
        <h1 className="text-h1 flex items-center gap-4">
          <BarChart3 className="text-primary-orange" size={32} /> Analytics Dashboard
        </h1>
      </div>

      <ErrorCard message={error} />
      
      {isLoading ? (
        <div className="flex flex-col items-center justify-center h-64 text-muted gap-4">
          <LoadingSpinner size={32} />
          <span className="animate-pulse">Crunching numbers...</span>
        </div>
      ) : !error && history.length === 0 ? (
        <EmptyState 
          icon={BarChart3} 
          title="No Analytics Data" 
          message="There is no prediction data available to generate analytics. Please run some predictions first." 
          className="glass-card"
        />
      ) : !error && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
          
          <motion.section 
            className="glass-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
          >
            <h2 className="text-h2 mb-4" style={{ fontSize: '1.25rem' }}>Predictions Over Time</h2>
            <PredictionsByDayChart data={daysData} />
          </motion.section>

          <motion.section 
            className="glass-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.1 }}
          >
            <h2 className="text-h2 mb-4" style={{ fontSize: '1.25rem' }}>Freshness Distribution</h2>
            <FreshnessDistributionChart data={freshnessData} />
          </motion.section>

          <motion.section 
            className="glass-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.2 }}
          >
            <h2 className="text-h2 mb-4" style={{ fontSize: '1.25rem' }}>Average Confidence by Grade</h2>
            <AverageConfidenceChart data={confidenceData} />
          </motion.section>

          <motion.section 
            className="glass-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.3 }}
          >
            <h2 className="text-h2 mb-4" style={{ fontSize: '1.25rem' }}>Endpoint Usage</h2>
            <EndpointUsageChart data={endpointData} />
          </motion.section>

        </div>
      )}
    </div>
  );
}

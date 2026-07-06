import { useState, useCallback } from 'react';
import { getPredictionHistory, getPredictionById, deletePrediction, getPredictionStats } from '../api/historyApi';
import { useToast } from './useToast';

export function useHistory() {
  const [data, setData] = useState([]);
  const [stats, setStats] = useState(null);
  const [pagination, setPagination] = useState({ page: 1, totalPages: 1, totalRecords: 0 });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const { addToast } = useToast();

  const fetchHistory = useCallback(async (page = 1, pageSize = 20) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await getPredictionHistory(page, pageSize);
      setData(result.predictions || []);
      setPagination({
        page: result.page || page,
        totalPages: result.total_pages || 1,
        totalRecords: result.total_records || 0
      });
      return result;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch history';
      setError(message);
      addToast(message, 'error');
    } finally {
      setIsLoading(false);
    }
  }, [addToast]);

  const fetchStats = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await getPredictionStats();
      setStats(result);
      return result;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch stats';
      setError(message);
      setStats({
        total_predictions: '-',
        average_confidence: '-',
        average_latency: '-',
        latest_prediction: null,
        model_version: 'Unknown',
        backend_status: 'Offline'
      });
    } finally {
      setIsLoading(false);
    }
  }, []);

  const removePrediction = useCallback(async (id) => {
    try {
      await deletePrediction(id);
      addToast('Prediction deleted successfully.', 'success');
      return true;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to delete prediction';
      addToast(message, 'error');
      throw err;
    }
  }, [addToast]);

  const fetchById = useCallback(async (id) => {
    try {
      return await getPredictionById(id);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch prediction';
      addToast(message, 'error');
      throw err;
    }
  }, [addToast]);

  return { 
    data, 
    stats, 
    pagination, 
    isLoading, 
    error, 
    fetchHistory, 
    fetchStats, 
    removePrediction, 
    fetchById 
  };
}

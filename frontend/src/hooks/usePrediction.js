import { useState, useCallback } from 'react';
import { analyzeBatch, analyzeCsvBatch } from '../api/predictionApi';
import { useToast } from './useToast';

export function usePrediction() {
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const { addToast } = useToast();

  const predict = useCallback(async (payload, isCsv = false, preprocessing = 'raw', temp = 4.0) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = isCsv 
        ? await analyzeCsvBatch(payload, preprocessing, temp)
        : await analyzeBatch(payload);
      setData(result);
      addToast('Prediction completed successfully.', 'success');
      return result;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'An unknown error occurred';
      setError(message);
      addToast(message, 'error', 5000);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [addToast]);

  const reset = useCallback(() => {
    setData(null);
    setError(null);
  }, []);

  return { predict, data, isLoading, error, reset };
}

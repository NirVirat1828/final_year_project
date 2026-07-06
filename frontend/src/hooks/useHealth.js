import { useState, useEffect } from 'react';
import { checkHealth } from '../api/healthApi';

export function useHealth() {
  const [isHealthy, setIsHealthy] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    const ping = async () => {
      try {
        await checkHealth();
        if (mounted) setIsHealthy(true);
      } catch {
        if (mounted) setIsHealthy(false);
      } finally {
        if (mounted) setIsLoading(false);
      }
    };
    
    ping();
    const interval = setInterval(ping, 30000); // Check every 30s
    
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  return { isHealthy, isLoading };
}

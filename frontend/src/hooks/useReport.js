import { useState, useCallback } from 'react';
import { downloadPredictionReport } from '../api/reportApi';
import { useToast } from './useToast';

export function useReport() {
  const [isDownloading, setIsDownloading] = useState(false);
  const { addToast } = useToast();

  const download = useCallback(async (id) => {
    setIsDownloading(true);
    addToast('Generating PDF report...', 'info');
    try {
      const blobUrl = await downloadPredictionReport(id);
      const a = document.createElement('a');
      a.href = blobUrl;
      a.download = `prediction_report_${id}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(blobUrl);
      addToast('PDF downloaded successfully.', 'success');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to download report';
      addToast(message, 'error');
    } finally {
      setIsDownloading(false);
    }
  }, [addToast]);

  return { download, isDownloading };
}

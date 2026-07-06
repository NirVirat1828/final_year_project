import { Download } from 'lucide-react';
import { useReport } from '../hooks/useReport';
import LoadingSpinner from './ui/LoadingSpinner';

export default function DownloadReportButton({ id, size = "md", label = "" }) {
  const { download, isDownloading } = useReport();

  const handleDownload = () => {
    download(id);
  };

  const btnStyle = size === "sm" ? { padding: '0.25rem 0.5rem', fontSize: '0.75rem' } : {};

  return (
    <button 
      className="btn btn-outline flex items-center gap-2 justify-center" 
      style={btnStyle}
      onClick={handleDownload}
      disabled={isDownloading}
      title="Download PDF Report"
    >
      {isDownloading ? <LoadingSpinner size={size === "sm" ? 14 : 18} className="text-current" /> : <Download size={size === "sm" ? 14 : 18} />}
      {label && <span>{isDownloading ? 'Downloading...' : label}</span>}
    </button>
  );
}

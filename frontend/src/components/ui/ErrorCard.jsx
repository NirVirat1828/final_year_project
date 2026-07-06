import { AlertCircle } from 'lucide-react';

export default function ErrorCard({ message, onRetry }) {
  if (!message) return null;
  
  return (
    <div className="warning-banner flex items-center justify-between gap-4" role="alert">
      <div className="flex items-center gap-2">
        <AlertCircle size={20} />
        <span>{message}</span>
      </div>
      {onRetry && (
        <button 
          onClick={onRetry} 
          className="btn btn-outline"
          style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
        >
          Retry
        </button>
      )}
    </div>
  );
}

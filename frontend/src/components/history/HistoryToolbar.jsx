import { RefreshCw } from 'lucide-react';

export default function HistoryToolbar({ isLoading, onRefresh }) {
  return (
    <div className="flex items-center justify-end">
      <button 
        className="btn btn-outline flex items-center gap-2"
        onClick={onRefresh}
        disabled={isLoading}
      >
        <RefreshCw size={16} className={isLoading ? "animate-spin" : ""} />
        Refresh
      </button>
    </div>
  );
}

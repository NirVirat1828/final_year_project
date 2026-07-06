import { ChevronLeft, ChevronRight } from 'lucide-react';

export default function HistoryPagination({ page, pageSize, totalPages, totalRecords, onPageChange }) {
  return (
    <div className="flex items-center justify-between" style={{ marginTop: 'auto', paddingTop: '1rem', borderTop: '1px solid var(--border-color)', fontSize: '0.875rem', color: 'var(--text-muted)' }}>
      <span>Showing {(page - 1) * pageSize + 1} to {Math.min(page * pageSize, totalRecords)} of {totalRecords} entries</span>
      <div className="flex items-center gap-2">
        <button 
          className="btn btn-outline" 
          style={{ padding: '0.25rem 0.5rem' }}
          disabled={page === 1}
          onClick={() => onPageChange(page - 1)}
        >
          <ChevronLeft size={16} />
        </button>
        <span style={{ margin: '0 0.5rem' }}>Page {page} of {totalPages}</span>
        <button 
          className="btn btn-outline" 
          style={{ padding: '0.25rem 0.5rem' }}
          disabled={page === totalPages}
          onClick={() => onPageChange(page + 1)}
        >
          <ChevronRight size={16} />
        </button>
      </div>
    </div>
  );
}

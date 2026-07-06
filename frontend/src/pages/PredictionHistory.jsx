import { useState, useEffect } from 'react';
import { Database, AlertCircle } from 'lucide-react';
import { useHistory } from '../hooks/useHistory';
import PredictionHistoryTable from '../components/history/PredictionHistoryTable';
import HistoryPagination from '../components/history/HistoryPagination';
import HistoryToolbar from '../components/history/HistoryToolbar';
import ConfirmDialog from '../components/ui/ConfirmDialog';
import ErrorCard from '../components/ui/ErrorCard';
import EmptyState from '../components/ui/EmptyState';
import SkeletonLoader from '../components/ui/SkeletonLoader';

export default function PredictionHistory() {
  const { data: history, pagination, isLoading, error, fetchHistory, removePrediction } = useHistory();
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  
  const [deleteModalId, setDeleteModalId] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    fetchHistory(page, pageSize);
  }, [page, pageSize, fetchHistory]);

  const confirmDelete = async () => {
    if (!deleteModalId) return;
    setIsDeleting(true);
    try {
      await removePrediction(deleteModalId);
      if (history.length === 1 && page > 1) {
        setPage(page - 1);
      } else {
        await fetchHistory(page, pageSize);
      }
      setDeleteModalId(null);
    } catch (err) {
      // Error is already toasted by hook
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="flex flex-col gap-8">
      <div className="flex items-center justify-between">
        <h1 className="text-h1 flex items-center gap-4">
          <Database className="text-primary-orange" size={32} /> Prediction History
        </h1>
        <HistoryToolbar isLoading={isLoading} onRefresh={() => fetchHistory()} />
      </div>

      <section className="glass-card flex flex-col gap-6" style={{ minHeight: '500px' }}>
        <ErrorCard message={error} />
        
        {isLoading && history.length === 0 ? (
          <div className="flex flex-col gap-4">
            <SkeletonLoader className="h-12 w-full" />
            <SkeletonLoader className="h-12 w-full" />
            <SkeletonLoader className="h-12 w-full" />
            <SkeletonLoader className="h-12 w-full" />
          </div>
        ) : !error && history.length === 0 ? (
          <EmptyState 
            icon={Database} 
            title="No Predictions Found" 
            message="Your prediction history is empty. Run a prediction to see it here." 
          />
        ) : (
          <>
            <PredictionHistoryTable 
              history={history} 
              onDelete={(id) => setDeleteModalId(id)}
              actionLoading={{}} // If needed later
            />
            <HistoryPagination 
              page={page} 
              pageSize={pageSize} 
              totalPages={pagination.totalPages} 
              totalRecords={pagination.totalRecords} 
              onPageChange={setPage} 
            />
          </>
        )}
      </section>

      <ConfirmDialog 
        isOpen={!!deleteModalId} 
        title="Delete Prediction"
        message={`Are you sure you want to permanently delete Prediction #${deleteModalId}?`}
        confirmText="Delete"
        isDestructive={true}
        isLoading={isDeleting}
        onConfirm={confirmDelete}
        onCancel={() => setDeleteModalId(null)}
      />
    </div>
  );
}

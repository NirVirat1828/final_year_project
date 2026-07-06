import PredictionRow from './PredictionRow';

export default function PredictionHistoryTable({ history, onDelete, actionLoading }) {
  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
        <thead>
          <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
            <th style={{ padding: '1rem 0' }}>ID</th>
            <th style={{ padding: '1rem' }}>Batch ID</th>
            <th style={{ padding: '1rem' }}>Grade</th>
            <th style={{ padding: '1rem' }}>Est. Age</th>
            <th style={{ padding: '1rem' }}>Date</th>
            <th style={{ padding: '1rem', textAlign: 'right' }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {history.map((record) => (
            <PredictionRow 
              key={record.id} 
              record={record} 
              onDelete={onDelete} 
              actionLoading={actionLoading[record.id]} 
            />
          ))}
        </tbody>
      </table>
    </div>
  );
}

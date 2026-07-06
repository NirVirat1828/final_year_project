import { Database } from 'lucide-react';

export default function EmptyState({ icon: Icon = Database, title = 'No Data', message = 'There is currently no data to display.', className = '' }) {
  return (
    <div className={`flex flex-col items-center justify-center h-64 text-muted text-center ${className}`}>
      <div style={{ padding: '1rem', backgroundColor: 'rgba(255,255,255,0.02)', borderRadius: '50%', marginBottom: '1rem' }}>
        <Icon size={32} />
      </div>
      <h3 className="text-h3 mb-2">{title}</h3>
      <p style={{ maxWidth: '300px', fontSize: '0.875rem' }}>{message}</p>
    </div>
  );
}

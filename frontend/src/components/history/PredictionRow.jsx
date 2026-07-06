import { Link } from 'react-router-dom';
import { Eye, Download, Trash2 } from 'lucide-react';
import DownloadReportButton from '../DownloadReportButton';

export default function PredictionRow({ record, onDelete, actionLoading }) {
  return (
    <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
      <td style={{ padding: '1rem 0', fontWeight: 'bold' }}>#{record.id}</td>
      <td style={{ padding: '1rem', color: 'var(--text-muted)' }}>{record.batch_id}</td>
      <td style={{ padding: '1rem' }}>
        <span className={`grade-badge grade-${record.freshness_grade?.toLowerCase() || 'default'}`} style={{ display: 'inline-block', padding: '2px 8px', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 'bold' }}>
          {record.freshness_grade}
        </span>
      </td>
      <td style={{ padding: '1rem' }}>{Number(record.prediction_days || 0).toFixed(1)} days</td>
      <td style={{ padding: '1rem', fontSize: '0.875rem', color: 'var(--text-muted)' }}>
        {new Date(record.created_at).toLocaleString()}
      </td>
      <td style={{ padding: '1rem', textAlign: 'right' }}>
        <div className="flex justify-end gap-2">
          <Link 
            to={`/history/${record.id}`}
            className="btn btn-outline flex items-center justify-center" 
            style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
            title="View Details"
          >
            <Eye size={14} />
          </Link>
          
          <DownloadReportButton id={record.id} size="sm" />
          
          <button 
            className="btn btn-outline" 
            style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem', color: '#ef4444', borderColor: 'rgba(239, 68, 68, 0.2)' }}
            onClick={() => onDelete(record.id)}
            disabled={actionLoading}
            title="Delete Record"
          >
            <Trash2 size={14} />
          </button>
        </div>
      </td>
    </tr>
  );
}

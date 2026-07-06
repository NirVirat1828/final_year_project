import { Clock, User } from 'lucide-react';

export default function TopNav() {
  return (
    <header className="top-nav">
      <div className="top-nav-brand">
        <h1 className="text-h2" style={{ fontSize: '1.25rem' }}>Food Freshness Intelligence System</h1>
      </div>

      <div className="top-nav-status whitespace-nowrap">


        <div className="flex items-center gap-2">
          <Clock size={16} />
        </div>

        <div className="flex items-center gap-2" style={{ paddingLeft: '1rem', borderLeft: '1px solid var(--border-color)' }}>
          <User size={18} />
          <span style={{ fontWeight: 500, color: 'var(--text-primary)' }}>Researcher Profile</span>
        </div>
      </div>
    </header>
  );
}

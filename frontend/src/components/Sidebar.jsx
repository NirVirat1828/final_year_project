import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Database, 
  Trophy, 
  Swords, 
  GitMerge, 
  PieChart, 
  TrendingUp, 
  Lightbulb, 
  Activity, 
  BookOpen, 
  FileText 
} from 'lucide-react';

const navItems = [
  { path: '/', label: 'Executive Dashboard', icon: <LayoutDashboard size={18} /> },
  { path: '/dataset', label: 'Dataset Explorer', icon: <Database size={18} /> },
  { path: '/tournament', label: 'Tournament Arena', icon: <Trophy size={18} /> },
  { path: '/battle', label: 'Model Battle Arena', icon: <Swords size={18} /> },
  { path: '/impact', label: 'Preprocessing Impact', icon: <GitMerge size={18} /> },
  { path: '/classification', label: 'Classification Track', icon: <PieChart size={18} /> },
  { path: '/regression', label: 'Regression Track', icon: <TrendingUp size={18} /> },
  { path: '/features', label: 'Feature Insights', icon: <Lightbulb size={18} /> },
  { path: '/prediction', label: 'Live Prediction', icon: <Activity size={18} /> },
  { path: '/research', label: 'Research Findings', icon: <BookOpen size={18} /> },
  { path: '/report', label: 'Report Generator', icon: <FileText size={18} /> },
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">O</div>
        <span className="text-h3" style={{ fontSize: '1rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>Orange Freshness</span>
      </div>
      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <NavLink 
            key={item.path} 
            to={item.path} 
            className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}
          >
            {item.icon}
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}

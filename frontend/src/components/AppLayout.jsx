import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import TopNav from './TopNav';

export default function AppLayout() {
  return (
    <div className="app-container">
      <Sidebar />
      <div className="main-content">
        <TopNav />
        <main className="page-container">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

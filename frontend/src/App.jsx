import { useCallback, useEffect, useState } from 'react';
import Attendance from './pages/Attendance';
import Dashboard from './pages/Dashboard';
import Members from './pages/Members';
import Plans from './pages/Plans';
import Trainers from './pages/Trainers';

const PAGES = {
  dashboard: { label: 'Dashboard', icon: '▦', component: Dashboard },
  members: { label: 'Members', icon: '👥', component: Members },
  attendance: { label: 'Attendance', icon: '✓', component: Attendance },
  plans: { label: 'Plans', icon: '₹', component: Plans },
  trainers: { label: 'Trainers', icon: '🏋️', component: Trainers },
};

const pageFromHash = () => {
  const key = window.location.hash.replace('#/', '');
  return PAGES[key] ? key : 'dashboard';
};

export default function App() {
  const [page, setPage] = useState(pageFromHash);
  const [toast, setToast] = useState('');

  useEffect(() => {
    const onHash = () => setPage(pageFromHash());
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, []);

  useEffect(() => {
    if (!toast) return undefined;
    const timer = setTimeout(() => setToast(''), 2600);
    return () => clearTimeout(timer);
  }, [toast]);

  const navigate = useCallback((key) => {
    window.location.hash = `/${key}`;
  }, []);

  const Page = PAGES[page].component;

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">IP</span>
          <div>
            <b>IronPulse</b>
            <small>Gym Management</small>
          </div>
        </div>
        <nav>
          {Object.entries(PAGES).map(([key, p]) => (
            <a key={key} href={`#/${key}`} className={page === key ? 'active' : ''}>
              <span className="nav-icon" aria-hidden="true">{p.icon}</span>
              <span className="nav-label">{p.label}</span>
            </a>
          ))}
        </nav>
        <div className="side-bottom">
          <div className="upgrade">
            <strong>Train hard. Ship often.</strong>
            <p>Tested, scanned and deployed to Kubernetes on every commit.</p>
          </div>
          <div className="profile">
            <div className="avatar">HC</div>
            <div>
              <b>Himanshu Chauhan</b>
              <small>Gym Admin</small>
            </div>
          </div>
        </div>
      </aside>
      <main className="main">
        <Page navigate={navigate} notify={setToast} />
      </main>
      {toast && (
        <div className="toast" role="status">
          {toast}
        </div>
      )}
    </div>
  );
}

import { Outlet } from 'react-router-dom';
import { Header } from '../components/Header';
import { Sidebar } from '../components/Sidebar';

export default function Root() {
  return (
    <div style={{ display: 'flex', height: '100vh', backgroundColor: 'var(--background)' }}>
      <Sidebar />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <Header />
        <main style={{ flex: 1, overflow: 'auto' }}>
          <Outlet />
        </main>
      </div>
    </div>
  );
}
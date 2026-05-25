import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Header } from '../components/Header';
import { Sidebar } from '../components/Sidebar';
import styles from './Root.module.css';

export default function Root() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className={styles.root}>
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      {sidebarOpen && <div className={styles.overlay} onClick={() => setSidebarOpen(false)} />}
      <div className={styles.content}>
        <Header onToggleSidebar={() => setSidebarOpen(prev => !prev)} />
        <main className={styles.main}>
          <Outlet />
        </main>
      </div>
    </div>
  );
}

// src/components/Sidebar.jsx
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { LayoutDashboard, Package, BarChart3, User, Settings, Bell } from 'lucide-react';
import { useState, useEffect } from 'react';
import { getAlertEvents } from '../lib/storage';
import styles from './Sidebar.module.css';

export function Sidebar() {
  const location = useLocation();
  const navigate = useNavigate();
  const [unreadAlerts, setUnreadAlerts] = useState(0);

  useEffect(() => {
    const loadAlerts = async () => {
      try {
        const events = await getAlertEvents();
        const eventsArray = Array.isArray(events) ? events : [];
        const unread = eventsArray.filter(e => !e.read).length;
        setUnreadAlerts(unread);
      } catch (error) {
        console.error('Error loading alerts:', error);
        setUnreadAlerts(0);
      }
    };
    loadAlerts();
  }, []);

  const handleLogoClick = (e) => {
    e.preventDefault();
    if (location.pathname === '/') {
      window.location.reload();
    } else {
      navigate('/');
      setTimeout(() => {
        window.location.reload();
      }, 100);
    }
  };

  const links = [
    { to: '/', icon: LayoutDashboard, label: 'Дашборд' },
    { to: '/products', icon: Package, label: 'Товары' },
    { to: '/analytics', icon: BarChart3, label: 'Аналитика' },
    { to: '/profile', icon: User, label: 'Профиль' },
    { to: '/settings', icon: Settings, label: 'Настройки' },
  ];

  return (
    <aside className={styles.sidebar}>
      <div className={styles.logo} onClick={handleLogoClick} style={{ cursor: 'pointer' }}>
        <div className={styles.logoContent}>
          <BarChart3 className={styles.logoIcon} />
          <span className={styles.logoText}>PriceTracker</span>
        </div>
        <p className={styles.logoSubtext}>Мониторинг цен онлайн-магазинов</p>
      </div>

      <nav className={styles.nav}>
        <ul className={styles.navList}>
          {links.map((link) => {
            const isActive = location.pathname === link.to;
            const Icon = link.icon;
            return (
              <li key={link.to}>
                <Link
                  to={link.to}
                  className={`${styles.navLink} ${isActive ? styles.navLinkActive : ''}`}
                >
                  <Icon className={styles.navIcon} />
                  <span className={styles.navLabel}>{link.label}</span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {unreadAlerts > 0 && (
        <div className={styles.notificationsBadge}>
          <Bell className={styles.badgeIcon} />
          <div className={styles.badgeContent}>
            <p className={styles.badgeTitle}>
              {unreadAlerts} новое уведомление{unreadAlerts > 1 ? 'я' : ''}
            </p>
            <p className={styles.badgeText}>Проверьте изменения цен</p>
          </div>
        </div>
      )}
    </aside>
  );
}
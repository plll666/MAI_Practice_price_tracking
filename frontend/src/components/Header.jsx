// src/components/Header.jsx
import { Bell, User, Moon, Sun, LogOut } from 'lucide-react';
import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getAlertEvents, markAllAlertsAsRead } from '../lib/storage';
import styles from './Header.module.css';

export function Header() {
  const [showNotifications, setShowNotifications] = useState(false);
  const [isDark, setIsDark] = useState(false);
  const [alerts, setAlerts] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    loadAlerts();
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
      setIsDark(true);
      document.documentElement.classList.add('dark');
    }
  }, []);

  const loadAlerts = async () => {
    try {
      const alertsData = await getAlertEvents();
      const alertsArray = Array.isArray(alertsData) ? alertsData : [];
      setAlerts(alertsArray.slice(0, 5).reverse());
      setUnreadCount(alertsArray.filter(a => !a.read).length);
    } catch (error) {
      console.error('Error loading alerts:', error);
      setAlerts([]);
      setUnreadCount(0);
    }
  };

  const toggleTheme = () => {
    setIsDark(!isDark);
    if (!isDark) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  };

  const handleMarkAllRead = async () => {
    await markAllAlertsAsRead();
    setShowNotifications(false);
    loadAlerts();
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className={styles.header}>
      {/* Левая часть с текстом */}
      <div className={styles.titleSection}>
        <h1 className={styles.title}>Мониторинг цен онлайн-магазинов</h1>
        <p className={styles.subtitle}>Отслеживайте изменения цен и получайте уведомления</p>
      </div>

      {/* Правая часть с кнопками */}
      <div className={styles.actions}>
        {/* Кнопка темы */}
        <button onClick={toggleTheme} className={styles.iconButton} title={isDark ? 'Светлая тема' : 'Темная тема'}>
          {isDark ? <Sun size={20} /> : <Moon size={20} />}
        </button>

        {/* Уведомления */}
        <div className={styles.notificationsContainer}>
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className={styles.iconButton}
            title="Уведомления"
          >
            <Bell size={20} />
            {unreadCount > 0 && (
              <span className={styles.badge}>{unreadCount}</span>
            )}
          </button>

          {showNotifications && (
            <div className={styles.dropdown}>
              <div className={styles.dropdownHeader}>
                <h3>Уведомления</h3>
                {unreadCount > 0 && (
                  <button onClick={handleMarkAllRead} className={styles.markAllButton}>
                    Отметить все
                  </button>
                )}
              </div>
              <div className={styles.dropdownList}>
                {alerts.length === 0 ? (
                  <div className={styles.emptyNotifications}>Нет уведомлений</div>
                ) : (
                  alerts.map(alert => (
                    <div
                      key={alert.id}
                      className={`${styles.notificationItem} ${!alert.read ? styles.unread : ''}`}
                    >
                      <p className={styles.notificationMessage}>{alert.message}</p>
                      <p className={styles.notificationTime}>
                        {new Date(alert.timestamp).toLocaleString('ru-RU')}
                      </p>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* Профиль */}
        <Link to="/profile" className={styles.profileButton}>
          <User size={20} />
          <span className={styles.userName}>{user?.login || 'Пользователь'}</span>
        </Link>

        {/* Выход */}
        <button onClick={handleLogout} className={styles.iconButton} title="Выйти">
          <LogOut size={20} />
        </button>
      </div>
    </header>
  );
}
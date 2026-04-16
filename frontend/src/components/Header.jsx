// src/components/Header.jsx
import { Bell, User, Moon, Sun, LogOut, TrendingDown, Target } from 'lucide-react';
import { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getAlertEvents, markAllAlertsAsRead, markAlertAsRead } from '../lib/storage';
import { showBrowserNotification, requestNotificationPermission, getNotificationPermission } from '../lib/notifications';
import styles from './Header.module.css';

export function Header() {
  const [showNotifications, setShowNotifications] = useState(false);
  const [isDark, setIsDark] = useState(false);
  const [alerts, setAlerts] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const lastAlertCount = useRef(0);

  useEffect(() => {
    loadAlerts();
    requestNotificationPermission();
    
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
      
      const newUnreadCount = alertsArray.filter(a => !a.read).length;
      const previousUnread = lastAlertCount.current;
      lastAlertCount.current = newUnreadCount;
      
      if (newUnreadCount > previousUnread && previousUnread > 0) {
        const newAlerts = alertsArray.filter(a => !a.read).slice(0, newUnreadCount - previousUnread);
        for (const alert of newAlerts) {
          if (alert.currentPrice) {
            showBrowserNotification('Цена снижена! 🎉', {
              body: alert.message,
              tag: `price-alert-${alert.id}`
            });
          }
        }
      }
      
      setAlerts(alertsArray.slice(0, 10).reverse());
      setUnreadCount(newUnreadCount);
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
    loadAlerts();
  };

  const handleAlertClick = async (alert) => {
    if (!alert.read) {
      await markAlertAsRead(alert.id);
      loadAlerts();
    }
    if (alert.productId) {
      navigate(`/products/${alert.productId}`);
      setShowNotifications(false);
    }
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
                      onClick={() => handleAlertClick(alert)}
                      style={{ cursor: alert.productId ? 'pointer' : 'default' }}
                    >
                      <div className={styles.notificationContent}>
                        <div className={styles.notificationIcon}>
                          <TrendingDown size={20} />
                        </div>
                        <div className={styles.notificationText}>
                          <p className={styles.notificationMessage}>{alert.message}</p>
                          <div className={styles.notificationMeta}>
                            <span className={styles.currentPrice}>
                              <Target size={12} /> {alert.currentPrice?.toLocaleString('ru-RU')} ₽
                            </span>
                            {alert.targetPrice && (
                              <span className={styles.targetPrice}>
                                целевая: {alert.targetPrice.toLocaleString('ru-RU')} ₽
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
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
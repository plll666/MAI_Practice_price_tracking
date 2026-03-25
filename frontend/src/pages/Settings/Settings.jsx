// Settings.jsx
import { useState, useEffect } from 'react';
import { Download, Trash2, Bell, Database, Clock, Mail, Send, BellRing, Save } from 'lucide-react';
import { getProducts, getPriceSnapshots, getAlertEvents, getAlertRules, saveUserSettings, getUserSettings } from '../../lib/storage';
import { useAuth } from '../../context/AuthContext';
import styles from './Settings.module.css';

export default function Settings() {
  const { user } = useAuth();
  const [products, setProducts] = useState([]);
  const [snapshots, setSnapshots] = useState([]);
  const [events, setEvents] = useState([]);
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [settings, setSettings] = useState({
    notificationInterval: '6',
    emailNotifications: false,
    browserNotifications: false,
    telegramNotifications: false,
    email: '',
    telegram: '',
  });
  const [saving, setSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState('');

  useEffect(() => {
    loadData();
    loadSettings();
  }, []);

  const loadData = async () => {
    try {
      const productsData = await getProducts();
      const snapshotsData = await getPriceSnapshots();
      const eventsData = await getAlertEvents();
      const rulesData = await getAlertRules();

      setProducts(productsData);
      setSnapshots(snapshotsData);
      setEvents(eventsData);
      setRules(rulesData);
    } catch (error) {
      console.error('Error loading settings data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadSettings = async () => {
    try {
      const savedSettings = await getUserSettings();
      if (savedSettings) {
        setSettings(prev => ({
          ...prev,
          ...savedSettings,
        }));
      }
    } catch (error) {
      console.error('Error loading settings:', error);
    }
  };

  const handleSaveSettings = async () => {
    setSaving(true);
    setSaveMessage('');

    try {
      await saveUserSettings(settings);
      setSaveMessage('Настройки успешно сохранены!');
      setTimeout(() => setSaveMessage(''), 3000);

      // Запрашиваем разрешение на браузерные уведомления
      if (settings.browserNotifications && 'Notification' in window) {
        const permission = await Notification.requestPermission();
        if (permission === 'granted') {
          console.log('Browser notifications enabled');
        }
      }
    } catch (error) {
      console.error('Error saving settings:', error);
      setSaveMessage('Ошибка при сохранении настроек');
      setTimeout(() => setSaveMessage(''), 3000);
    } finally {
      setSaving(false);
    }
  };

  const handleExport = () => {
    const data = {
      products,
      snapshots,
      events,
      rules,
      settings,
      exportedAt: new Date().toISOString(),
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `price-tracker-export-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleClearData = () => {
    if (confirm('Вы уверены? Все данные будут удалены безвозвратно.')) {
      localStorage.clear();
      window.location.reload();
    }
  };

  const handleTestBrowserNotification = async () => {
    if ('Notification' in window) {
      const permission = await Notification.requestPermission();
      if (permission === 'granted') {
        new Notification('PriceTracker', {
          body: 'Тестовое уведомление! Уведомления работают корректно.',
          icon: '/logo192.png'
        });
      } else {
        alert('Разрешение на уведомления не получено');
      }
    } else {
      alert('Ваш браузер не поддерживает уведомления');
    }
  };

  if (loading) {
    return <div className={styles.container}>Загрузка...</div>;
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>Настройки</h1>
        <p className={styles.subtitle}>Управление уведомлениями и приложением</p>
      </div>

      <div className={styles.sections}>
        {/* Настройки уведомлений */}
        <div className={styles.section}>
          <div className={styles.sectionHeader}>
            <Bell className={styles.sectionIcon} />
            <h2 className={styles.sectionTitle}>Уведомления</h2>
          </div>

          <div className={styles.sectionContent}>
            {/* Интервал проверки */}
            <div className={styles.settingItem}>
              <div className={styles.settingInfo}>
                <Clock className={styles.settingIcon} />
                <div>
                  <div className={styles.settingLabel}>Интервал проверки цен</div>
                  <div className={styles.settingDescription}>Как часто проверять изменение цен</div>
                </div>
              </div>
              <select
                value={settings.notificationInterval}
                onChange={(e) => setSettings({ ...settings, notificationInterval: e.target.value })}
                className={styles.select}
              >
                <option value="1">Каждый час</option>
                <option value="6">Каждые 6 часов</option>
                <option value="12">Каждые 12 часов</option>
                <option value="24">Раз в день</option>
              </select>
            </div>

            {/* Email уведомления */}
            <div className={styles.settingItem}>
              <div className={styles.settingInfo}>
                <Mail className={styles.settingIcon} />
                <div>
                  <div className={styles.settingLabel}>Email уведомления</div>
                  <div className={styles.settingDescription}>Получать уведомления на почту</div>
                </div>
              </div>
              <button
                onClick={() => setSettings({ ...settings, emailNotifications: !settings.emailNotifications })}
                className={`${styles.toggle} ${settings.emailNotifications ? styles.toggleOn : styles.toggleOff}`}
              >
                <span className={`${styles.toggleKnob} ${settings.emailNotifications ? styles.toggleKnobOn : ''}`} />
              </button>
            </div>

            {/* Telegram уведомления */}
            <div className={styles.settingItem}>
              <div className={styles.settingInfo}>
                <Send className={styles.settingIcon} />
                <div>
                  <div className={styles.settingLabel}>Telegram уведомления</div>
                  <div className={styles.settingDescription}>Получать уведомления в Telegram</div>
                </div>
              </div>
              <button
                onClick={() => setSettings({ ...settings, telegramNotifications: !settings.telegramNotifications })}
                className={`${styles.toggle} ${settings.telegramNotifications ? styles.toggleOn : styles.toggleOff}`}
              >
                <span className={`${styles.toggleKnob} ${settings.telegramNotifications ? styles.toggleKnobOn : ''}`} />
              </button>
            </div>

            {/* Браузерные уведомления */}
            <div className={styles.settingItem}>
              <div className={styles.settingInfo}>
                <BellRing className={styles.settingIcon} />
                <div>
                  <div className={styles.settingLabel}>Браузерные уведомления</div>
                  <div className={styles.settingDescription}>Всплывающие уведомления в браузере</div>
                </div>
              </div>
              <div className={styles.toggleGroup}>
                <button
                  onClick={() => setSettings({ ...settings, browserNotifications: !settings.browserNotifications })}
                  className={`${styles.toggle} ${settings.browserNotifications ? styles.toggleOn : styles.toggleOff}`}
                >
                  <span className={`${styles.toggleKnob} ${settings.browserNotifications ? styles.toggleKnobOn : ''}`} />
                </button>
                {settings.browserNotifications && (
                  <button onClick={handleTestBrowserNotification} className={styles.testButton}>
                    Тест
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Контактные данные */}
        <div className={styles.section}>
          <div className={styles.sectionHeader}>
            <Mail className={styles.sectionIcon} />
            <h2 className={styles.sectionTitle}>Контактные данные для уведомлений</h2>
          </div>

          <div className={styles.sectionContent}>
            <div className={styles.settingItem}>
              <div className={styles.settingInfo}>
                <Mail className={styles.settingIcon} />
                <div>
                  <div className={styles.settingLabel}>Email для уведомлений</div>
                  <div className={styles.settingDescription}>Укажите email для получения уведомлений</div>
                </div>
              </div>
              <input
                type="email"
                value={settings.email}
                onChange={(e) => setSettings({ ...settings, email: e.target.value })}
                className={styles.input}
                placeholder="your@email.com"
              />
            </div>

            <div className={styles.settingItem}>
              <div className={styles.settingInfo}>
                <Send className={styles.settingIcon} />
                <div>
                  <div className={styles.settingLabel}>Telegram username</div>
                  <div className={styles.settingDescription}>@username для уведомлений в Telegram</div>
                </div>
              </div>
              <input
                type="text"
                value={settings.telegram}
                onChange={(e) => setSettings({ ...settings, telegram: e.target.value })}
                className={styles.input}
                placeholder="@username"
              />
            </div>
          </div>
        </div>

        {/* Управление данными */}
        <div className={styles.section}>
          <div className={styles.sectionHeader}>
            <Database className={styles.sectionIcon} />
            <h2 className={styles.sectionTitle}>Управление данными</h2>
          </div>

          <div className={styles.sectionContent}>
            <div className={styles.settingItem}>
              <div className={styles.settingInfo}>
                <Download className={styles.settingIcon} />
                <div>
                  <div className={styles.settingLabel}>Экспорт данных</div>
                  <div className={styles.settingDescription}>Скачать все данные в JSON</div>
                </div>
              </div>
              <button onClick={handleExport} className={styles.exportButton}>
                <Download className={styles.iconSmall} />
                Экспорт
              </button>
            </div>

            <div className={styles.settingItem}>
              <div className={styles.settingInfo}>
                <Trash2 className={`${styles.settingIcon} ${styles.dangerIcon}`} />
                <div>
                  <div className={`${styles.settingLabel} ${styles.dangerLabel}`}>Удалить все данные</div>
                  <div className={styles.settingDescription}>Полная очистка localStorage</div>
                </div>
              </div>
              <button onClick={handleClearData} className={styles.clearButton}>
                <Trash2 className={styles.iconSmall} />
                Очистить
              </button>
            </div>
          </div>
        </div>

        {/* Статистика хранилища */}
        <div className={styles.section}>
          <div className={styles.sectionHeader}>
            <Database className={styles.sectionIcon} />
            <h2 className={styles.sectionTitle}>Статистика хранилища</h2>
          </div>

          <div className={styles.statsGrid}>
            <div className={styles.statItem}>
              <div className={styles.statValue}>{products.length}</div>
              <div className={styles.statLabel}>Товары</div>
            </div>
            <div className={styles.statItem}>
              <div className={styles.statValue}>{snapshots.length}</div>
              <div className={styles.statLabel}>Снимки цен</div>
            </div>
            <div className={styles.statItem}>
              <div className={styles.statValue}>{rules.length}</div>
              <div className={styles.statLabel}>Правила</div>
            </div>
            <div className={styles.statItem}>
              <div className={styles.statValue}>{events.length}</div>
              <div className={styles.statLabel}>События</div>
            </div>
          </div>
        </div>

        {/* Кнопка сохранения */}
        <div className={styles.saveSection}>
          <button
            onClick={handleSaveSettings}
            disabled={saving}
            className={styles.saveButton}
          >
            <Save className={styles.iconSmall} />
            {saving ? 'Сохранение...' : 'Сохранить настройки'}
          </button>
          {saveMessage && (
            <div className={saveMessage.includes('успешно') ? styles.successMessage : styles.errorMessage}>
              {saveMessage}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
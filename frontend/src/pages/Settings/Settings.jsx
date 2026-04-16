// Settings.jsx
import { useState, useEffect, useCallback, memo } from 'react';
import { Download, Trash2, Bell, Database, Clock, Mail, Phone, Send, BellRing, Save, CheckCircle, AlertCircle, Edit2, X } from 'lucide-react';
import { getProducts, getPriceSnapshots, getAlertEvents, getAlertRules, saveUserSettings, getUserSettings, getParseInterval, setParseInterval, getUserContacts, updateUserContacts } from '../../lib/storage';
import { useAuth } from '../../context/AuthContext';
import styles from './Settings.module.css';

const InputField = memo(({ icon: Icon, label, name, type, placeholder, value, onChange, error }) => {
  const handleChange = (e) => {
    onChange(name, e.target.value);
  };

  return (
    <div className={styles.inputField}>
      <div className={styles.inputHeader}>
        <div className={styles.inputIconWrapper}>
          <Icon className={styles.inputIcon} />
        </div>
        <div className={styles.inputLabel}>{label}</div>
      </div>
      <div className={styles.inputWrapper}>
        <input
          type={type}
          value={value || ''}
          onChange={handleChange}
          className={`${styles.input} ${error ? styles.inputError : value ? styles.inputValid : ''}`}
          placeholder={placeholder}
        />
        {value && !error && (
          <CheckCircle className={styles.inputValidationIcon} />
        )}
        {error && (
          <AlertCircle className={styles.inputValidationIconError} />
        )}
      </div>
      {error && (
        <div className={styles.inputErrorText}>
          <AlertCircle className={styles.errorIconSmall} />
          {error}
        </div>
      )}
    </div>
  );
});

InputField.displayName = 'InputField';

export default function Settings() {
  const { user } = useAuth();
  const [products, setProducts] = useState([]);
  const [snapshots, setSnapshots] = useState([]);
  const [events, setEvents] = useState([]);
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [settings, setSettings] = useState({
    notificationInterval: '3600',
    emailNotifications: false,
    browserNotifications: false,
    telegramNotifications: false,
  });

  const [contacts, setContacts] = useState({
    email: '',
    phone: '',
    telegram: ''
  });
  const [editContacts, setEditContacts] = useState({
    email: '',
    phone: '',
    telegram: ''
  });
  const [contactsErrors, setContactsErrors] = useState({});
  const [isEditingContacts, setIsEditingContacts] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState('');

  const validateEmail = useCallback((email) => {
    if (!email) return true;
    const emailRegex = /^[^\s@]+@([^\s@]+\.)+[^\s@]+$/;
    return emailRegex.test(email);
  }, []);

  const validatePhone = useCallback((phone) => {
    if (!phone) return true;
    const phoneRegex = /^(\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$|^\+\d{1,3}\s?\d{10}$/;
    return phoneRegex.test(phone);
  }, []);

  const validateTelegram = useCallback((telegram) => {
    if (!telegram) return true;
    const tgRegex = /^@?[a-zA-Z0-9_]{5,32}$/;
    return tgRegex.test(telegram);
  }, []);

  const validateField = useCallback((field, value) => {
    switch (field) {
      case 'email':
        return validateEmail(value) ? '' : 'Введите корректный email';
      case 'phone':
        return validatePhone(value) ? '' : 'Введите корректный номер телефона';
      case 'telegram':
        return validateTelegram(value) ? '' : 'Введите корректный Telegram username';
      default:
        return '';
    }
  }, [validateEmail, validatePhone, validateTelegram]);

  const handleContactsFieldChange = useCallback((field, value) => {
    setEditContacts(prev => ({ ...prev, [field]: value }));
    const error = validateField(field, value);
    setContactsErrors(prev => ({ ...prev, [field]: error }));
  }, [validateField]);

  const validateContactsForm = useCallback(() => {
    const newErrors = {};
    let isValid = true;

    const fields = ['email', 'phone', 'telegram'];
    for (const field of fields) {
      const value = editContacts[field];
      const error = validateField(field, value);
      if (error) {
        newErrors[field] = error;
        isValid = false;
      }
    }

    setContactsErrors(newErrors);
    return isValid;
  }, [editContacts, validateField]);

  useEffect(() => {
    loadData();
    loadSettings();
    loadContacts();
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
      const parseInterval = await getParseInterval();
      const savedSettings = await getUserSettings();

      setSettings(prev => ({
        ...prev,
        ...savedSettings,
        notificationInterval: String(parseInterval),
      }));
    } catch (error) {
      console.error('Error loading settings:', error);
    }
  };

  const loadContacts = async () => {
    try {
      const data = await getUserContacts();
      if (data) {
        setContacts({
          email: data.email || '',
          phone: data.phone_number || '',
          telegram: data.tg || ''
        });
        setEditContacts({
          email: data.email || '',
          phone: data.phone_number || '',
          telegram: data.tg || ''
        });
      }
    } catch (error) {
      console.error('Error loading contacts:', error);
    }
  };

  const handleSaveSettings = async () => {
    setSaving(true);
    setSaveMessage('');

    try {
      const intervalSeconds = parseInt(settings.notificationInterval);
      await setParseInterval(intervalSeconds);
      await saveUserSettings(settings);

      setSaveMessage('Настройки успешно сохранены!');
      setTimeout(() => setSaveMessage(''), 3000);

      if (settings.browserNotifications && 'Notification' in window) {
        const permission = await Notification.requestPermission();
        if (permission === 'granted') {
          new Notification('PriceTracker', {
            body: 'Уведомления успешно включены!',
            icon: '/logo192.png'
          });
        }
      }
    } catch (error) {
      console.error('Error saving settings:', error);
      setSaveMessage('Ошибка при сохранении настроек: ' + error.message);
      setTimeout(() => setSaveMessage(''), 3000);
    } finally {
      setSaving(false);
    }
  };

  const handleSaveContacts = async () => {
    if (!validateContactsForm()) {
      return;
    }

    setSaving(true);
    setSaveMessage('');

    try {
      await updateUserContacts({
        email: editContacts.email,
        phone_number: editContacts.phone,
        tg: editContacts.telegram
      });

      setContacts({ ...editContacts });
      setIsEditingContacts(false);
      setSaveMessage('Контакты успешно сохранены!');
      setTimeout(() => setSaveMessage(''), 3000);
    } catch (error) {
      console.error('Error saving contacts:', error);
      setSaveMessage('Ошибка при сохранении контактов');
      setTimeout(() => setSaveMessage(''), 3000);
    } finally {
      setSaving(false);
    }
  };

  const handleCancelContactsEdit = () => {
    setEditContacts({ ...contacts });
    setIsEditingContacts(false);
    setContactsErrors({});
  };

  const handleExport = () => {
    const data = {
      products,
      snapshots,
      events,
      rules,
      settings,
      contacts,
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
                <option value="120">Раз в 2 минуты</option>
                <option value="3600">Каждый час</option>
                <option value="7200">Раз в 2 часа</option>
                <option value="21600">Каждые 6 часов</option>
                <option value="43200">Каждые 12 часов</option>
                <option value="86400">Раз в день</option>
              </select>
            </div>

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
            <h2 className={styles.sectionTitle}>Контактные данные</h2>
            {!isEditingContacts && (
              <button
                onClick={() => setIsEditingContacts(true)}
                className={styles.editContactsButton}
              >
                <Edit2 size={14} />
                Изменить
              </button>
            )}
          </div>

          <div className={styles.sectionContent}>
            {isEditingContacts ? (
              <div className={styles.contactsEditGrid}>
                <InputField
                  icon={Mail}
                  label="Email"
                  name="email"
                  type="email"
                  placeholder="example@mail.com"
                  value={editContacts.email}
                  onChange={handleContactsFieldChange}
                  error={contactsErrors.email}
                />

                <InputField
                  icon={Phone}
                  label="Телефон"
                  name="phone"
                  type="tel"
                  placeholder="+7 (999) 123-45-67"
                  value={editContacts.phone}
                  onChange={handleContactsFieldChange}
                  error={contactsErrors.phone}
                />

                <InputField
                  icon={Send}
                  label="Telegram"
                  name="telegram"
                  type="text"
                  placeholder="@username"
                  value={editContacts.telegram}
                  onChange={handleContactsFieldChange}
                  error={contactsErrors.telegram}
                />

                <div className={styles.contactsActions}>
                  <button
                    onClick={handleSaveContacts}
                    disabled={saving}
                    className={styles.saveContactsButton}
                  >
                    <Save size={14} />
                    {saving ? 'Сохранение...' : 'Сохранить'}
                  </button>
                  <button
                    onClick={handleCancelContactsEdit}
                    className={styles.cancelContactsButton}
                  >
                    <X size={14} />
                    Отмена
                  </button>
                </div>
              </div>
            ) : (
              <div className={styles.contactsDisplay}>
                <div className={styles.contactDisplayItem}>
                  <Mail size={16} />
                  <div className={styles.contactDisplayContent}>
                    <span className={styles.contactDisplayLabel}>Email</span>
                    <span className={styles.contactDisplayValue}>
                      {contacts.email || <span className={styles.notSpecified}>Не указан</span>}
                    </span>
                  </div>
                </div>

                <div className={styles.contactDisplayItem}>
                  <Phone size={16} />
                  <div className={styles.contactDisplayContent}>
                    <span className={styles.contactDisplayLabel}>Телефон</span>
                    <span className={styles.contactDisplayValue}>
                      {contacts.phone || <span className={styles.notSpecified}>Не указан</span>}
                    </span>
                  </div>
                </div>

                <div className={styles.contactDisplayItem}>
                  <Send size={16} />
                  <div className={styles.contactDisplayContent}>
                    <span className={styles.contactDisplayLabel}>Telegram</span>
                    <span className={styles.contactDisplayValue}>
                      {contacts.telegram ? (
                        <a
                          href={`https://t.me/${contacts.telegram.replace('@', '')}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className={styles.telegramLink}
                        >
                          {contacts.telegram}
                        </a>
                      ) : (
                        <span className={styles.notSpecified}>Не указан</span>
                      )}
                    </span>
                  </div>
                </div>
              </div>
            )}
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

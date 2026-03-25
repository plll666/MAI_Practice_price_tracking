// Profile.jsx
import { useState, useEffect, useCallback, memo } from 'react';
import { User, Mail, Phone, Send, Calendar, Package, Bell, TrendingDown, Award, Edit2, Save, X, CheckCircle, AlertCircle } from 'lucide-react';
import { getProducts, getPriceSnapshots, getAlertEvents, getAlertRules } from '../../lib/storage';
import { getTopPriceChanges } from '../../lib/analytics';
import { useAuth } from '../../context/AuthContext';
import { updateCurrentUser } from '../../lib/api';
import styles from './Profile.module.css';

// Меморизированный компонент поля ввода
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
      {!error && value && (
        <div className={styles.inputSuccessText}>
          <CheckCircle className={styles.successIconSmall} />
          Поле заполнено верно
        </div>
      )}
    </div>
  );
});

InputField.displayName = 'InputField';

export default function Profile() {
  const { user, loading: authLoading } = useAuth();
  const [products, setProducts] = useState([]);
  const [snapshots, setSnapshots] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [rules, setRules] = useState([]);
  const [topDrops, setTopDrops] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [profileData, setProfileData] = useState({
    name: '',
    email: '',
    phone: '',
    telegram: '',
    joinDate: '',
  });
  const [editData, setEditData] = useState({
    name: '',
    email: '',
    phone: '',
    telegram: '',
  });
  const [errors, setErrors] = useState({});
  const [updating, setUpdating] = useState(false);

  // Функции валидации
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

  const validateName = useCallback((name) => {
    if (!name) return true;
    const nameRegex = /^[a-zA-Zа-яА-Я\s\-]{2,50}$/;
    return nameRegex.test(name);
  }, []);

  const validateField = useCallback((field, value) => {
    switch (field) {
      case 'email':
        return validateEmail(value) ? '' : 'Введите корректный email (example@mail.com)';
      case 'phone':
        return validatePhone(value) ? '' : 'Введите корректный номер телефона (+7 999 123-45-67)';
      case 'telegram':
        return validateTelegram(value) ? '' : 'Введите корректный Telegram username (от 5 до 32 символов, только буквы, цифры и _)';
      case 'name':
        return validateName(value) ? '' : 'Имя должно содержать от 2 до 50 символов (только буквы, пробелы и дефисы)';
      default:
        return '';
    }
  }, [validateEmail, validatePhone, validateTelegram, validateName]);

  const handleFieldChange = useCallback((field, value) => {
    setEditData(prev => {
      const newData = { ...prev, [field]: value };
      return newData;
    });

    const error = validateField(field, value);
    setErrors(prev => ({ ...prev, [field]: error }));
  }, [validateField]);

  const validateForm = useCallback(() => {
    const newErrors = {};
    let isValid = true;

    const fields = ['name', 'email', 'phone', 'telegram'];
    for (const field of fields) {
      const value = editData[field];
      const error = validateField(field, value);
      if (error) {
        newErrors[field] = error;
        isValid = false;
      }
    }

    setErrors(newErrors);
    return isValid;
  }, [editData, validateField]);

  useEffect(() => {
    if (user) {
      const newProfileData = {
        name: user.full_name || '',
        email: user.email || '',
        phone: user.phone || '',
        telegram: user.telegram || '',
        joinDate: user.created_at ? new Date(user.created_at).toISOString().split('T')[0] : new Date().toISOString().split('T')[0],
      };
      setProfileData(newProfileData);
      setEditData({
        name: user.full_name || '',
        email: user.email || '',
        phone: user.phone || '',
        telegram: user.telegram || '',
      });
    }
  }, [user]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const productsData = await getProducts();
      const snapshotsData = await getPriceSnapshots();
      const alertsData = await getAlertEvents();
      const rulesData = await getAlertRules();
      const topDropsData = await getTopPriceChanges(30, 1, 'drops', productsData);

      setProducts(productsData);
      setSnapshots(snapshotsData);
      setAlerts(alertsData);
      setRules(rulesData);
      setTopDrops(topDropsData);
    } catch (error) {
      console.error('Error loading profile data:', error);
    } finally {
      setLoading(false);
    }
  };

  const totalSavings = topDrops.reduce((sum, drop) => sum + Math.abs(drop.changeAmount), 0);
  const activeAlerts = rules.filter(r => r.enabled).length;
  const memberDays = profileData.joinDate
    ? Math.floor(
        (new Date().getTime() - new Date(profileData.joinDate).getTime()) / (1000 * 60 * 60 * 24)
      )
    : 0;

  const handleSave = async () => {
    if (!validateForm()) {
      return;
    }

    setUpdating(true);
    try {
      await updateCurrentUser({
        full_name: editData.name,
        email: editData.email,
        phone: editData.phone,
        telegram: editData.telegram,
      });
      setProfileData(prev => ({
        ...prev,
        name: editData.name,
        email: editData.email,
        phone: editData.phone,
        telegram: editData.telegram,
      }));
      setIsEditing(false);
      setErrors({});
    } catch (error) {
      console.error('Failed to update profile:', error);
      alert('Ошибка при обновлении профиля');
    } finally {
      setUpdating(false);
    }
  };

  const handleCancel = useCallback(() => {
    setEditData({
      name: profileData.name,
      email: profileData.email,
      phone: profileData.phone,
      telegram: profileData.telegram,
    });
    setIsEditing(false);
    setErrors({});
  }, [profileData]);

  if (authLoading || loading) {
    return <div className={styles.container}>Загрузка...</div>;
  }

  const stats = [
    { label: 'Товары', value: products.length, icon: Package, color: 'blue' },
    { label: 'Уведомления', value: activeAlerts, icon: Bell, color: 'amber' },
    { label: 'История', value: snapshots.length, icon: TrendingDown, color: 'green' },
    { label: 'Дней с нами', value: memberDays, icon: Calendar, color: 'purple' },
  ];

  return (
    <div className={styles.container}>
      {/* Основная карточка профиля */}
      <div className={styles.profileCard}>
        <div className={styles.profileHeader}>
          <div className={styles.profileInfo}>
            <div className={styles.avatar}>
              <User className={styles.avatarIcon} />
            </div>
            <div>
              {isEditing ? (
                <input
                  type="text"
                  value={editData.name}
                  onChange={(e) => handleFieldChange('name', e.target.value)}
                  className={`${styles.editNameInput} ${errors.name ? styles.inputError : ''}`}
                  placeholder="Ваше имя"
                />
              ) : (
                <h1 className={styles.userName}>{profileData.name || 'Пользователь'}</h1>
              )}
            </div>
          </div>

          {!isEditing ? (
            <button onClick={() => setIsEditing(true)} className={styles.editButton}>
              <Edit2 className={styles.iconSmall} />
              Редактировать профиль
            </button>
          ) : (
            <div className={styles.editActions}>
              <button onClick={handleSave} disabled={updating} className={styles.saveButton}>
                <Save className={styles.iconSmall} />
                {updating ? 'Сохранение...' : 'Сохранить'}
              </button>
              <button onClick={handleCancel} className={styles.cancelButton}>
                <X className={styles.iconSmall} />
                Отмена
              </button>
            </div>
          )}
        </div>

        {/* Контактная информация */}
        <div className={styles.contactSection}>
          <h3 className={styles.sectionTitle}>Контактная информация</h3>

          {!isEditing ? (
            // Режим просмотра
            <div className={styles.contactGrid}>
              <div className={styles.contactItem}>
                <div className={styles.contactIconWrapper}>
                  <Mail className={styles.contactIcon} />
                </div>
                <div className={styles.contactContent}>
                  <p className={styles.contactLabel}>Email</p>
                  <p className={styles.contactValue}>{profileData.email || '—'}</p>
                </div>
              </div>

              <div className={styles.contactItem}>
                <div className={styles.contactIconWrapper}>
                  <Phone className={styles.contactIcon} />
                </div>
                <div className={styles.contactContent}>
                  <p className={styles.contactLabel}>Телефон</p>
                  <p className={styles.contactValue}>{profileData.phone || '—'}</p>
                </div>
              </div>

              <div className={styles.contactItem}>
                <div className={styles.contactIconWrapper}>
                  <Send className={styles.contactIcon} />
                </div>
                <div className={styles.contactContent}>
                  <p className={styles.contactLabel}>Telegram</p>
                  <p className={styles.contactValue}>
                    {profileData.telegram ? (
                      <a
                        href={`https://t.me/${profileData.telegram.replace('@', '')}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={styles.telegramLink}
                      >
                        {profileData.telegram}
                      </a>
                    ) : '—'}
                  </p>
                </div>
              </div>
            </div>
          ) : (
            // Режим редактирования
            <div className={styles.editContactGrid}>
              <InputField
                icon={Mail}
                label="Email"
                name="email"
                type="email"
                placeholder="example@mail.com"
                value={editData.email}
                onChange={handleFieldChange}
                error={errors.email}
              />

              <InputField
                icon={Phone}
                label="Телефон"
                name="phone"
                type="tel"
                placeholder="+7 (999) 123-45-67"
                value={editData.phone}
                onChange={handleFieldChange}
                error={errors.phone}
              />

              <InputField
                icon={Send}
                label="Telegram"
                name="telegram"
                type="text"
                placeholder="@username или username"
                value={editData.telegram}
                onChange={handleFieldChange}
                error={errors.telegram}
              />
            </div>
          )}
        </div>

        {/* Статистика */}
        <div className={styles.statsGrid}>
          {stats.map((stat) => {
            const Icon = stat.icon;
            return (
              <div key={stat.label} className={styles.statItem}>
                <Icon className={`${styles.statIcon} ${styles[`statIcon${stat.color}`]}`} />
                <div className={styles.statValue}>{stat.value}</div>
                <div className={styles.statLabel}>{stat.label}</div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Дополнительная информация */}
      <div className={styles.infoGrid}>
        <div className={styles.infoCard}>
          <Calendar className={styles.infoIcon} />
          <p className={styles.infoLabel}>Дата регистрации</p>
          <p className={styles.infoValue}>
            {profileData.joinDate
              ? new Date(profileData.joinDate).toLocaleDateString('ru-RU', {
                  day: 'numeric',
                  month: 'long',
                  year: 'numeric',
                })
              : 'Неизвестно'}
          </p>
        </div>

        <div className={styles.infoCard}>
          <Award className={styles.infoIcon} />
          <p className={styles.infoLabel}>Общая экономия</p>
          <p className={styles.infoValue}>{totalSavings.toLocaleString('ru-RU')} ₽</p>
        </div>

        <div className={styles.infoCard}>
          <Package className={styles.infoIcon} />
          <p className={styles.infoLabel}>Отслеживаемые товары</p>
          <p className={styles.infoValue}>{products.length}</p>
        </div>
      </div>

      {/* Активность */}
      <div className={styles.activityCard}>
        <h2 className={styles.activityTitle}>Активность</h2>
        <div className={styles.activityList}>
          <div className={styles.activityItem}>
            <span>Всего уведомлений получено</span>
            <span className={styles.activityValue}>{alerts.length}</span>
          </div>
          <div className={styles.activityItem}>
            <span>Активных правил уведомлений</span>
            <span className={styles.activityValue}>{activeAlerts}</span>
          </div>
          <div className={styles.activityItem}>
            <span>Записей истории цен</span>
            <span className={styles.activityValue}>{snapshots.length}</span>
          </div>
          <div className={styles.activityItem}>
            <span>Средняя частота проверок</span>
            <span className={styles.activityValue}>Каждые 12 часов</span>
          </div>
        </div>
      </div>
    </div>
  );
}
// frontend/src/pages/Auth/Register.jsx
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import styles from './Auth.module.css';

export default function Register() {
  const [formData, setFormData] = useState({
    login: '',
    password: '',
  });
  const [loading, setLoading] = useState(false);
  const [localError, setLocalError] = useState(null);
  const { register, error: authError } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setLocalError(null);

    try {
      console.log('Attempting to register with login:', formData.login);
      await register(formData);
      console.log('Registration successful, navigating to /');
      navigate('/');
    } catch (err) {
      console.error('Registration failed:', err);
      setLocalError(err.message || 'Ошибка регистрации. Проверьте подключение к серверу.');
    } finally {
      setLoading(false);
    }
  };

  const displayError = localError || authError;

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <div className={styles.header}>
          <h1 className={styles.title}>Регистрация</h1>
          <p className={styles.subtitle}>Создайте новую учетную запись</p>
        </div>

        <form onSubmit={handleSubmit} className={styles.form}>
          {displayError && (
            <div className={styles.errorMessage}>
              {displayError}
            </div>
          )}

          <div className={styles.formGroup}>
            <label className={styles.label}>Логин</label>
            <input
              type="text"
              name="login"
              required
              value={formData.login}
              onChange={handleChange}
              className={styles.input}
              placeholder="Введите логин"
            />
          </div>

          <div className={styles.formGroup}>
            <label className={styles.label}>Пароль</label>
            <input
              type="password"
              name="password"
              required
              value={formData.password}
              onChange={handleChange}
              className={styles.input}
              placeholder="••••••••"
            />
          </div>

          <button type="submit" disabled={loading} className={styles.submitButton}>
            {loading ? 'Регистрация...' : 'Зарегистрироваться'}
          </button>

          <p className={styles.footerText}>
            Уже есть аккаунт?{' '}
            <Link to="/login" className={styles.link}>
              Войти
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}
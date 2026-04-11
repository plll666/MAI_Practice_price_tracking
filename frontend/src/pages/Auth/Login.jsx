// frontend/src/pages/Auth/Login.jsx
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import styles from './Auth.module.css';

export default function Login() {
  const [formData, setFormData] = useState({
    login: '',
    password: '',
  });
  const [loading, setLoading] = useState(false);
  const [localError, setLocalError] = useState(null);  
  const { login: authLogin, error: authError } = useAuth();
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
      console.log('Attempting to login with:', formData.login);
      await authLogin(formData.login, formData.password); 
      console.log('Login successful, navigating to /');
      navigate('/');
    } catch (err) {
      console.error('Login failed:', err);
      setLocalError(err.message || 'Ошибка входа. Проверьте логин и пароль.');
    } finally {
      setLoading(false);
    }
  };

  const displayError = localError || authError;

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <div className={styles.header}>
          <h1 className={styles.title}>Вход</h1>
          <h2 className={styles.subtitle}>Войдите в свою учетную запись</h2>
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
            {loading ? 'Вход...' : 'Войти'}
          </button>

          <p className={styles.footerText}>
            Нет аккаунта?{' '}
            <Link to="/register" className={styles.link}>
              Зарегистрироваться
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}
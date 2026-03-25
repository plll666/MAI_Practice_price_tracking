// src/context/AuthContext.jsx
import React, { createContext, useState, useContext, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getCurrentUser, login as apiLogin, register as apiRegister, logout as apiLogout } from '../lib/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      setLoading(false);
      return;
    }

    try {
      const userData = await getCurrentUser();
      setUser(userData);
    } catch (err) {
      console.error('Auth check failed:', err);
      localStorage.removeItem('access_token');
      localStorage.removeItem('token_type');
      localStorage.removeItem('user_login');
    } finally {
      setLoading(false);
    }
  };

  const login = async (login, password) => {
    setError(null);
    try {
      await apiLogin(login, password);
      const userData = await getCurrentUser();
      setUser(userData);
      navigate('/');
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const register = async (userData) => {
    setError(null);
    try {
      await apiRegister(userData);
      await login(userData.login, userData.password);
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const logout = () => {
    apiLogout();
    setUser(null);
    navigate('/login');
  };

  const value = {
    user,
    loading,
    error,
    login,
    register,
    logout,
    isAuthenticated: !!user,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
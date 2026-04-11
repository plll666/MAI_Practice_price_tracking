// src/lib/api.js
const API_URL = "/api"; 

const handleResponse = async (response) => {
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }
  return response.json();
};

// ============= Аутентификация =============
export const register = async (login, password) => {
  const response = await fetch(`${API_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ login, password }),
  });

  const data = await handleResponse(response);

  if (data.access_token) {
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('token_type', data.token_type);
    localStorage.setItem('user_login', login);
  }

  return data;
};

export const login = async (login, password) => {
  const formData = new URLSearchParams();
  formData.append('username', login);
  formData.append('password', password);

  const response = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData,
  });
  const data = await handleResponse(response);

  if (data.access_token) {
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('token_type', data.token_type);
    localStorage.setItem('user_login', login);
  }

  return data;
};

export const logout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('token_type');
  localStorage.removeItem('user_login');
  window.location.href = '/login';
};
export const getCurrentUser = async () => {
  const token = localStorage.getItem('access_token');
  const login = localStorage.getItem('user_login');
  if (!token) return null;
  return {
    login: login,
    is_active: true
  };
};
export const updateCurrentUser = async (userData) => {
  console.log('Update user logic for:', userData);
  return userData;
};
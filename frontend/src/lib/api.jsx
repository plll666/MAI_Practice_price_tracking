// src/lib/api.js
const handleResponse = async (response) => {
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }
  return response.json();
};

// ============= Аутентификация =============
export const register = async (userData) => {
  const response = await fetch(`/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      login: userData.login,
      password: userData.password,
    }),
  });
  return handleResponse(response);
};

export const login = async (login, password) => {
  const formData = new URLSearchParams();
  formData.append('username', login);
  formData.append('password', password);

  const response = await fetch(`/auth/login`, {
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

// ============= Пользователь (заглушка) =============
export const getCurrentUser = async () => {
  const login = localStorage.getItem('user_login');
  return {
    id: 1,
    login: login || 'user',
    full_name: login || 'User',
    email: `${login || 'user'}@example.com`,
    is_active: true,
    created_at: new Date().toISOString(),
  };
};

export const updateCurrentUser = async (userData) => {
  console.log('Update user:', userData);
  return userData;
};
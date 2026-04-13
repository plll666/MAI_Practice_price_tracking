// src/lib/storage.js

const API_BASE = '/api';
const getAuthHeaders = () => {
  const token = localStorage.getItem('access_token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
  };
};

const mapProduct = (p) => {
  if (!p) return null;
  
  return {
    ...p,
    id: p.id?.toString(), 
    name: p.title || 'Без названия',
    currentPrice: p.price || 0,
    imageUrl: p.image_url || `https://via.placeholder.com/200?text=No+Image`,
    shop: p.brand || 'Unknown',
    category: p.category || 'Товары',
    tags: Array.isArray(p.tags) ? p.tags : [],
    currency: '₽'
  };
};

export const getProducts = async () => {
  try {
    const response = await fetch(`${API_BASE}/products/`, {
      headers: getAuthHeaders() // Передаем токен
    });    
    
    if (response.status === 401) {
      console.error('Неавторизован или токен истек');
      return [];
    }

    if (!response.ok) return [];
    
    const data = await response.json();
    const items = data.products || (Array.isArray(data) ? data : []);
    
    return items.map(mapProduct).filter(Boolean);
  } catch (error) {
    console.error('Failed to fetch products:', error);
    return [];
  }
};

export const getProduct = async (id) => {
  try {
    const response = await fetch(`${API_BASE}/products/${id}`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) return null;
    const data = await response.json();
    return mapProduct(data);
  } catch (error) {
    console.error('Failed to get product:', error);
    return null;
  }
};

export const addProductByUrl = async (url) => {
  try {
    const response = await fetch(`${API_BASE}/products/new_link`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ url: url })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Ошибка при добавлении ссылки');
    }

    const data = await response.json();
    return mapProduct(data);
  } catch (error) {
    console.error('Error adding product:', error);
    throw error;
  }
};

export const getPriceSnapshots = async (productId) => {
  return []; 
};

export const deleteProduct = async (id) => {
  try {
    const response = await fetch(`${API_BASE}/products/${id}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to delete');
  } catch (error) {
    console.error('Failed to delete product:', error);
    throw error;
  }
};

export const saveProduct = async (product) => {
  console.log('Save product called', product);
  return product;
};

export const getAlertRules = async (productId) => [];
export const saveAlertRule = async (rule) => rule;
export const deleteAlertRule = async (id) => {};
export const getAlertEvents = async () => [];
export const markAllAlertsAsRead = async () => {};

export const getUserSettings = async () => {
  const settings = localStorage.getItem('user_settings');
  return settings ? JSON.parse(settings) : { notifications: true, theme: 'light' };
};

export const saveUserSettings = async (s) => {
  localStorage.setItem('user_settings', JSON.stringify(s));
};

export const initializeDemoData = async () => {
  console.log('Backend mode: skipping demo data initialization');
};
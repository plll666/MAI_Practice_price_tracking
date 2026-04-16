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
    currentPrice: p.price || p.current_price || 0,
    imageUrl: p.image_url || `https://via.placeholder.com/200?text=No+Image`,
    shop: p.brand || 'Unknown',
    category: p.category || 'Товары',
    tags: Array.isArray(p.tags) ? p.tags : [],
    currency: '₽',
    targetPrice: p.target_price || null
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

export const addProductByUrl = async (url, targetPrice = null) => {
  try {
    const body = { url };
    if (targetPrice) {
      body.target_price = targetPrice;
    }
    const response = await fetch(`${API_BASE}/products/new_link`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(body)
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

export const getPriceSnapshots = async (productId, days = 30) => {
  if (!productId || productId === 'undefined' || productId === 'null') {
    console.warn('getPriceSnapshots: пропуск запроса, некорректный productId:', productId);
    return [];
  }
  
  try {
    const response = await fetch(`${API_BASE}/products/${productId}/history?days=${days}`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) return [];
    const data = await response.json();
    if (data.history && Array.isArray(data.history)) {
      return data.history.map(h => ({
        timestamp: h.date,
        price: h.price
      }));
    }
    return [];
  } catch (error) {
    console.error('Failed to fetch price snapshots:', error);
    return [];
  }
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

export const updateTargetPrice = async (productId, targetPrice) => {
  try {
    const body = {};
    if (targetPrice !== null && targetPrice !== undefined && targetPrice !== '') {
      body.target_price = parseFloat(targetPrice);
    } else {
      body.target_price = null;
    }
    
    const response = await fetch(`${API_BASE}/products/${productId}/target-price`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(body)
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Ошибка сохранения');
    }

    return await response.json();
  } catch (error) {
    console.error('Error updating target price:', error);
    throw error;
  }
};

export const getAlertRules = async (productId) => [];
export const saveAlertRule = async (rule) => rule;
export const deleteAlertRule = async (id) => {};

export const getAlertEvents = async () => {
  try {
    const response = await fetch(`${API_BASE}/alerts/`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) return [];
    const data = await response.json();
    return data.map(alert => ({
      id: alert.id,
      message: alert.message,
      timestamp: alert.created_at,
      read: alert.is_read,
      productId: alert.product_id,
      imageUrl: alert.image_url,
      currentPrice: alert.current_price,
      targetPrice: alert.target_price
    }));
  } catch (error) {
    console.error('Failed to fetch alerts:', error);
    return [];
  }
};

export const markAllAlertsAsRead = async () => {
  try {
    const response = await fetch(`${API_BASE}/alerts/read-all`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to mark all as read');
    return await response.json();
  } catch (error) {
    console.error('Failed to mark all alerts as read:', error);
  }
};

export const markAlertAsRead = async (alertId) => {
  try {
    const response = await fetch(`${API_BASE}/alerts/${alertId}/read`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to mark as read');
    return await response.json();
  } catch (error) {
    console.error('Failed to mark alert as read:', error);
  }
};

export const getUserSettings = async () => {
  const settings = localStorage.getItem('user_settings');
  return settings ? JSON.parse(settings) : { notifications: true, theme: 'light' };
};

export const saveUserSettings = async (s) => {
  localStorage.setItem('user_settings', JSON.stringify(s));
};

// src/lib/storage.js

// ... остальной код ...

export const getParseInterval = async () => {
  try {
    const response = await fetch(`${API_BASE}/settings/parse-interval`, {
      method: 'GET',
      headers: getAuthHeaders()
    });
    if (!response.ok) return 3600; // 3600 секунд = 1 час (дефолт)
    const data = await response.json();
    return data.parse_interval || 3600;
  } catch (error) {
    console.error('Failed to get parse interval:', error);
    return 3600; // Дефолт 1 час
  }
};

export const setParseInterval = async (interval) => {
  try {
    const response = await fetch(`${API_BASE}/settings/parse-interval`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ parse_interval: interval })
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to set parse interval');
    }
    return await response.json();
  } catch (error) {
    console.error('Failed to set parse interval:', error);
    throw error;
  }
};

export const initializeDemoData = async () => {
  console.log('Backend mode: skipping demo data initialization');
};

export const getProductPrices = async () => {
  try {
    const response = await fetch(`${API_BASE}/products/prices`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) return [];
    const data = await response.json();
    return data.products || [];
  } catch (error) {
    console.error('Failed to fetch product prices:', error);
    return [];
  }
};

export const getUserContacts = async () => {
  try {
    const response = await fetch(`${API_BASE}/users/me/contacts`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) return null;
    return response.json();
  } catch (error) {
    console.error('Failed to fetch contacts:', error);
    return null;
  }
};

export const updateUserContacts = async (contacts) => {
  try {
    const response = await fetch(`${API_BASE}/users/me/contacts`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(contacts)
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Ошибка сохранения контактов');
    }
    return response.json();
  } catch (error) {
    console.error('Failed to update contacts:', error);
    throw error;
  }
};

export const getAnalytics = async (days = 30) => {
  try {
    const response = await fetch(`${API_BASE}/analytics?days=${days}`, {
      headers: getAuthHeaders()
    });
    if (response.status === 401) {
      console.warn('Analytics: не авторизован');
      return null;
    }
    if (!response.ok) {
      throw new Error('Failed to fetch analytics');
    }
    return response.json();
  } catch (error) {
    console.error('Failed to fetch analytics:', error);
    return {
      summary: {
        total_products: 0,
        total_shops: 0,
        total_savings: 0,
        avg_price_change: 0,
        avg_price: 0,
        min_price: 0,
        max_price: 0
      },
      by_shop: [],
      price_trend: [],
      top_drops: [],
      top_increases: [],
      price_histogram: [],
      changes_timeline: []
    };
  }
};
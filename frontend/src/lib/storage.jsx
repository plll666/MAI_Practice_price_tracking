// src/lib/storage.js
// Products
export const getProducts = async () => {
  try {
    return JSON.parse(localStorage.getItem('price_tracker_products') || '[]');
  } catch (error) {
    console.error('Failed to get products:', error);
    return [];
  }
};

export const getProduct = async (id) => {
  try {
    const products = await getProducts();
    return products.find(p => p.id === id) || null;
  } catch (error) {
    console.error('Failed to get product:', error);
    return null;
  }
};

export const saveProduct = async (product) => {
  try {
    const products = await getProducts();
    const existingIndex = products.findIndex(p => p.id === product.id);

    if (existingIndex >= 0) {
      products[existingIndex] = product;
    } else {
      products.push(product);
    }

    localStorage.setItem('price_tracker_products', JSON.stringify(products));
    return product;
  } catch (error) {
    console.error('Failed to save product:', error);
    throw error;
  }
};

export const deleteProduct = async (id) => {
  try {
    const products = await getProducts();
    const filtered = products.filter(p => p.id !== id);
    localStorage.setItem('price_tracker_products', JSON.stringify(filtered));
  } catch (error) {
    console.error('Failed to delete product:', error);
    throw error;
  }
};

// Price Snapshots
export const getPriceSnapshots = async (productId) => {
  try {
    const snapshots = JSON.parse(localStorage.getItem('price_tracker_snapshots') || '[]');
    return productId ? snapshots.filter(s => s.productId === productId) : snapshots;
  } catch (error) {
    console.error('Failed to get price snapshots:', error);
    return [];
  }
};

export const savePriceSnapshot = async (snapshot) => {
  try {
    const snapshots = JSON.parse(localStorage.getItem('price_tracker_snapshots') || '[]');
    snapshots.push(snapshot);
    localStorage.setItem('price_tracker_snapshots', JSON.stringify(snapshots));
  } catch (error) {
    console.error('Failed to save price snapshot:', error);
  }
};

// Alert Rules
export const getAlertRules = async (productId) => {
  try {
    const rules = JSON.parse(localStorage.getItem('price_tracker_alert_rules') || '[]');
    return productId ? rules.filter(r => r.productId === productId) : rules;
  } catch (error) {
    console.error('Failed to get alert rules:', error);
    return [];
  }
};

export const saveAlertRule = async (rule) => {
  try {
    const rules = await getAlertRules();
    const existingIndex = rules.findIndex(r => r.id === rule.id);

    if (existingIndex >= 0) {
      rules[existingIndex] = rule;
    } else {
      rule.id = `rule-${Date.now()}`;
      rules.push(rule);
    }

    localStorage.setItem('price_tracker_alert_rules', JSON.stringify(rules));
    return rule;
  } catch (error) {
    console.error('Failed to save alert rule:', error);
    throw error;
  }
};

export const deleteAlertRule = async (id) => {
  try {
    const rules = await getAlertRules();
    const filtered = rules.filter(r => r.id !== id);
    localStorage.setItem('price_tracker_alert_rules', JSON.stringify(filtered));
  } catch (error) {
    console.error('Failed to delete alert rule:', error);
    throw error;
  }
};

// Alert Events
export const getAlertEvents = async () => {
  try {
    return JSON.parse(localStorage.getItem('price_tracker_alert_events') || '[]');
  } catch (error) {
    console.error('Failed to get alert events:', error);
    return [];
  }
};

export const markAllAlertsAsRead = async () => {
  try {
    const events = await getAlertEvents();
    const updated = events.map(e => ({ ...e, read: true }));
    localStorage.setItem('price_tracker_alert_events', JSON.stringify(updated));
  } catch (error) {
    console.error('Failed to mark all alerts as read:', error);
    throw error;
  }
};

// Initialize demo data
export const initializeDemoData = async () => {
  const products = await getProducts();
  if (products.length > 0) return;

  console.log('Initializing demo data...');
  const now = new Date().toISOString();

  const demoProducts = [
    {
      id: 'product-1',
      name: 'iPhone 15 Pro 256GB',
      url: 'https://example.com/iphone-15-pro',
      shop: 'TechStore',
      category: 'Электроника',
      currentPrice: 89990,
      currency: 'RUB',
      imageUrl: 'https://images.unsplash.com/photo-1592286927505-b0501d7433af?w=400',
      isAvailable: true,
      tags: ['apple', 'phone'],
      addedAt: now,
      lastChecked: now,
    },
    {
      id: 'product-2',
      name: 'Sony WH-1000XM5',
      url: 'https://example.com/sony-headphones',
      shop: 'AudioShop',
      category: 'Аудио',
      currentPrice: 29990,
      currency: 'RUB',
      imageUrl: 'https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=400',
      isAvailable: true,
      tags: ['sony', 'headphones'],
      addedAt: now,
      lastChecked: now,
    },
    {
      id: 'product-3',
      name: 'Samsung 4K TV 55"',
      url: 'https://example.com/samsung-tv',
      shop: 'ElectroMarket',
      category: 'ТВ',
      currentPrice: 54990,
      currency: 'RUB',
      imageUrl: 'https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=400',
      isAvailable: true,
      tags: ['samsung', 'tv'],
      addedAt: now,
      lastChecked: now,
    },
  ];

  for (const product of demoProducts) {
    await saveProduct(product);

    // Create price history
    const snapshots = [];
    for (let i = 0; i <= 30; i++) {
      const variation = (Math.random() - 0.5) * 0.15;
      const price = Math.round(product.currentPrice * (1 + variation));
      const timestamp = new Date(Date.now() - i * 24 * 60 * 60 * 1000).toISOString();
      snapshots.push({
        id: `${product.id}-${i}`,
        productId: product.id,
        price: price,
        currency: product.currency,
        timestamp: timestamp,
        isAvailable: true,
      });
    }
    localStorage.setItem('price_tracker_snapshots', JSON.stringify([
      ...JSON.parse(localStorage.getItem('price_tracker_snapshots') || '[]'),
      ...snapshots
    ]));
  }

  console.log('Demo data initialized');
};

// Auto-initialize
if (typeof window !== 'undefined') {
  initializeDemoData().catch(console.error);
}

export const getUserSettings = async () => {
  try {
    const settings = localStorage.getItem('price_tracker_user_settings');
    return settings ? JSON.parse(settings) : null;
  } catch (error) {
    console.error('Failed to get user settings:', error);
    return null;
  }
};

export const saveUserSettings = async (settings) => {
  try {
    localStorage.setItem('price_tracker_user_settings', JSON.stringify(settings));
    return settings;
  } catch (error) {
    console.error('Failed to save user settings:', error);
    throw error;
  }
};
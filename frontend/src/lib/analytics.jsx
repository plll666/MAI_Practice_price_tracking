// analytics.js
import { getPriceSnapshots } from './storage';

export const calculatePriceStats = (snapshots) => {
  if (!snapshots || snapshots.length === 0) return null;

  const sortedSnapshots = [...snapshots].sort(
    (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
  );

  const prices = sortedSnapshots.map(s => s.price);
  const current = prices[prices.length - 1];
  const min = Math.min(...prices);
  const max = Math.max(...prices);
  const avg = Math.round(prices.reduce((sum, p) => sum + p, 0) / prices.length);

  const now = new Date();
  const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
  const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);

  const snapshot7d = sortedSnapshots.find(
    s => new Date(s.timestamp) >= sevenDaysAgo
  ) || sortedSnapshots[0];

  const snapshot30d = sortedSnapshots.find(
    s => new Date(s.timestamp) >= thirtyDaysAgo
  ) || sortedSnapshots[0];

  const change7d = current - snapshot7d.price;
  const change30d = current - snapshot30d.price;
  const changePercent7d = snapshot7d.price ? (change7d / snapshot7d.price) * 100 : 0;
  const changePercent30d = snapshot30d.price ? (change30d / snapshot30d.price) * 100 : 0;

  return {
    min,
    max,
    avg,
    current,
    change7d,
    change30d,
    changePercent7d,
    changePercent30d,
  };
};

export const getTopPriceChanges = async (period = 30, limit = 5, type = 'drops', products) => {
  const changes = [];

  for (const product of products) {
    const snapshots = await getPriceSnapshots(product.id);
    const stats = calculatePriceStats(snapshots);
    if (!stats) continue;

    const changePercent = period === 7 ? stats.changePercent7d : stats.changePercent30d;
    const changeAmount = period === 7 ? stats.change7d : stats.change30d;

    changes.push({
      product,
      changePercent,
      changeAmount,
      period,
    });
  }

  const sorted = changes.sort((a, b) =>
    type === 'drops'
      ? a.changePercent - b.changePercent
      : b.changePercent - a.changePercent
  );

  return sorted.slice(0, limit);
};

export const getProductsByCategory = (products) => {
  const categories = {};

  for (const product of products) {
    categories[product.category] = (categories[product.category] || 0) + 1;
  }

  return categories;
};

export const getProductsByShop = (products) => {
  const shops = {};

  for (const product of products) {
    shops[product.shop] = (shops[product.shop] || 0) + 1;
  }

  return shops;
};

export const getAveragePriceByCategory = (products) => {
  const categoryPrices = {};

  for (const product of products) {
    if (!categoryPrices[product.category]) {
      categoryPrices[product.category] = [];
    }
    categoryPrices[product.category].push(product.currentPrice);
  }

  const result = {};
  for (const [category, prices] of Object.entries(categoryPrices)) {
    result[category] = Math.round(
      prices.reduce((sum, p) => sum + p, 0) / prices.length
    );
  }

  return result;
};

export const formatPrice = (price, currency = 'RUB') => {
  const symbols = {
    RUB: '₽',
    USD: '$',
    EUR: '€',
  };

  return `${price.toLocaleString('ru-RU')} ${symbols[currency] || currency}`;
};

export const formatPriceChange = (change, percent) => {
  const sign = change > 0 ? '+' : '';
  return `${sign}${change.toLocaleString('ru-RU')} (${sign}${percent.toFixed(1)}%)`;
};
// Analytics.jsx
import { Link } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { TrendingDown, TrendingUp, Package, DollarSign, ShoppingBag } from 'lucide-react';
import { getProducts } from '../../lib/storage';
import { getTopPriceChanges, formatPrice, getProductsByCategory, getAveragePriceByCategory } from '../../lib/analytics';
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import styles from './Analytics.module.css';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16'];

export default function Analytics() {
  const [products, setProducts] = useState([]);
  const [topDrops, setTopDrops] = useState([]);
  const [topIncreases, setTopIncreases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [categoryData, setCategoryData] = useState({});
  const [avgPriceByCategory, setAvgPriceByCategory] = useState({});

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const productsData = await getProducts();
      setProducts(productsData);
      setCategoryData(getProductsByCategory(productsData));
      setAvgPriceByCategory(getAveragePriceByCategory(productsData));

      const topDropsData = await getTopPriceChanges(30, 5, 'drops', productsData);
      const topIncreasesData = await getTopPriceChanges(30, 5, 'increases', productsData);

      setTopDrops(topDropsData);
      setTopIncreases(topIncreasesData);
    } catch (error) {
      console.error('Error loading analytics data:', error);
    } finally {
      setLoading(false);
    }
  };

  const categoryChartData = Object.entries(categoryData).map(([name, value]) => ({
    name: name.length > 15 ? name.slice(0, 12) + '...' : name,
    fullName: name,
    value,
  }));

  const avgPriceChartData = Object.entries(avgPriceByCategory).map(([name, avgPrice]) => ({
    name: name.length > 15 ? name.slice(0, 12) + '...' : name,
    fullName: name,
    avgPrice,
  }));

  const priceTrendData = [
    { month: 'Янв', avgPrice: 24500 },
    { month: 'Фев', avgPrice: 23800 },
    { month: 'Мар', avgPrice: 24200 },
    { month: 'Апр', avgPrice: 23500 },
    { month: 'Май', avgPrice: 22800 },
    { month: 'Июн', avgPrice: 22500 },
  ];

  const stats = [
    {
      label: 'Всего товаров',
      value: products.length,
      icon: Package,
      color: 'blue',
    },
    {
      label: 'Категории',
      value: Object.keys(categoryData).length,
      icon: ShoppingBag,
      color: 'purple',
    },
    {
      label: 'Снижения цен',
      value: topDrops.filter(d => d.changePercent < -5).length,
      icon: TrendingDown,
      color: 'green',
    },
    {
      label: 'Экономия (30д)',
      value: topDrops.reduce((sum, d) => sum + Math.abs(d.changeAmount), 0).toLocaleString('ru-RU') + ' ₽',
      icon: DollarSign,
      color: 'emerald',
    },
  ];

  if (loading) {
    return <div className={styles.container}>Загрузка...</div>;
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>Аналитика</h1>
        <p className={styles.subtitle}>Статистика и тренды изменения цен</p>
      </div>

      <div className={styles.statsGrid}>
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.label} className={`${styles.statCard} ${styles[`statCard${stat.color}`]}`}>
              <div className={styles.statHeader}>
                <Icon className={`${styles.statIcon} ${styles[`statIcon${stat.color}`]}`} />
                <span className={styles.statValue}>{stat.value}</span>
              </div>
              <p className={styles.statLabel}>{stat.label}</p>
            </div>
          );
        })}
      </div>

      <div className={styles.chartsGrid}>
        <div className={styles.chartCard}>
          <h2 className={styles.chartTitle}>Товары по категориям</h2>
          {categoryChartData.length === 0 ? (
            <div className={styles.chartEmpty}>Нет данных</div>
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={categoryChartData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => percent > 0.05 ? `${name} (${(percent * 100).toFixed(0)}%)` : ''}
                  outerRadius={100}
                  dataKey="value"
                >
                  {categoryChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: 'var(--card)', border: `1px solid var(--border)`, borderRadius: '8px' }}
                  formatter={(value, name, props) => [`${value} товаров`, props.payload.fullName]}
                />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className={styles.chartCard}>
          <h2 className={styles.chartTitle}>Средняя цена по категориям</h2>
          {avgPriceChartData.length === 0 ? (
            <div className={styles.chartEmpty}>Нет данных</div>
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={avgPriceChartData} layout="vertical" margin={{ left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" horizontal={false} />
                <XAxis type="number" stroke="var(--muted-foreground)" tickFormatter={(value) => `${value.toLocaleString()}₽`} />
                <YAxis type="category" dataKey="name" stroke="var(--muted-foreground)" width={80} />
                <Tooltip
                  contentStyle={{ backgroundColor: 'var(--card)', border: `1px solid var(--border)`, borderRadius: '8px' }}
                  formatter={(value) => [`${value.toLocaleString()} ₽`, 'Средняя цена']}
                  labelFormatter={(label, payload) => payload[0]?.payload.fullName || label}
                />
                <Bar dataKey="avgPrice" fill="#3b82f6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      <div className={styles.trendCard}>
        <h2 className={styles.chartTitle}>Динамика средней цены</h2>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={priceTrendData}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis dataKey="month" stroke="var(--muted-foreground)" />
            <YAxis stroke="var(--muted-foreground)" tickFormatter={(value) => `${value.toLocaleString()}₽`} />
            <Tooltip
              contentStyle={{ backgroundColor: 'var(--card)', border: `1px solid var(--border)`, borderRadius: '8px' }}
              formatter={(value) => [`${value.toLocaleString()} ₽`, 'Средняя цена']}
            />
            <Line type="monotone" dataKey="avgPrice" stroke="#10b981" strokeWidth={2} dot={{ fill: '#10b981', r: 4 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className={styles.topChangesGrid}>
        <div className={styles.topCard}>
          <div className={`${styles.topHeader} ${styles.topHeaderGreen}`}>
            <TrendingDown className={styles.topHeaderIconGreen} />
            <h2 className={styles.topHeaderTitle}>ТОП снижений цен (30 дн)</h2>
          </div>
          <div className={styles.topContent}>
            {topDrops.length === 0 ? (
              <div className={styles.topEmpty}>Нет данных</div>
            ) : (
              <div className={styles.topList}>
                {topDrops.map((change, index) => (
                  <Link key={change.product.id} to={`/products/${change.product.id}`} className={styles.topItem}>
                    <div className={styles.topRank}>{index + 1}</div>
                    <img src={change.product.imageUrl} alt={change.product.name} className={styles.topImage} />
                    <div className={styles.topInfo}>
                      <div className={styles.topName}>{change.product.name}</div>
                      <div className={styles.topShop}>{change.product.shop}</div>
                    </div>
                    <div className={styles.topStats}>
                      <div className={styles.topPercentGreen}>{change.changePercent.toFixed(1)}%</div>
                      <div className={styles.topPrice}>{formatPrice(change.product.currentPrice, change.product.currency)}</div>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className={styles.topCard}>
          <div className={`${styles.topHeader} ${styles.topHeaderRed}`}>
            <TrendingUp className={styles.topHeaderIconRed} />
            <h2 className={styles.topHeaderTitle}>ТОП повышений цен (30 дн)</h2>
          </div>
          <div className={styles.topContent}>
            {topIncreases.length === 0 ? (
              <div className={styles.topEmpty}>Нет данных</div>
            ) : (
              <div className={styles.topList}>
                {topIncreases.map((change, index) => (
                  <Link key={change.product.id} to={`/products/${change.product.id}`} className={styles.topItem}>
                    <div className={styles.topRank}>{index + 1}</div>
                    <img src={change.product.imageUrl} alt={change.product.name} className={styles.topImage} />
                    <div className={styles.topInfo}>
                      <div className={styles.topName}>{change.product.name}</div>
                      <div className={styles.topShop}>{change.product.shop}</div>
                    </div>
                    <div className={styles.topStats}>
                      <div className={styles.topPercentRed}>+{change.changePercent.toFixed(1)}%</div>
                      <div className={styles.topPrice}>{formatPrice(change.product.currentPrice, change.product.currency)}</div>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
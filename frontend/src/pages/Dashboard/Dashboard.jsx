// Dashboard.jsx - добавьте useEffect для прослушивания события обновления
import { Link } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { Package, TrendingDown, TrendingUp, Bell, ArrowRight, AlertCircle, ShoppingBag, Plus } from 'lucide-react';
import { getProducts, getAlertEvents } from '../../lib/storage';
import { formatPrice, getTopPriceChanges } from '../../lib/analytics';
import styles from './Dashboard.module.css';

export default function Dashboard() {
  const [products, setProducts] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [topDrops, setTopDrops] = useState([]);
  const [topIncreases, setTopIncreases] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const productsData = await getProducts();
      const alertsData = await getAlertEvents();

      const topDropsData = await getTopPriceChanges(30, 3, 'drops', productsData);
      const topIncreasesData = await getTopPriceChanges(30, 3, 'increases', productsData);

      setProducts(productsData);
      setAlerts(alertsData.filter(a => !a.read));
      setTopDrops(topDropsData);
      setTopIncreases(topIncreasesData);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();

    // Слушаем событие обновления дашборда
    const handleRefresh = () => {
      console.log('Refreshing dashboard...');
      loadData();
    };

    // Слушаем изменения в localStorage
    const handleStorageChange = (e) => {
      if (e.key === 'refresh_timestamp') {
        loadData();
      }
    };

    window.addEventListener('refreshDashboard', handleRefresh);
    window.addEventListener('storage', handleStorageChange);

    return () => {
      window.removeEventListener('refreshDashboard', handleRefresh);
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

  const uniqueCategories = [...new Set(products.map(p => p.category))];
  const priceDropCount = topDrops.filter(d => d.changePercent < -5).length;

  const stats = [
    { label: 'Товары', value: products.length, icon: Package, color: 'blue' },
    { label: 'Категории', value: uniqueCategories.length, icon: ShoppingBag, color: 'purple' },
    { label: 'Снижения', value: priceDropCount, icon: TrendingDown, color: 'green' },
    { label: 'Уведомления', value: alerts.length, icon: Bell, color: 'amber' },
  ];

  if (loading) {
    return <div className={styles.container}>Загрузка...</div>;
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Дашборд</h1>
          <p className={styles.subtitle}>Отслеживание цен на товары</p>
        </div>
        <Link to="/add-product" className={styles.addButton}>
          <Plus className={styles.addIcon} />
          Добавить товар
        </Link>
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

      <div className={styles.changesGrid}>
        <div className={styles.changeCard}>
          <div className={`${styles.changeHeader} ${styles.changeHeaderGreen}`}>
            <div className={styles.changeHeaderLeft}>
              <TrendingDown className={styles.changeHeaderIconGreen} />
              <h2 className={styles.changeHeaderTitle}>Снижения цен</h2>
            </div>
            <Link to="/analytics" className={styles.changeLink}>
              Все <ArrowRight className={styles.linkIcon} />
            </Link>
          </div>
          <div className={styles.changeContent}>
            {topDrops.length === 0 ? (
              <div className={styles.emptyState}>
                <AlertCircle className={styles.emptyIcon} />
                <p>Нет данных о снижениях</p>
              </div>
            ) : (
              <div className={styles.changeList}>
                {topDrops.map((change) => (
                  <Link key={change.product.id} to={`/products/${change.product.id}`} className={styles.changeItem}>
                    <img src={change.product.imageUrl} alt={change.product.name} className={styles.changeImage} />
                    <div className={styles.changeInfo}>
                      <div className={styles.changeName}>{change.product.name}</div>
                      <div className={styles.changeShop}>{change.product.shop}</div>
                    </div>
                    <div className={styles.changeStats}>
                      <div className={styles.changePercentGreen}>{change.changePercent.toFixed(1)}%</div>
                      <div className={styles.changePrice}>{formatPrice(change.product.currentPrice, change.product.currency)}</div>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className={styles.changeCard}>
          <div className={`${styles.changeHeader} ${styles.changeHeaderRed}`}>
            <div className={styles.changeHeaderLeft}>
              <TrendingUp className={styles.changeHeaderIconRed} />
              <h2 className={styles.changeHeaderTitle}>Повышения цен</h2>
            </div>
            <Link to="/analytics" className={styles.changeLink}>
              Все <ArrowRight className={styles.linkIcon} />
            </Link>
          </div>
          <div className={styles.changeContent}>
            {topIncreases.length === 0 ? (
              <div className={styles.emptyState}>
                <AlertCircle className={styles.emptyIcon} />
                <p>Нет данных о повышениях</p>
              </div>
            ) : (
              <div className={styles.changeList}>
                {topIncreases.map((change) => (
                  <Link key={change.product.id} to={`/products/${change.product.id}`} className={styles.changeItem}>
                    <img src={change.product.imageUrl} alt={change.product.name} className={styles.changeImage} />
                    <div className={styles.changeInfo}>
                      <div className={styles.changeName}>{change.product.name}</div>
                      <div className={styles.changeShop}>{change.product.shop}</div>
                    </div>
                    <div className={styles.changeStats}>
                      <div className={styles.changePercentRed}>+{change.changePercent.toFixed(1)}%</div>
                      <div className={styles.changePrice}>{formatPrice(change.product.currentPrice, change.product.currency)}</div>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      <div className={styles.productsCard}>
        <div className={styles.productsHeader}>
          <h2 className={styles.productsTitle}>Отслеживаемые товары</h2>
          <Link to="/products" className={styles.productsLink}>
            Все товары <ArrowRight className={styles.linkIcon} />
          </Link>
        </div>
        <div className={styles.productsContent}>
          {products.length === 0 ? (
            <div className={styles.emptyProducts}>
              <Package className={styles.emptyProductsIcon} />
              <p>Нет товаров для отслеживания</p>
              <Link to="/add-product" className={styles.emptyProductsButton}>
                <Plus className={styles.addIcon} />
                Добавить первый товар
              </Link>
            </div>
          ) : (
            <div className={styles.productsGrid}>
              {products.slice(0, 6).map((product) => {
                return (
                  <Link key={product.id} to={`/products/${product.id}`} className={styles.productItem}>
                    <img src={product.imageUrl} alt={product.name} className={styles.productImage} />
                    <div className={styles.productInfo}>
                      <div className={styles.productName}>{product.name}</div>
                      <div className={styles.productMeta}>
                        <span>{product.shop}</span>
                        <span>•</span>
                        <span>{product.category}</span>
                      </div>
                    </div>
                    <div className={styles.productPrice}>
                      <div className={styles.productCurrentPrice}>{formatPrice(product.currentPrice, product.currency)}</div>
                    </div>
                  </Link>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
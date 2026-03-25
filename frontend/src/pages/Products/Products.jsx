    import { Link } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { Search, Plus, Trash2, ExternalLink, Filter, Package } from 'lucide-react';
import { getProducts, deleteProduct } from '../../lib/storage';
import { calculatePriceStats, formatPrice } from '../../lib/analytics';
import styles from './Products.module.css';

export default function Products() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedShop, setSelectedShop] = useState('all');

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    try {
      const data = await getProducts();
      setProducts(data);
    } catch (error) {
      console.error('Error loading products:', error);
    } finally {
      setLoading(false);
    }
  };

  const categories = ['all', ...new Set(products.map(p => p.category))];
  const shops = ['all', ...new Set(products.map(p => p.shop))];

  const filteredProducts = products.filter(product => {
    const matchesSearch = product.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         product.shop.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         product.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesCategory = selectedCategory === 'all' || product.category === selectedCategory;
    const matchesShop = selectedShop === 'all' || product.shop === selectedShop;

    return matchesSearch && matchesCategory && matchesShop;
  });

  const handleDelete = async (id, name) => {
    if (confirm(`Удалить товар "${name}" из отслеживания?`)) {
      await deleteProduct(id);
      loadProducts();
    }
  };

  if (loading) {
    return <div className={styles.container}>Загрузка...</div>;
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Товары</h1>
          <p className={styles.subtitle}>Отслеживаемые товары</p>
        </div>
        <Link to="/add-product" className={styles.addButton}>
          <Plus className={styles.addIcon} />
          Добавить товар
        </Link>
      </div>

      <div className={styles.filtersCard}>
        <div className={styles.filtersGrid}>
          <div className={styles.searchWrapper}>
            <Search className={styles.searchIcon} />
            <input
              type="text"
              placeholder="Поиск по названию, магазину, тегам..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className={styles.searchInput}
            />
          </div>

          <div className={styles.selectWrapper}>
            <Filter className={styles.selectIcon} />
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className={styles.select}
            >
              {categories.map(cat => (
                <option key={cat} value={cat}>
                  {cat === 'all' ? 'Все категории' : cat}
                </option>
              ))}
            </select>
          </div>

          <div className={styles.selectWrapper}>
            <Filter className={styles.selectIcon} />
            <select
              value={selectedShop}
              onChange={(e) => setSelectedShop(e.target.value)}
              className={styles.select}
            >
              {shops.map(shop => (
                <option key={shop} value={shop}>
                  {shop === 'all' ? 'Все магазины' : shop}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {filteredProducts.length === 0 ? (
        <div className={styles.emptyState}>
          {products.length === 0 ? (
            <>
              <Package className={styles.emptyIcon} />
              <p className={styles.emptyText}>Нет товаров для отслеживания</p>
              <Link to="/add-product" className={styles.emptyButton}>
                <Plus className={styles.addIcon} />
                Добавить первый товар
              </Link>
            </>
          ) : (
            <>
              <Search className={styles.emptyIcon} />
              <p className={styles.emptyText}>Ничего не найдено по вашему запросу</p>
              <button
                onClick={() => {
                  setSearchQuery('');
                  setSelectedCategory('all');
                  setSelectedShop('all');
                }}
                className={styles.resetButton}
              >
                Сбросить фильтры
              </button>
            </>
          )}
        </div>
      ) : (
        <div className={styles.productsGrid}>
          {filteredProducts.map((product) => {
            const stats = calculatePriceStats(product.id);
            const change = stats ? stats.changePercent7d : 0;
            return (
              <div key={product.id} className={styles.productCard}>
                <Link to={`/products/${product.id}`}>
                  <img src={product.imageUrl} alt={product.name} className={styles.productImage} />
                </Link>
                <div className={styles.productContent}>
                  <Link to={`/products/${product.id}`}>
                    <h3 className={styles.productName}>{product.name}</h3>
                  </Link>
                  <div className={styles.productMeta}>
                    <span className={styles.productShop}>{product.shop}</span>
                    <span>•</span>
                    <span>{product.category}</span>
                  </div>
                  {product.tags.length > 0 && (
                    <div className={styles.tagsList}>
                      {product.tags.slice(0, 3).map(tag => (
                        <span key={tag} className={styles.tag}>{tag}</span>
                      ))}
                      {product.tags.length > 3 && (
                        <span className={styles.tagMore}>+{product.tags.length - 3}</span>
                      )}
                    </div>
                  )}
                  <div className={styles.productFooter}>
                    <div>
                      <div className={styles.productPrice}>
                        {formatPrice(product.currentPrice, product.currency)}
                      </div>
                      {change !== 0 && (
                        <div className={change < 0 ? styles.priceChangeDown : styles.priceChangeUp}>
                          {change > 0 ? '↑' : '↓'} {Math.abs(change).toFixed(1)}% за 7 дней
                        </div>
                      )}
                    </div>
                    <div className={styles.productActions}>
                      <Link to={`/products/${product.id}`} className={styles.actionButton}>
                        Подробнее
                      </Link>
                      <a
                        href={product.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={styles.actionIcon}
                        title="Открыть в магазине"
                      >
                        <ExternalLink className={styles.iconSmall} />
                      </a>
                      <button
                        onClick={() => handleDelete(product.id, product.name)}
                        className={`${styles.actionIcon} ${styles.actionIconDanger}`}
                        title="Удалить"
                      >
                        <Trash2 className={styles.iconSmall} />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
import { useState, useEffect, useMemo } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  ArrowLeft,
  ExternalLink,
  Trash2,
  Target,
  Edit2,
  Save,
  Bell,
  TrendingUp,
  TrendingDown,
  Minus,
  Calendar,
  DollarSign
} from 'lucide-react';
import {
  getProduct,
  getPriceSnapshots,
  deleteProduct,
  getAlertRules,
  saveAlertRule,
  deleteAlertRule,
  saveProduct,
  updateTargetPrice
} from '../../lib/storage';
import { formatPrice, formatPriceChange } from '../../lib/analytics';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ReferenceDot
} from 'recharts';
import styles from './ProductDetail.module.css';

const PERIODS = [
  { label: '7 дней', value: 7 },
  { label: '30 дней', value: 30 },
  { label: '90 дней', value: 90 },
  { label: '180 дней', value: 180 },
  { label: '360 дней', value: 360 }
];

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className={styles.customTooltip}>
        <p className={styles.tooltipDate}>{label}</p>
        <p className={styles.tooltipPrice}>
          <DollarSign size={14} />
          {data.price?.toLocaleString('ru-RU')} ₽
        </p>
        {data.change !== undefined && data.change !== null && (
          <p className={`${styles.tooltipChange} ${data.change >= 0 ? styles.changeUp : styles.changeDown}`}>
            {data.change >= 0 ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
            {data.change >= 0 ? '+' : ''}{data.change?.toLocaleString('ru-RU')} ₽
          </p>
        )}
      </div>
    );
  }
  return null;
};

export default function ProductDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [product, setProduct] = useState(null);
  const [snapshots, setSnapshots] = useState([]);
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState(30);
  const [priceStats, setPriceStats] = useState(null);
  const [isEditingTargetPrice, setIsEditingTargetPrice] = useState(false);
  const [targetPriceInput, setTargetPriceInput] = useState('');
  const [updatingTargetPrice, setUpdatingTargetPrice] = useState(false);
  
  useEffect(() => {
    if (!id || id === 'undefined') return;
    loadData();
  }, [id, selectedPeriod]);

  const loadData = async () => {
    if (!id || id === 'undefined' || id === 'null') {
      console.warn('loadData: пропуск, некорректный id:', id);
      return;
    }
    
    try {
      setLoading(true);
      const [productData, historyData, rulesData] = await Promise.all([
        getProduct(id),
        getPriceSnapshots(id, selectedPeriod),
        getAlertRules(id)
      ]);

      if (!productData) {
        setProduct(null);
        return;
      }

      setProduct({
        ...productData,
        name: productData.title,
        currentPrice: productData.current_price || 0,
        imageUrl: productData.image_url || 'https://via.placeholder.com/200',
        targetPrice: productData.target_price || null
      });
      
      if (productData.target_price) {
        setTargetPriceInput(productData.target_price.toString());
      } else {
        setTargetPriceInput('');
      }
      
      setSnapshots(historyData || []);
      setRules(rulesData || []);

      if (historyData.length > 0) {
        const prices = historyData.map(s => s.price);
        const min = Math.min(...prices);
        const max = Math.max(...prices);
        const avg = prices.reduce((a, b) => a + b, 0) / prices.length;
        const first = historyData[0].price;
        const last = historyData[historyData.length - 1].price;
        const change = last - first;
        const changePercent = first > 0 ? (change / first) * 100 : 0;

        setPriceStats({
          min,
          max,
          avg,
          change,
          changePercent,
          change7d: calculateChange(historyData, 7),
          change30d: calculateChange(historyData, 30)
        });
      } else {
        setPriceStats(null);
      }

    } catch (error) {
      console.error('Error loading product data:', error);
      if (error.message?.includes('401')) {
        navigate('/login');
      }
      setProduct(null);
    } finally {
      setLoading(false);
    }
  };

  const calculateChange = (data, days) => {
    if (data.length < 2) return { change: 0, percent: 0 };
    
    const now = new Date();
    const cutoff = new Date(now.getTime() - days * 24 * 60 * 60 * 1000);
    
    const oldData = data.filter(s => new Date(s.timestamp) <= cutoff);
    const recentData = data.filter(s => new Date(s.timestamp) > cutoff);
    
    if (oldData.length === 0 || recentData.length === 0) return { change: 0, percent: 0 };
    
    const oldPrice = oldData[oldData.length - 1].price;
    const newPrice = recentData[recentData.length - 1].price;
    const change = newPrice - oldPrice;
    const percent = oldPrice > 0 ? (change / oldPrice) * 100 : 0;
    
    return { change, percent };
  };

  const chartData = useMemo(() => {
    if (!snapshots.length) return [];

    return snapshots
      .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
      .map((s, i, arr) => {
        const prevPrice = i > 0 ? arr[i - 1].price : s.price;
        return {
          date: new Date(s.timestamp).toLocaleDateString('ru-RU', {
            day: 'numeric',
            month: 'short'
          }),
          fullDate: new Date(s.timestamp).toLocaleDateString('ru-RU', {
            day: 'numeric',
            month: 'long',
            year: 'numeric'
          }),
          price: s.price,
          change: i > 0 ? s.price - prevPrice : 0,
          index: i
        };
      });
  }, [snapshots]);

  const minPrice = priceStats?.min;
  const maxPrice = priceStats?.max;
  const currentPrice = product?.currentPrice;
  const priceDirection = priceStats?.change >= 0 ? 'up' : 'down';

  const handleDelete = async () => {
    if (confirm(`Удалить товар "${product.name}" из отслеживания?`)) {
      await deleteProduct(id);
      navigate('/products');
    }
  };

  const handleUpdateTargetPrice = async () => {
    if (!product) return;

    setUpdatingTargetPrice(true);
    try {
      const targetPriceValue = targetPriceInput && targetPriceInput.trim() ? parseFloat(targetPriceInput) : null;
      
      await updateTargetPrice(id, targetPriceValue);
      
      const updatedProduct = {
        ...product,
        targetPrice: isNaN(targetPriceValue) ? null : targetPriceValue
      };
      setProduct(updatedProduct);
      
      setIsEditingTargetPrice(false);
    } catch (error) {
      console.error('Error updating target price:', error);
      alert('Ошибка при обновлении целевой цены');
    } finally {
      setUpdatingTargetPrice(false);
    }
  };

  if (loading) {
    return <div className={styles.container}>
      <div className={styles.loading}>
        <div className={styles.spinner}></div>
        <p>Загрузка данных...</p>
      </div>
    </div>;
  }

  if (!product) {
    return (
      <div className={styles.notFound}>
        <h1>Товар не найден</h1>
        <Link to="/products" className={styles.backButton}>
          <ArrowLeft className={styles.iconSmall} />
          Вернуться к товарам
        </Link>
      </div>
    );
  }

  const targetPriceRule = rules.find(r => r.type === 'threshold');

  return (
    <div className={styles.container}>
      <div className={styles.backLink}>
        <Link to="/products" className={styles.backLinkText}>
          <ArrowLeft className={styles.iconSmall} />
          Назад к товарам
        </Link>
      </div>

      <div className={styles.mainGrid}>
        <div className={styles.mainInfo}>
          <div className={styles.productHeader}>
            <img src={product.imageUrl} alt={product.name} className={styles.productImage} />
            <div className={styles.productDetails}>
              <h1 className={styles.productTitle}>{product.name}</h1>
              <div className={styles.productMeta}>
                <span>{product.shop}</span>
                <span>•</span>
                <span>{product.category}</span>
              </div>
              {product.tags && product.tags.length > 0 && (
                <div className={styles.tagsList}>
                  {product.tags.map((tag) => (
                    <span key={tag} className={styles.tag}>{tag}</span>
                  ))}
                </div>
              )}
              <div className={styles.actionButtons}>
                <a href={product.url} target="_blank" rel="noopener noreferrer" className={styles.actionButton}>
                  <ExternalLink className={styles.iconSmall} />
                  Открыть в магазине
                </a>
                <button onClick={handleDelete} className={`${styles.actionButton} ${styles.actionButtonDanger}`}>
                  <Trash2 className={styles.iconSmall} />
                  Удалить
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className={styles.priceStats}>
          <h2 className={styles.sectionTitle}>Текущая цена</h2>
          
          <div className={`${styles.currentPriceWrapper} ${priceDirection === 'down' ? styles.priceDown : priceDirection === 'up' ? styles.priceUp : ''}`}>
            <div className={styles.currentPrice}>
              {currentPrice > 0 ? (
                formatPrice(currentPrice, product.currency)
              ) : (
                <span style={{color: '#999', fontSize: '1.5rem'}}>Нет в наличии</span>
              )}
            </div>
            {priceStats && priceStats.change !== 0 && (
              <div className={`${styles.priceChange} ${priceDirection === 'down' ? styles.changeDown : styles.changeUp}`}>
                {priceDirection === 'down' ? <TrendingDown size={18} /> : <TrendingUp size={18} />}
                <span>{priceStats.change >= 0 ? '+' : ''}{formatPrice(priceStats.change, product.currency)}</span>
                <span className={styles.changePercent}>({priceStats.changePercent >= 0 ? '+' : ''}{priceStats.changePercent.toFixed(1)}%)</span>
              </div>
            )}
          </div>

          <div className={styles.targetPriceSection}>
            <div className={styles.targetPriceHeader}>
              <Target className={styles.targetIcon} />
              <span className={styles.targetLabel}>Целевая цена</span>
            </div>

            {!isEditingTargetPrice ? (
              <div className={styles.targetPriceDisplay}>
                {product.targetPrice ? (
                  <>
                    <span className={styles.targetPriceValue}>
                      {formatPrice(product.targetPrice, product.currency)}
                    </span>
                    {targetPriceRule && (
                      <span className={`${styles.targetStatus} ${targetPriceRule.enabled ? styles.active : styles.inactive}`}>
                        <Bell className={styles.statusIcon} />
                        {targetPriceRule.enabled ? 'Уведомления активны' : 'Уведомления отключены'}
                      </span>
                    )}
                    <button
                      onClick={() => setIsEditingTargetPrice(true)}
                      className={styles.editTargetButton}
                      title="Редактировать целевую цену"
                    >
                      <Edit2 className={styles.iconSmall} />
                    </button>
                  </>
                ) : (
                  <div className={styles.noTargetPrice}>
                    <p>Целевая цена не установлена</p>
                    <button
                      onClick={() => setIsEditingTargetPrice(true)}
                      className={styles.setTargetButton}
                    >
                      <Target className={styles.iconSmall} />
                      Установить
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div className={styles.targetPriceEdit}>
                <div className={styles.targetPriceInputWrapper}>
                  <input
                    type="number"
                    value={targetPriceInput}
                    onChange={(e) => setTargetPriceInput(e.target.value)}
                    className={styles.targetPriceInput}
                    placeholder="Введите целевую цену"
                    step="1000"
                    min="0"
                  />
                  <span className={styles.currencySymbol}>₽</span>
                </div>
                <div className={styles.targetPriceActions}>
                  <button
                    onClick={handleUpdateTargetPrice}
                    disabled={updatingTargetPrice}
                    className={styles.saveTargetButton}
                  >
                    <Save className={styles.iconSmall} />
                    {updatingTargetPrice ? 'Сохранение...' : 'Сохранить'}
                  </button>
                  <button
                    onClick={() => {
                      setIsEditingTargetPrice(false);
                      setTargetPriceInput(product.targetPrice?.toString() || '');
                    }}
                    className={styles.cancelTargetButton}
                  >
                    Отмена
                  </button>
                </div>
              </div>
            )}
          </div>

          {priceStats && (
            <div className={styles.statsGrid}>
              <div className={styles.statCard}>
                <div className={styles.statIcon}><TrendingDown size={16} /></div>
                <div className={styles.statContent}>
                  <div className={styles.statLabel}>Минимум</div>
                  <div className={styles.statValue}>{formatPrice(priceStats.min, product.currency)}</div>
                </div>
              </div>
              <div className={styles.statCard}>
                <div className={styles.statIcon}><TrendingUp size={16} /></div>
                <div className={styles.statContent}>
                  <div className={styles.statLabel}>Максимум</div>
                  <div className={styles.statValue}>{formatPrice(priceStats.max, product.currency)}</div>
                </div>
              </div>
              <div className={styles.statCard}>
                <div className={styles.statIcon}><DollarSign size={16} /></div>
                <div className={styles.statContent}>
                  <div className={styles.statLabel}>Средняя</div>
                  <div className={styles.statValue}>{formatPrice(priceStats.avg, product.currency)}</div>
                </div>
              </div>
              <div className={styles.statCard}>
                <div className={styles.statIcon}><Calendar size={16} /></div>
                <div className={styles.statContent}>
                  <div className={styles.statLabel}>За {selectedPeriod} дн.</div>
                  <div className={`${styles.statValue} ${priceStats.change >= 0 ? styles.changeUp : styles.changeDown}`}>
                    {priceStats.change >= 0 ? '+' : ''}{priceStats.changePercent.toFixed(1)}%
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className={styles.chartCard}>
        <div className={styles.chartHeader}>
          <h2 className={styles.sectionTitle}>История цен</h2>
          <div className={styles.periodSelector}>
            {PERIODS.map(period => (
              <button
                key={period.value}
                onClick={() => setSelectedPeriod(period.value)}
                className={`${styles.periodButton} ${selectedPeriod === period.value ? styles.periodActive : ''}`}
              >
                {period.label}
              </button>
            ))}
          </div>
        </div>
        
        {chartData.length > 0 ? (
          <div className={styles.chartContainer}>
            <ResponsiveContainer width="100%" height={400}>
              <AreaChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                <defs>
                  <linearGradient id="priceGradientUp" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#22c55e" stopOpacity={0.05}/>
                  </linearGradient>
                  <linearGradient id="priceGradientDown" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0.05}/>
                  </linearGradient>
                  <linearGradient id="priceGradientNeutral" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.05}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                <XAxis 
                  dataKey="date" 
                  stroke="var(--muted-foreground)"
                  tick={{ fontSize: 12 }}
                  tickLine={false}
                  axisLine={{ stroke: 'var(--border)' }}
                />
                <YAxis 
                  stroke="var(--muted-foreground)"
                  tick={{ fontSize: 12 }}
                  tickLine={false}
                  axisLine={{ stroke: 'var(--border)' }}
                  tickFormatter={(value) => `${value.toLocaleString()}₽`}
                  domain={['dataMin - 100', 'dataMax + 100']}
                />
                <Tooltip content={<CustomTooltip />} />
                
                {minPrice && (
                  <ReferenceLine 
                    y={minPrice} 
                    stroke="#22c55e" 
                    strokeDasharray="5 5" 
                    strokeWidth={1}
                    label={{
                      value: 'Мин',
                      position: 'right',
                      fill: '#22c55e',
                      fontSize: 11
                    }}
                  />
                )}
                {maxPrice && (
                  <ReferenceLine 
                    y={maxPrice} 
                    stroke="#ef4444" 
                    strokeDasharray="5 5" 
                    strokeWidth={1}
                    label={{
                      value: 'Макс',
                      position: 'right',
                      fill: '#ef4444',
                      fontSize: 11
                    }}
                  />
                )}
                
                <Area
                  type="monotone"
                  dataKey="price"
                  stroke={priceDirection === 'down' ? '#22c55e' : priceDirection === 'up' ? '#ef4444' : '#3b82f6'}
                  strokeWidth={3}
                  fill={priceDirection === 'down' ? 'url(#priceGradientUp)' : priceDirection === 'up' ? 'url(#priceGradientDown)' : 'url(#priceGradientNeutral)'}
                  animationDuration={1000}
                  animationEasing="ease-out"
                  dot={false}
                  activeDot={{ 
                    r: 6, 
                    fill: priceDirection === 'down' ? '#22c55e' : priceDirection === 'up' ? '#ef4444' : '#3b82f6',
                    stroke: '#fff',
                    strokeWidth: 2
                  }}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className={styles.noDataMessage}>
            <p>Нет данных о ценах за выбранный период</p>
          </div>
        )}
      </div>
    </div>
  );
}

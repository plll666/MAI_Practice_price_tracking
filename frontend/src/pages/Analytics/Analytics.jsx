import { useState, useEffect, useMemo } from 'react';
import { Link } from 'react-router-dom';
import {
  TrendingDown,
  TrendingUp,
  Package,
  DollarSign,
  ShoppingBag,
  BarChart3,
  Calendar,
  ArrowUpRight,
  ArrowDownRight,
  Sparkles
} from 'lucide-react';
import { getAnalytics } from '../../lib/storage';
import { useAuth } from '../../context/AuthContext';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  ScatterChart,
  Scatter,
  ZAxis
} from 'recharts';
import styles from './Analytics.module.css';

const PERIODS = [
  { label: '7 дн', value: 7 },
  { label: '30 дн', value: 30 },
  { label: '90 дн', value: 90 },
  { label: '180 дн', value: 180 },
  { label: '360 дн', value: 360 }
];

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16'];

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className={styles.customTooltip}>
        <p className={styles.tooltipLabel}>{label}</p>
        {payload.map((entry, index) => (
          <p key={index} className={styles.tooltipValue} style={{ color: entry.color }}>
            {entry.name}: {typeof entry.value === 'number' ? entry.value.toLocaleString('ru-RU') : entry.value}
            {entry.name.includes('цена') || entry.name.includes('price') ? ' ₽' : ''}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

const PriceTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className={styles.priceTooltip}>
        <p className={styles.priceTooltipDate}>{data.date}</p>
        <p className={styles.priceTooltipPrice}>
          <DollarSign size={14} />
          {data.avg_price?.toLocaleString('ru-RU')} ₽
        </p>
        <div className={styles.priceTooltipRange}>
          <span>мин: {data.min_price?.toLocaleString('ru-RU')} ₽</span>
          <span>макс: {data.max_price?.toLocaleString('ru-RU')} ₽</span>
        </div>
      </div>
    );
  }
  return null;
};

export default function Analytics() {
  const { loading: authLoading } = useAuth();
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState(30);

  useEffect(() => {
    loadAnalytics();
  }, [selectedPeriod]);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      const data = await getAnalytics(selectedPeriod);
      if (data === null) {
        setAnalytics(null);
        setLoading(false);
        return;
      }
      setAnalytics(data);
    } catch (error) {
      console.error('Error loading analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const stats = useMemo(() => {
    if (!analytics?.summary) return [];
    const { summary } = analytics;
    return [
      {
        label: 'Товаров',
        value: summary.total_products,
        icon: Package,
        color: 'blue'
      },
      {
        label: 'Магазинов',
        value: summary.total_shops,
        icon: ShoppingBag,
        color: 'purple'
      },
      {
        label: 'Экономия',
        value: `${summary.total_savings.toLocaleString('ru-RU')} ₽`,
        icon: DollarSign,
        color: 'green'
      },
      {
        label: 'Ср. цена',
        value: `${Math.round(summary.avg_price).toLocaleString('ru-RU')} ₽`,
        icon: BarChart3,
        color: 'amber'
      }
    ];
  }, [analytics]);

  const shopChartData = useMemo(() => {
    if (!analytics?.by_shop) return [];
    return analytics.by_shop.map((shop, index) => ({
      name: shop.shop.length > 12 ? shop.shop.slice(0, 10) + '...' : shop.shop,
      fullName: shop.shop,
      value: shop.count,
      fill: COLORS[index % COLORS.length]
    }));
  }, [analytics]);

  const trendChartData = useMemo(() => {
    if (!analytics?.price_trend) return [];
    return analytics.price_trend.map(point => ({
      ...point,
      date: new Date(point.date).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
    }));
  }, [analytics]);

  const histogramData = useMemo(() => {
    if (!analytics?.price_histogram) return [];
    return analytics.price_histogram.map(bucket => ({
      name: bucket.label,
      count: bucket.count,
      fill: COLORS[Math.floor(Math.random() * COLORS.length)]
    }));
  }, [analytics]);

  const timelineData = useMemo(() => {
    if (!analytics?.changes_timeline) return [];
    return analytics.changes_timeline.slice(0, 30).map(event => ({
      ...event,
      date: new Date(event.date).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
    }));
  }, [analytics]);

  if (authLoading || loading) {
    return (
      <div className={styles.container}>
        <div className={styles.header}>
          <h1 className={styles.title}>Аналитика</h1>
        </div>
        <div className={styles.loadingState}>
          <div className={styles.spinner}></div>
          <p>Загрузка аналитики...</p>
        </div>
      </div>
    );
  }

  if (!analytics || analytics === null) {
    return (
      <div className={styles.container}>
        <div className={styles.header}>
          <h1 className={styles.title}>Аналитика</h1>
        </div>
        <div className={styles.emptyState}>
          <BarChart3 className={styles.emptyIcon} />
          <h2>Необходима авторизация</h2>
          <p>Войдите в систему для просмотра аналитики</p>
          <Link to="/login" className={styles.emptyButton}>
            Войти
          </Link>
        </div>
      </div>
    );
  }

  if (analytics.summary.total_products === 0) {
    return (
      <div className={styles.container}>
        <div className={styles.header}>
          <h1 className={styles.title}>Аналитика</h1>
        </div>
        <div className={styles.emptyState}>
          <BarChart3 className={styles.emptyIcon} />
          <h2>Нет данных для анализа</h2>
          <p>Добавьте товары для отслеживания, чтобы увидеть аналитику</p>
          <Link to="/add-product" className={styles.emptyButton}>
            Добавить товар
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Аналитика</h1>
          <p className={styles.subtitle}>Статистика и тренды изменения цен</p>
        </div>
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

      <div className={styles.statsGrid}>
        {stats.map(stat => {
          const Icon = stat.icon;
          return (
            <div key={stat.label} className={`${styles.statCard} ${styles[`statCard${stat.color}`]}`}>
              <div className={styles.statIconWrapper}>
                <Icon className={styles.statIcon} />
              </div>
              <div className={styles.statContent}>
                <div className={styles.statValue}>{stat.value}</div>
                <div className={styles.statLabel}>{stat.label}</div>
              </div>
            </div>
          );
        })}
      </div>

      <div className={styles.chartSection}>
        <h2 className={styles.sectionTitle}>
          <TrendingUp className={styles.sectionIcon} />
          Динамика цен
        </h2>
        <div className={styles.chartCard}>
          {trendChartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={trendChartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                <defs>
                  <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
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
                  tickFormatter={(value) => `${(value / 1000).toFixed(0)}к`}
                />
                <Tooltip content={<PriceTooltip />} />
                <Area
                  type="monotone"
                  dataKey="avg_price"
                  stroke="#3b82f6"
                  strokeWidth={3}
                  fill="url(#priceGradient)"
                  name="Цена"
                  animationDuration={1000}
                />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className={styles.noData}>Недостаточно данных для отображения тренда</div>
          )}
        </div>
      </div>

      <div className={styles.chartsGrid}>
        <div className={styles.chartSection}>
          <h2 className={styles.sectionTitle}>
            <ShoppingBag className={styles.sectionIcon} />
            Распределение по магазинам
          </h2>
          <div className={styles.chartCard}>
            {shopChartData.length > 0 ? (
              <div className={styles.pieContainer}>
                <ResponsiveContainer width="60%" height={280}>
                  <PieChart>
                    <Pie
                      data={shopChartData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={2}
                      dataKey="value"
                    >
                      {shopChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.fill} />
                      ))}
                    </Pie>
                    <Tooltip content={<CustomTooltip />} />
                  </PieChart>
                </ResponsiveContainer>
                <div className={styles.pieLegend}>
                  {shopChartData.map((entry, index) => (
                    <div key={index} className={styles.legendItem}>
                      <span className={styles.legendColor} style={{ backgroundColor: entry.fill }} />
                      <span className={styles.legendName}>{entry.fullName}</span>
                      <span className={styles.legendValue}>{entry.value}</span>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className={styles.noData}>Нет данных о магазинах</div>
            )}
          </div>
        </div>

        <div className={styles.chartSection}>
          <h2 className={styles.sectionTitle}>
            <BarChart3 className={styles.sectionIcon} />
            Гистограмма цен
          </h2>
          <div className={styles.chartCard}>
            {histogramData.length > 0 ? (
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={histogramData} margin={{ top: 20, right: 30, left: 20, bottom: 40 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                  <XAxis
                    dataKey="name"
                    stroke="var(--muted-foreground)"
                    tick={{ fontSize: 11 }}
                    tickLine={false}
                    axisLine={{ stroke: 'var(--border)' }}
                    angle={-45}
                    textAnchor="end"
                    height={60}
                  />
                  <YAxis
                    stroke="var(--muted-foreground)"
                    tick={{ fontSize: 12 }}
                    tickLine={false}
                    axisLine={{ stroke: 'var(--border)' }}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="count" radius={[4, 4, 0, 0]} name="Товаров" animationDuration={1000}>
                    {histogramData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className={styles.noData}>Нет данных для гистограммы</div>
            )}
          </div>
        </div>
      </div>

      <div className={styles.chartSection}>
        <h2 className={styles.sectionTitle}>
          <Calendar className={styles.sectionIcon} />
          Timeline изменений цен
        </h2>
        <div className={styles.chartCard}>
          {timelineData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <ScatterChart margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis
                  dataKey="date"
                  stroke="var(--muted-foreground)"
                  tick={{ fontSize: 11 }}
                  tickLine={false}
                  axisLine={{ stroke: 'var(--border)' }}
                  name="Дата"
                />
                <YAxis
                  dataKey="change_percent"
                  stroke="var(--muted-foreground)"
                  tick={{ fontSize: 11 }}
                  tickLine={false}
                  axisLine={{ stroke: 'var(--border)' }}
                  tickFormatter={(value) => `${value > 0 ? '+' : ''}${value.toFixed(1)}%`}
                  name="Изменение %"
                />
                <ZAxis dataKey="price_to" range={[50, 400]} />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload;
                      return (
                        <div className={styles.timelineTooltip}>
                          <p className={styles.timelineTooltipTitle}>{data.title}</p>
                          <p className={styles.timelineTooltipDate}>{data.date}</p>
                          <p className={styles[`timelineTooltip${data.is_drop ? 'Drop' : 'Rise'}`]}>
                            {data.is_drop ? <ArrowDownRight size={14} /> : <ArrowUpRight size={14} />}
                            {data.change_percent > 0 ? '+' : ''}{data.change_percent.toFixed(1)}%
                          </p>
                          <p className={styles.timelineTooltipPrice}>
                            {data.price_from.toLocaleString('ru-RU')} → {data.price_to.toLocaleString('ru-RU')} ₽
                          </p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Scatter
                  data={timelineData}
                  fill="#3b82f6"
                  shape="circle"
                >
                  {timelineData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={entry.is_drop ? '#10b981' : '#ef4444'}
                    />
                  ))}
                </Scatter>
              </ScatterChart>
            </ResponsiveContainer>
          ) : (
            <div className={styles.noData}>Нет данных об изменениях цен</div>
          )}
        </div>
      </div>

      <div className={styles.topChangesGrid}>
        <div className={styles.topCard}>
          <div className={`${styles.topHeader} ${styles.topHeaderGreen}`}>
            <TrendingDown className={styles.topIcon} />
            <h3>Лучшие снижения цен</h3>
            <span className={styles.topBadge}>-{selectedPeriod} дн</span>
          </div>
          <div className={styles.topContent}>
            {analytics.top_drops && analytics.top_drops.length > 0 ? (
              <div className={styles.topList}>
                {analytics.top_drops.slice(0, 5).map((item, index) => (
                  <Link key={item.product_id} to={`/products/${item.product_id}`} className={styles.topItem}>
                    <div className={styles.topRank}>{index + 1}</div>
                    {item.image_url && (
                      <img src={item.image_url} alt={item.title} className={styles.topImage} />
                    )}
                    <div className={styles.topInfo}>
                      <div className={styles.topName}>{item.title}</div>
                      <div className={styles.topShop}>{item.shop}</div>
                    </div>
                    <div className={styles.topStats}>
                      <div className={styles.topPercentGreen}>
                        {item.change_percent.toFixed(1)}%
                      </div>
                      <div className={styles.topPrice}>
                        {item.current_price.toLocaleString('ru-RU')} ₽
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            ) : (
              <div className={styles.topEmpty}>Нет данных о снижениях</div>
            )}
          </div>
        </div>

        <div className={styles.topCard}>
          <div className={`${styles.topHeader} ${styles.topHeaderRed}`}>
            <TrendingUp className={styles.topIcon} />
            <h3>Максимальные повышения</h3>
            <span className={styles.topBadge}>-{selectedPeriod} дн</span>
          </div>
          <div className={styles.topContent}>
            {analytics.top_increases && analytics.top_increases.length > 0 ? (
              <div className={styles.topList}>
                {analytics.top_increases.slice(0, 5).map((item, index) => (
                  <Link key={item.product_id} to={`/products/${item.product_id}`} className={styles.topItem}>
                    <div className={styles.topRank}>{index + 1}</div>
                    {item.image_url && (
                      <img src={item.image_url} alt={item.title} className={styles.topImage} />
                    )}
                    <div className={styles.topInfo}>
                      <div className={styles.topName}>{item.title}</div>
                      <div className={styles.topShop}>{item.shop}</div>
                    </div>
                    <div className={styles.topStats}>
                      <div className={styles.topPercentRed}>
                        +{item.change_percent.toFixed(1)}%
                      </div>
                      <div className={styles.topPrice}>
                        {item.current_price.toLocaleString('ru-RU')} ₽
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            ) : (
              <div className={styles.topEmpty}>Нет данных о повышениях</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

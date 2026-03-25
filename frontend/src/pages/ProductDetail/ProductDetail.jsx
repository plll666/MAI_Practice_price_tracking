// ProductDetail.jsx
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useState, useEffect } from 'react';
import {
  ArrowLeft,
  ExternalLink,
  Trash2,
  Plus,
  X,
  ToggleLeft,
  ToggleRight,
  Target,
  Edit2,
  Save,
  Bell
} from 'lucide-react';
import {
  getProduct,
  getPriceSnapshots,
  deleteProduct,
  getAlertRules,
  saveAlertRule,
  deleteAlertRule,
  saveProduct
} from '../../lib/storage';
import { calculatePriceStats, formatPrice, formatPriceChange } from '../../lib/analytics';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import styles from './ProductDetail.module.css';

export default function ProductDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [snapshots, setSnapshots] = useState([]);
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddRule, setShowAddRule] = useState(false);
  const [ruleType, setRuleType] = useState('price_drop');
  const [ruleValue, setRuleValue] = useState('');
  const [ruleUnit, setRuleUnit] = useState('percent');

  // Состояния для редактирования целевой цены
  const [isEditingTargetPrice, setIsEditingTargetPrice] = useState(false);
  const [targetPriceInput, setTargetPriceInput] = useState('');
  const [updatingTargetPrice, setUpdatingTargetPrice] = useState(false);

  useEffect(() => {
    loadData();
  }, [id]);

  const loadData = async () => {
    try {
      const productData = await getProduct(id);
      const snapshotsData = await getPriceSnapshots(id);
      const rulesData = await getAlertRules(id);

      setProduct(productData);
      setSnapshots(snapshotsData);
      setRules(rulesData);

      // Устанавливаем текущую целевую цену для редактирования
      if (productData?.targetPrice) {
        setTargetPriceInput(productData.targetPrice.toString());
      }
    } catch (error) {
      console.error('Error loading product data:', error);
    } finally {
      setLoading(false);
    }
  };

  const stats = product ? calculatePriceStats(snapshots) : null;

  const chartData = snapshots
    .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
    .map((s) => ({
      date: new Date(s.timestamp).toLocaleDateString('ru-RU', {
        day: 'numeric',
        month: 'short',
      }),
      price: s.price,
    }));

  const handleDelete = async () => {
    if (confirm(`Удалить товар "${product.name}" из отслеживания?`)) {
      await deleteProduct(id);
      navigate('/products');
    }
  };

  // Обновление целевой цены
  const handleUpdateTargetPrice = async () => {
    if (!product) return;

    setUpdatingTargetPrice(true);
    try {
      const newTargetPrice = parseFloat(targetPriceInput);
      const updatedProduct = {
        ...product,
        targetPrice: isNaN(newTargetPrice) ? null : newTargetPrice
      };

      await saveProduct(updatedProduct);
      setProduct(updatedProduct);

      const existingTargetRule = rules.find(r => r.type === 'threshold');

      if (newTargetPrice && !isNaN(newTargetPrice) && newTargetPrice > 0) {
        if (existingTargetRule) {
          const updatedRule = {
            ...existingTargetRule,
            value: newTargetPrice,
            enabled: true
          };
          await saveAlertRule(updatedRule);
        } else {
          const newRule = {
            id: `rule-${Date.now()}`,
            productId: id,
            type: 'threshold',
            value: newTargetPrice,
            unit: 'amount',
            enabled: true,
            createdAt: new Date().toISOString(),
          };
          await saveAlertRule(newRule);
        }
      } else if (existingTargetRule) {
        await deleteAlertRule(existingTargetRule.id);
      }

      const updatedRules = await getAlertRules(id);
      setRules(updatedRules);

      setIsEditingTargetPrice(false);
    } catch (error) {
      console.error('Error updating target price:', error);
      alert('Ошибка при обновлении целевой цены');
    } finally {
      setUpdatingTargetPrice(false);
    }
  };

  const handleAddRule = async () => {
    if (!ruleValue) return;

    const rule = {
      productId: id,
      type: ruleType,
      value: parseFloat(ruleValue),
      unit: ruleUnit,
      enabled: true,
    };
    await saveAlertRule(rule);
    setShowAddRule(false);
    setRuleValue('');
    loadData();
  };

  const handleToggleRule = async (rule) => {
    await saveAlertRule({ ...rule, enabled: !rule.enabled });
    loadData();
  };

  const handleDeleteRule = async (ruleId) => {
    if (confirm('Удалить правило уведомления?')) {
      await deleteAlertRule(ruleId);
      loadData();
    }
  };

  if (loading) {
    return <div className={styles.container}>Загрузка...</div>;
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
          <div className={styles.currentPrice}>{formatPrice(product.currentPrice, product.currency)}</div>

          {/* Целевая цена */}
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
                        {targetPriceRule.enabled ? (
                          <Bell className={styles.statusIcon} />
                        ) : (
                          <Bell className={styles.statusIcon} />
                        )}
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
                    <X className={styles.iconSmall} />
                    Отмена
                  </button>
                  {product.targetPrice && (
                    <button
                      onClick={async () => {
                        if (confirm('Удалить целевую цену?')) {
                          setUpdatingTargetPrice(true);
                          try {
                            const updatedProduct = { ...product, targetPrice: null };
                            await saveProduct(updatedProduct);
                            setProduct(updatedProduct);

                            if (targetPriceRule) {
                              await deleteAlertRule(targetPriceRule.id);
                            }

                            const updatedRules = await getAlertRules(id);
                            setRules(updatedRules);
                            setIsEditingTargetPrice(false);
                            setTargetPriceInput('');
                          } catch (error) {
                            console.error('Error removing target price:', error);
                            alert('Ошибка при удалении целевой цены');
                          } finally {
                            setUpdatingTargetPrice(false);
                          }
                        }
                      }}
                      className={styles.removeTargetButton}
                    >
                      <Trash2 className={styles.iconSmall} />
                      Удалить
                    </button>
                  )}
                </div>
              </div>
            )}
          </div>

          {stats && (
            <div className={styles.statsList}>
              <div className={styles.statItem}>
                <div className={styles.statLabel}>За 7 дней</div>
                <div className={stats.change7d < 0 ? styles.statValueDown : stats.change7d > 0 ? styles.statValueUp : styles.statValueNeutral}>
                  {formatPriceChange(stats.change7d, stats.changePercent7d)}
                </div>
              </div>
              <div className={styles.statItem}>
                <div className={styles.statLabel}>За 30 дней</div>
                <div className={stats.change30d < 0 ? styles.statValueDown : stats.change30d > 0 ? styles.statValueUp : styles.statValueNeutral}>
                  {formatPriceChange(stats.change30d, stats.changePercent30d)}
                </div>
              </div>
              <div className={styles.statItem}>
                <div className={styles.statLabel}>Минимум</div>
                <div className={styles.statValueNeutral}>{formatPrice(stats.min, product.currency)}</div>
              </div>
              <div className={styles.statItem}>
                <div className={styles.statLabel}>Максимум</div>
                <div className={styles.statValueNeutral}>{formatPrice(stats.max, product.currency)}</div>
              </div>
              <div className={styles.statItem}>
                <div className={styles.statLabel}>Средняя</div>
                <div className={styles.statValueNeutral}>{formatPrice(stats.avg, product.currency)}</div>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className={styles.chartCard}>
        <h2 className={styles.sectionTitle}>История цен</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis dataKey="date" stroke="var(--muted-foreground)" />
            <YAxis stroke="var(--muted-foreground)" tickFormatter={(value) => `${value.toLocaleString()}₽`} />
            <Tooltip
              contentStyle={{ backgroundColor: 'var(--card)', border: `1px solid var(--border)`, borderRadius: '8px' }}
              formatter={(value) => [`${value.toLocaleString()} ₽`, 'Цена']}
            />
            <Line type="monotone" dataKey="price" stroke="#3b82f6" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className={styles.rulesCard}>
        <div className={styles.rulesHeader}>
          <h2 className={styles.sectionTitle}>Правила уведомлений</h2>
          <button onClick={() => setShowAddRule(!showAddRule)} className={styles.addRuleButton}>
            <Plus className={styles.iconSmall} />
            Добавить правило
          </button>
        </div>

        {showAddRule && (
          <div className={styles.addRuleForm}>
            <div className={styles.formGrid}>
              <select
                value={ruleType}
                onChange={(e) => setRuleType(e.target.value)}
                className={styles.select}
              >
                <option value="price_drop">Снижение цены</option>
                <option value="price_increase">Повышение цены</option>
                <option value="threshold">Порог цены</option>
              </select>
              <input
                type="number"
                value={ruleValue}
                onChange={(e) => setRuleValue(e.target.value)}
                className={styles.input}
                placeholder="Значение"
              />
              <select
                value={ruleUnit}
                onChange={(e) => setRuleUnit(e.target.value)}
                className={styles.select}
              >
                <option value="percent">Процент</option>
                <option value="amount">Сумма (₽)</option>
              </select>
            </div>
            <div className={styles.formActions}>
              <button onClick={handleAddRule} className={styles.saveButton}>Сохранить</button>
              <button onClick={() => setShowAddRule(false)} className={styles.cancelButton}>Отмена</button>
            </div>
          </div>
        )}

        <div className={styles.rulesList}>
          {rules.length === 0 ? (
            <div className={styles.emptyRules}>Нет правил уведомлений</div>
          ) : (
            rules.map((rule) => (
              <div key={rule.id} className={styles.ruleItem}>
                <div className={styles.ruleInfo}>
                  <div className={styles.ruleText}>
                    {rule.type === 'price_drop' && 'Снижение цены на '}
                    {rule.type === 'price_increase' && 'Повышение цены на '}
                    {rule.type === 'threshold' && 'Цена достигнет '}
                    {rule.value}
                    {rule.unit === 'percent' ? '%' : ' ₽'}
                  </div>
                  <div className={styles.ruleStatus}>
                    {rule.enabled ? 'Активно' : 'Отключено'}
                  </div>
                </div>
                <div className={styles.ruleActions}>
                  <button onClick={() => handleToggleRule(rule)} className={styles.toggleButton}>
                    {rule.enabled ? <ToggleRight className={styles.iconMedium} /> : <ToggleLeft className={styles.iconMedium} />}
                  </button>
                  <button onClick={() => handleDeleteRule(rule.id)} className={styles.deleteRuleButton}>
                    <X className={styles.iconSmall} />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
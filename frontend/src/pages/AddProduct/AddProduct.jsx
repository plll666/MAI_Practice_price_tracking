import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, Plus, X, Link as LinkIcon, Target } from 'lucide-react';
import { saveProduct, savePriceSnapshot, saveAlertRule } from '../../lib/storage';
import styles from './AddProduct.module.css';

export default function AddProduct() {
  const navigate = useNavigate();
  const [url, setUrl] = useState('');
  const [tags, setTags] = useState([]);
  const [tagInput, setTagInput] = useState('');
  const [targetPrice, setTargetPrice] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    const productId = `product-${Date.now()}`;
    const now = new Date().toISOString();

    try {
      const urlObj = new URL(url);
      const hostname = urlObj.hostname.replace('www.', '');
      const mockPrice = Math.floor(Math.random() * 50000) + 10000;

      const product = {
        id: productId,
        name: `Товар из ${hostname}`,
        url: url,
        shop: hostname,
        category: 'Электроника',
        tags,
        currentPrice: mockPrice,
        currency: 'RUB',
        imageUrl: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400',
        isAvailable: true,
        addedAt: now,
        lastChecked: now,
        targetPrice: targetPrice ? parseFloat(targetPrice) : null,
      };

      await saveProduct(product);

      const snapshot = {
        id: `${productId}-0`,
        productId,
        price: mockPrice,
        currency: 'RUB',
        timestamp: now,
        isAvailable: true,
      };

      await savePriceSnapshot(snapshot);

      // Создаем правило уведомления о достижении целевой цены
      if (targetPrice && parseFloat(targetPrice) > 0) {
        const alertRule = {
          id: `rule-${Date.now()}`,
          productId,
          type: 'threshold',
          value: parseFloat(targetPrice),
          unit: 'amount',
          enabled: true,
          createdAt: now,
        };
        await saveAlertRule(alertRule);
      }

      // Создаем историю цен
      for (let i = 1; i <= 30; i++) {
        const variation = (Math.random() - 0.5) * 0.15;
        const historicalPrice = Math.round(mockPrice * (1 + variation));
        const timestamp = new Date(Date.now() - i * 24 * 60 * 60 * 1000).toISOString();

        await savePriceSnapshot({
          id: `${productId}-${i}`,
          productId,
          price: historicalPrice,
          currency: 'RUB',
          timestamp,
          isAvailable: true,
        });
      }

      setIsLoading(false);
      navigate(`/products/${productId}`);
    } catch (error) {
      console.error('Error adding product:', error);
      setIsLoading(false);
      alert('Ошибка при добавлении товара. Проверьте URL.');
    }
  };

  const handleAddTag = () => {
    if (tagInput.trim() && !tags.includes(tagInput.trim())) {
      setTags([...tags, tagInput.trim()]);
      setTagInput('');
    }
  };

  const handleRemoveTag = (tag) => {
    setTags(tags.filter(t => t !== tag));
  };

  return (
    <div className={styles.container}>
      <div className={styles.backLink}>
        <Link to="/" className={styles.backLinkText}>
          <ArrowLeft className={styles.iconSmall} />
          Назад
        </Link>
      </div>

      <div className={styles.formCard}>
        <div className={styles.formHeader}>
          <div className={styles.iconWrapper}>
            <LinkIcon className={styles.headerIcon} />
          </div>
          <h1 className={styles.title}>Добавить товар</h1>
          <p className={styles.subtitle}>Вставьте ссылку и настройте отслеживание</p>
        </div>

        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.formGroup}>
            <label className={styles.label}>URL товара</label>
            <input
              type="url"
              required
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className={styles.input}
              placeholder="https://example.com/product"
            />
          </div>

          <div className={styles.formGroup}>
            <label className={styles.label}>Целевая цена (опционально)</label>
            <div className={styles.targetPriceWrapper}>
              <Target className={styles.targetIcon} />
              <input
                type="number"
                value={targetPrice}
                onChange={(e) => setTargetPrice(e.target.value)}
                className={styles.input}
                placeholder="Например: 15000"
                step="1000"
                min="0"
              />
              <span className={styles.currencySymbol}>₽</span>
            </div>
            <p className={styles.hint}>
              При достижении этой цены вы получите уведомление
            </p>
          </div>

          <div className={styles.formGroup}>
            <label className={styles.label}>Теги</label>
            <div className={styles.tagInputWrapper}>
              <input
                type="text"
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    handleAddTag();
                  }
                }}
                className={styles.tagInput}
                placeholder="Добавить тег..."
              />
              <button type="button" onClick={handleAddTag} className={styles.addTagButton}>
                <Plus className={styles.iconSmall} />
              </button>
            </div>

            {tags.length > 0 && (
              <div className={styles.tagsList}>
                {tags.map(tag => (
                  <span key={tag} className={styles.tag}>
                    {tag}
                    <button type="button" onClick={() => handleRemoveTag(tag)} className={styles.removeTagButton}>
                      <X className={styles.iconTiny} />
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>

          <button type="submit" disabled={isLoading} className={styles.submitButton}>
            {isLoading ? 'Добавление...' : 'Добавить товар'}
          </button>
        </form>
      </div>
    </div>
  );
}
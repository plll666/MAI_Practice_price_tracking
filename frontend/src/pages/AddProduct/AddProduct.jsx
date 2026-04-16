import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, Plus, X, Link as LinkIcon, Target } from 'lucide-react';
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

  try {
    const { addProductByUrl } = await import('../../lib/storage');
    const targetPriceValue = targetPrice && targetPrice.trim() ? parseFloat(targetPrice) : null;
    const result = await addProductByUrl(url, targetPriceValue); 

    setIsLoading(false);
    navigate(`/products/${result.id}`);
  } catch (error) {
    console.error('Error adding product:', error);
    setIsLoading(false);
    alert(`Ошибка: ${error.message}`);
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
          <p className={styles.subtitle}>Вставьте ссылку для запуска парсера</p>
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
            <label className={styles.label}>Желаемая цена (мониторинг)</label>
            <div className={styles.targetPriceWrapper}>
              <Target className={styles.targetIcon} />
              <input
                type="number"
                value={targetPrice}
                onChange={(e) => setTargetPrice(e.target.value)}
                className={styles.input}
                placeholder="Например: 15000"
              />
              <span className={styles.currencySymbol}>₽</span>
            </div>
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
            {isLoading ? 'Запуск парсера...' : 'Начать отслеживание'}
          </button>
        </form>
      </div>
    </div>
  );
}
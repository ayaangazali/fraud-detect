// src/components/LanguageSwitcher.tsx
import { TranslationKey } from '../i18n/translations';

interface LanguageSwitcherProps {
  isArabic: boolean;
  onToggle: () => void;
  t: (key: TranslationKey) => string;
}

export function LanguageSwitcher({ isArabic, onToggle }: LanguageSwitcherProps) {
  return (
    <div className="language-switcher">
      <button 
        className={`lang-btn ${!isArabic ? 'active' : ''}`}
        onClick={() => !isArabic || onToggle()}
        title="Switch to English"
      >
        EN
      </button>
      <button 
        className={`lang-btn ${isArabic ? 'active' : ''}`}
        onClick={() => isArabic || onToggle()}
        title="Switch to Arabic"
      >
        AR | عربي
      </button>
    </div>
  );
}

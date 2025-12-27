'use client';

import { useLanguage } from 'lib/i18n/context';
import { useRouter } from 'next/navigation';

export default function LanguageToggle() {
  const { language, setLanguage } = useLanguage();
  const router = useRouter();

  const toggleLang = async () => {
    const newLang = language === 'EN' ? 'VI' : 'EN';
    
    // Set cookie via API route
    await fetch('/api/set-language', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ language: newLang })
    });
    
    // Update client state
    setLanguage(newLang);
    
    // Refresh page to re-render server components with new language
    router.refresh();
  };

  return (
    <button
      onClick={toggleLang}
      className="text-sm font-medium text-neutral-500 hover:text-black dark:text-neutral-400 dark:hover:text-neutral-300"
    >
      {language}
    </button>
  );
}

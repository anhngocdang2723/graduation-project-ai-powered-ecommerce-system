import { cookies } from 'next/headers';
import { dictionary, Language } from './dictionary';

export async function getServerTranslation() {
  const cookieStore = await cookies();
  const language = (cookieStore.get('language')?.value as Language) || 'VI';
  
  const t = (key: string): string => {
    const keys = key.split('.');
    let value: any = dictionary[language];
    
    for (const k of keys) {
      value = value?.[k];
      if (value === undefined) break;
    }
    
    return value || key;
  };
  
  return { t, language };
}

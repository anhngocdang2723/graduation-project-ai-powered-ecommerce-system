import { getCategories } from 'lib/medusa';
import { getServerTranslation } from 'lib/i18n/server';
import Link from 'next/link';
import { ProductCollection } from 'lib/medusa/types';

export async function CategoryGrid() {
  const { t } = await getServerTranslation();
  const categories = await getCategories();
  
  // Limit to 8 main categories for cleaner display
  const displayCategories = categories.slice(0, 8);

  if (!displayCategories.length) return null;

  return (
    <section className="mx-auto max-w-screen-2xl px-4 py-8">
      <h2 className="mb-6 text-2xl font-bold">{t('categories.title')}</h2>
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-8">
        {displayCategories.map((category: ProductCollection) => (
          <Link
            key={category.id}
            href={category.path}
            className="group flex flex-col items-center rounded-lg border border-neutral-200 p-4 transition-all hover:border-blue-600 hover:shadow-md dark:border-neutral-800 dark:hover:border-blue-600"
          >
            <div className="mb-2 flex h-16 w-16 items-center justify-center rounded-full bg-neutral-100 text-2xl dark:bg-neutral-900">
              {category.title.charAt(0)}
            </div>
            <span className="text-center text-sm font-medium group-hover:text-blue-600">
              {category.title}
            </span>
          </Link>
        ))}
      </div>
    </section>
  );
}

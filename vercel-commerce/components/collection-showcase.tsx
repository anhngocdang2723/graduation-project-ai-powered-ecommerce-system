import { getCollections } from 'lib/medusa';
import { getServerTranslation } from 'lib/i18n/server';
import Link from 'next/link';

export async function CollectionShowcase() {
  const { t } = await getServerTranslation();
  const collections = await getCollections();
  
  // Show only first 4 collections
  const showcaseCollections = collections.slice(0, 4);

  if (showcaseCollections.length === 0) return null;

  return (
    <div className="mx-auto max-w-screen-2xl px-4 py-12">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold">{t('collections.title')}</h2>
          <p className="mt-2 text-neutral-600 dark:text-neutral-400">
            {t('collections.subtitle')}
          </p>
        </div>
        <Link
          href="/collections"
          className="text-sm font-semibold text-blue-600 hover:underline dark:text-blue-400"
        >
          {t('collections.viewAll')} →
        </Link>
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        {showcaseCollections.map((collection) => (
          <Link
            key={collection.id}
            href={`/collections/${collection.handle}`}
            className="group relative overflow-hidden rounded-lg border border-neutral-200 transition hover:shadow-lg dark:border-neutral-800"
          >
            <div className="aspect-square bg-gradient-to-br from-blue-500 to-purple-600 p-6 transition group-hover:scale-105">
              <div className="flex h-full flex-col justify-end">
                <h3 className="text-xl font-bold text-white">{collection.title}</h3>
                <p className="mt-1 text-sm text-white/80">{t('common.viewMore')} →</p>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}

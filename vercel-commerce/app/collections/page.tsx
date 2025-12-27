import { getCollections } from 'lib/medusa';
import { getServerTranslation } from 'lib/i18n/server';
import Link from 'next/link';

export async function generateMetadata() {
  const { t } = await getServerTranslation();
  return {
    title: t('collections.title'),
    description: t('collections.discover')
  };
}

export default async function CollectionsPage() {
  const { t } = await getServerTranslation();
  const collections = await getCollections();

  return (
    <div className="mx-auto max-w-screen-2xl px-4 py-8">
      <div className="mb-8">
        <h1 className="mb-2 text-3xl font-bold">{t('collections.title')}</h1>
        <p className="text-neutral-600 dark:text-neutral-400">
          {t('collections.discover')}
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {collections.map((collection) => (
          <Link
            key={collection.id}
            href={`/collections/${collection.handle}`}
            className="group relative overflow-hidden rounded-lg border border-neutral-200 bg-white transition hover:shadow-lg dark:border-neutral-800 dark:bg-black"
          >
            <div className="aspect-[4/3] overflow-hidden bg-neutral-100 dark:bg-neutral-900">
              {/* Placeholder for collection image */}
              <div className="flex h-full w-full items-center justify-center bg-gradient-to-br from-blue-500 to-purple-600">
                <span className="text-4xl font-bold text-white opacity-50">
                  {collection.title.charAt(0)}
                </span>
              </div>
            </div>
            <div className="p-6">
              <h2 className="mb-2 text-xl font-semibold group-hover:text-blue-600 dark:group-hover:text-blue-400">
                {collection.title}
              </h2>
              {collection.description && (
                <p className="line-clamp-2 text-sm text-neutral-600 dark:text-neutral-400">
                  {collection.description}
                </p>
              )}
              <p className="mt-4 text-sm font-semibold text-blue-600 dark:text-blue-400">
                {t('collections.viewCollection')} →
              </p>
            </div>
          </Link>
        ))}
      </div>

      {collections.length === 0 && (
        <div className="flex min-h-[400px] flex-col items-center justify-center rounded-lg border border-neutral-200 bg-white p-12 dark:border-neutral-800 dark:bg-black">
          <h2 className="mb-2 text-xl font-semibold">{t('collections.noCollections')}</h2>
          <p className="mb-6 text-neutral-600 dark:text-neutral-400">
            {t('collections.checkBackCollections')}
          </p>
          <Link
            href="/search"
            className="rounded-full bg-blue-600 px-6 py-3 text-white transition hover:bg-blue-700"
          >
            {t('collections.browseAllProducts')}
          </Link>
        </div>
      )}
    </div>
  );
}

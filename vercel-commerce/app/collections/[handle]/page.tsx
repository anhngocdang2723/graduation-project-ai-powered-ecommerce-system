import type { Metadata } from 'next';
import { notFound } from 'next/navigation';

import SearchResults from 'components/search/search-results';
import { defaultSort, sorting } from 'lib/constants';
import { getCollections, getCollectionProducts } from 'lib/medusa';

export async function generateMetadata({
  params
}: {
  params: { handle: string };
}): Promise<Metadata> {
  const collections = await getCollections();
  const collection = collections.find((c) => c.handle === params.handle);
  
  if (!collection) return notFound();

  return {
    title: collection.seo?.title || collection.title,
    description: collection.seo?.description || collection.description
  };
}

export default async function CollectionPage({ 
  params,
  searchParams 
}: { 
  params: { handle: string };
  searchParams?: { [key: string]: string | string[] | undefined };
}) {
  const collections = await getCollections();
  const collection = collections.find((c) => c.handle === params.handle);
  
  if (!collection) return notFound();

  const { sort, page } = searchParams as { [key: string]: string };
  const { sortKey, reverse } = sorting.find((item) => item.slug === sort) || defaultSort;
  const currentPage = page ? parseInt(page) : 1;
  const pageSize = 12;
  const offset = (currentPage - 1) * pageSize;

  const products = await getCollectionProducts(collection.id, reverse, sortKey, pageSize, offset);

  return (
    <section>
      {/* Collection Header */}
      <div className="mb-8">
        <h1 className="mb-2 text-3xl font-bold">{collection.title}</h1>
        {collection.description && (
          <p className="text-neutral-600 dark:text-neutral-400">{collection.description}</p>
        )}
      </div>

      {/* Use shared SearchResults template */}
      <SearchResults products={products} searchValue="" currentPage={currentPage} pageSize={pageSize} />
    </section>
  );
}

import { Metadata } from 'next';
import { notFound } from 'next/navigation';

import SearchResults from 'components/search/search-results';
import { defaultSort, sorting } from 'lib/constants';
import { getCategory, getCategoryProducts } from 'lib/medusa';

export const runtime = 'edge';

export async function generateMetadata(props: {
  params: Promise<{ handle: string }>;
}): Promise<Metadata> {
  const params = await props.params;
  const category = await getCategory(params.handle);

  if (!category) return notFound();

  return {
    title: category.seo?.title || category.title,
    description: category.seo?.description || category.description,
    openGraph: {
      images: [
        {
          url: `/api/og?title=${encodeURIComponent(category.title)}`,
          width: 1200,
          height: 630
        }
      ]
    }
  };
}

export default async function CategoryPage(props: {
  params: Promise<{ handle: string }>;
  searchParams?: Promise<{ [key: string]: string | string[] | undefined }>;
}) {
  const params = await props.params;
  const searchParams = (await props.searchParams) || {};
  const category = await getCategory(params.handle);

  if (!category) return notFound();

  const { sort, page } = searchParams as { [key: string]: string };
  const { sortKey, reverse } = sorting.find((item) => item.slug === sort) || defaultSort;
  const currentPage = page ? parseInt(page) : 1;
  const pageSize = 12;
  const offset = (currentPage - 1) * pageSize;

  const products = await getCategoryProducts(params.handle, reverse, sortKey, pageSize, offset);
  
  console.log('[CategoryPage] Products fetched:', products.length, 'for category:', params.handle);

  return (
    <>
      {/* Category Header */}
      <div className="mb-8">
        <h1 className="mb-2 text-3xl font-bold">{category.title || category.name}</h1>
        {category.description && (
          <p className="text-neutral-600 dark:text-neutral-400">{category.description}</p>
        )}
      </div>

      {/* Use shared SearchResults template */}
      <SearchResults products={products} searchValue="" currentPage={currentPage} pageSize={pageSize} />
    </>
  );
}

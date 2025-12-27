import { getCategory, getCategoryProducts } from 'lib/medusa';
import { getServerTranslation } from 'lib/i18n/server';
import { Metadata } from 'next';
import { notFound } from 'next/navigation';

import Grid from 'components/grid';
import ProductGridItems from 'components/layout/product-grid-items';
import { Pagination } from 'components/pagination';
import { defaultSort, sorting } from 'lib/constants';

export const runtime = 'edge';

export async function generateMetadata({
  params
}: {
  params: { collection: string };
}): Promise<Metadata> {
  const collection = await getCategory(params.collection);

  if (!collection) return notFound();

  return {
    title: collection.seo?.title || collection.title,
    description:
      collection.seo?.description || collection.description || `${collection.title} products`
  };
}

export default async function CategoryPage({
  params,
  searchParams
}: {
  params: { collection: string };
  searchParams?: { [key: string]: string | string[] | undefined };
}) {
  const { t } = await getServerTranslation();
  const { sort, page } = searchParams as { [key: string]: string };
  const { sortKey, reverse } = sorting.find((item) => item.slug === sort) || defaultSort;
  
  const currentPage = page ? parseInt(page) : 1;
  const pageSize = 12;
  const offset = (currentPage - 1) * pageSize;
  
  const products = await getCategoryProducts(params.collection, reverse, sortKey, pageSize, offset);
  const totalPages = products.length === pageSize ? currentPage + 1 : currentPage;

  return (
    <section>
      {products.length === 0 ? (
        <p className="py-3 text-lg">{t('collections.noProducts')}</p>
      ) : (
        <>
          <Grid className="grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
            <ProductGridItems products={products} />
          </Grid>
          <Pagination currentPage={currentPage} totalPages={totalPages} />
        </>
      )}
    </section>
  );
}

'use client';

import Grid from 'components/grid';
import ProductGridItems from 'components/layout/product-grid-items';
import { Pagination } from 'components/pagination';
import { useLanguage } from 'lib/i18n/context';
import { Product } from 'lib/medusa/types';

export default function SearchResults({
  products,
  searchValue,
  currentPage = 1,
  pageSize = 12
}: {
  products: Product[];
  searchValue: string;
  currentPage?: number;
  pageSize?: number;
}) {
  const { t } = useLanguage();
  const resultsText = products.length > 1 ? t('search.results') : t('search.result');
  // Estimate total pages (this would ideally come from API)
  const totalPages = products.length === pageSize ? currentPage + 1 : currentPage;

  return (
    <>
      {searchValue ? (
        <p className="mb-4">
          {products.length === 0
            ? `${t('search.noResults')} `
            : `${t('search.showing')} ${products.length} ${resultsText} ${t('search.for')} `}
          <span className="font-bold">&quot;{searchValue}&quot;</span>
        </p>
      ) : null}
      {products.length > 0 ? (
        <>
          <Grid className="grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
            <ProductGridItems products={products} />
          </Grid>
          <Pagination currentPage={currentPage} totalPages={totalPages} />
        </>
      ) : null}
    </>
  );
}

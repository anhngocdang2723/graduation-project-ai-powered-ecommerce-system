import SearchResults from 'components/search/search-results';
import { defaultSort, sorting } from 'lib/constants';
import { getProducts } from 'lib/medusa';

export const runtime = 'edge';

export const metadata = {
  title: 'Search',
  description: 'Search for products in the store.'
};

export default async function SearchPage({
  searchParams
}: {
  searchParams?: { [key: string]: string | string[] | undefined };
}) {
  const { sort, q: searchValue, page } = searchParams as { [key: string]: string };
  const { sortKey, reverse } = sorting.find((item) => item.slug === sort) || defaultSort;
  const currentPage = page ? parseInt(page) : 1;
  const pageSize = 12;
  const offset = (currentPage - 1) * pageSize;

  const products = await getProducts({ 
    sortKey, 
    reverse, 
    query: searchValue,
    limit: pageSize,
    offset 
  });

  return <SearchResults products={products} searchValue={searchValue} currentPage={currentPage} pageSize={pageSize} />;
}

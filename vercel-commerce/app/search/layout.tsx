import Footer from 'components/layout/footer';
import Collections from 'components/layout/search/collections';
import FilterList from 'components/layout/search/filter';
import PriceFilter from 'components/layout/search/price-filter';
import { sorting } from 'lib/constants';
import { Suspense } from 'react';

export default function SearchLayout({ children }: { children: React.ReactNode }) {
  return (
    <Suspense>
      <div className="mx-auto flex max-w-screen-2xl flex-col gap-8 px-4 pb-4 text-black dark:text-white md:flex-row">
        <div className="order-first w-full flex-none md:max-w-[200px]">
          <Collections />
          <div className="mt-4">
            <PriceFilter />
          </div>
        </div>
        <div className="order-last min-h-screen w-full md:order-none">{children}</div>
        <div className="order-none flex-none md:order-last md:w-[125px]">
          <FilterList list={sorting} title="Sort by" />
        </div>
      </div>
      <Footer />
    </Suspense>
  );
}

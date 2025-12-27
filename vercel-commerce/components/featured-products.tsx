import Grid from 'components/grid';
import ProductGridItems from 'components/layout/product-grid-items';
import { getProducts } from 'lib/medusa';
import { getServerTranslation } from 'lib/i18n/server';
import Link from 'next/link';

export async function FeaturedProducts() {
  const { t } = await getServerTranslation();
  const products = await getProducts({});
  
  // Show first 8 products as featured
  const featuredProducts = products.slice(0, 8);

  if (!featuredProducts.length) return null;

  return (
    <section className="mx-auto max-w-screen-2xl px-4 py-8">
      <div className="mb-6 flex items-center justify-between">
        <h2 className="text-2xl font-bold">{t('featured.title')}</h2>
        <Link
          href="/search"
          className="text-sm font-medium text-blue-600 hover:underline"
        >
          {t('featured.viewAll')} →
        </Link>
      </div>
      <Grid className="grid-cols-2 sm:grid-cols-3 md:grid-cols-4">
        <ProductGridItems products={featuredProducts} />
      </Grid>
    </section>
  );
}

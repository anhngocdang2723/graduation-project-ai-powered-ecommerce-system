import { getProducts } from 'lib/medusa';
import Link from 'next/link';
import { GridTileImage } from './grid/tile';

export async function Carousel() {
  // Get all products for carousel
  const products = await getProducts({});

  if (!products?.length) return null;

  // Limit to 10 products for cleaner display
  const carouselProducts = products.slice(0, 10);

  return (
    <div className="w-full overflow-x-auto pb-6 pt-1">
      <ul className="flex animate-carousel gap-4">
        {carouselProducts.map((product, i) => (
          <li
            key={`${product.handle}${i}`}
            className="relative aspect-square h-[280px] w-[280px] flex-none"
          >
            <Link href={`/product/${product.handle}`} className="relative h-full w-full">
              <GridTileImage
                alt={product.featuredImage?.altText}
                label={{
                  title: product.title,
                  amount: product.priceRange.maxVariantPrice.amount,
                  currencyCode: product.priceRange.maxVariantPrice.currencyCode
                }}
                src={product.featuredImage?.url}
                fill
                sizes="(min-width: 1024px) 25vw, (min-width: 768px) 33vw, 50vw"
                stockQuantity={product.variants?.[0]?.inventory_quantity}
              />
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

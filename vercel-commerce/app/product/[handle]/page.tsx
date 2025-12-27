import type { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { Suspense } from 'react';

import { GridTileImage } from 'components/grid/tile';
import Footer from 'components/layout/footer';
import { Gallery } from 'components/product/gallery';
import { ProductDescription } from 'components/product/product-description';
import ProductReviews from 'components/product/product-reviews';
import { RelatedProducts } from 'components/product/related-products';import { ProductViewTracker } from 'components/tracking/tracking-wrapper';import { HIDDEN_PRODUCT_TAG } from 'lib/constants';
import { getProduct } from 'lib/medusa';
import { Image } from 'lib/medusa/types';
import Link from 'next/link';

export const runtime = 'edge';

export async function generateMetadata({
  params
}: {
  params: { handle: string };
}): Promise<Metadata> {
  const product = await getProduct(params.handle);

  if (!product) return notFound();

  const { url, width, height, altText: alt } = product.featuredImage || {};
  const indexable = !product.tags.includes(HIDDEN_PRODUCT_TAG);

  return {
    title: product.title,
    description: product.description,
    robots: {
      index: indexable,
      follow: indexable,
      googleBot: {
        index: indexable,
        follow: indexable
      }
    },
    openGraph: url
      ? {
          images: [
            {
              url,
              width,
              height,
              alt
            }
          ]
        }
      : null
  };
}

export default async function ProductPage({ params }: { params: { handle: string } }) {
  const product = await getProduct(params.handle);

  if (!product) return notFound();

  const productJsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Product',
    name: product.title,
    description: product.description,
    image: product.featuredImage.url,
    offers: {
      '@type': 'AggregateOffer',
      availability: product.availableForSale
        ? 'https://schema.org/InStock'
        : 'https://schema.org/OutOfStock',
      priceCurrency: product.priceRange.maxVariantPrice.currencyCode,
      highPrice: product.priceRange.maxVariantPrice.amount
    }
  };

  return (
    <>
      <ProductViewTracker 
        productId={product.id!}
        productHandle={product.handle}
        category={product.tags?.[0] || ''}
        price={product.priceRange.maxVariantPrice.amount}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(productJsonLd)
        }}
      />
      <div className="mx-auto max-w-screen-2xl px-4">
        <div className="flex flex-col rounded-lg border border-neutral-200 bg-white p-8 dark:border-neutral-800 dark:bg-black md:p-12 lg:flex-row">
          <div className="h-full w-full basis-full lg:basis-4/6">
            <Gallery
              images={product.images!.map((image: Image) => ({
                src: image.url,
                altText: image.altText
              }))}
            />
          </div>

          <div className="basis-full lg:basis-2/6">
            <ProductDescription product={product} />
          </div>
        </div>
        
        <div className="mt-8">
          <ProductReviews
            productId={product.id!}
            reviews={[
              {
                id: '1',
                author: 'John Doe',
                rating: 5,
                comment: 'Great product! Highly recommend.',
                date: '2025-12-10',
                verified: true
              },
              {
                id: '2',
                author: 'Jane Smith',
                rating: 4,
                comment: 'Good quality, fast shipping.',
                date: '2025-12-08',
                verified: true
              }
            ]}
            averageRating={4.5}
            totalReviews={2}
          />
        </div>
        
        <Suspense fallback={<div className="h-64 animate-pulse" />}>
          <RelatedProducts productId={product.id!} productHandle={product.handle} />
        </Suspense>
      </div>
      <Suspense>
        <Footer />
      </Suspense>
    </>
  );
}

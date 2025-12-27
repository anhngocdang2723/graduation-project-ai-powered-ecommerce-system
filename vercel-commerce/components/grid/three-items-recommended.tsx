'use client';

import { GridTileImage } from 'components/grid/tile';
import type { Product } from 'lib/medusa/types';
import { getUserId } from 'lib/tracking/user-behavior';
import Link from 'next/link';
import { useEffect, useState } from 'react';

function ThreeItemGridItem({
  item,
  size,
  priority
}: {
  item: Product;
  size: 'full' | 'half';
  priority?: boolean;
}) {
  return (
    <div
      className={size === 'full' ? 'md:col-span-4 md:row-span-2' : 'md:col-span-2 md:row-span-1'}
    >
      <Link className="relative block aspect-square h-full w-full" href={`/product/${item.handle}`}>
        <GridTileImage
          src={item.featuredImage?.url || item.thumbnail || 'https://via.placeholder.com/300x300?text=No+Image'}
          fill
          sizes={
            size === 'full' ? '(min-width: 768px) 66vw, 100vw' : '(min-width: 768px) 33vw, 100vw'
          }
          priority={priority}
          alt={item.title}
          label={{
            position: size === 'full' ? 'center' : 'bottom',
            title: item.title as string,
            amount: item.priceRange?.maxVariantPrice?.amount || '0',
            currencyCode: item.priceRange?.maxVariantPrice?.currencyCode || 'VND'
          }}
        />
      </Link>
    </div>
  );
}

export function ThreeItemGrid() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRecommendations();
  }, []);

  const loadRecommendations = async () => {
    try {
      const userId = getUserId();
      const response = await fetch(`/api/recommendations?userId=${userId}&limit=3`);
      
      if (response.ok) {
        const data = await response.json();
        const recs = data.recommendations || [];
        
        console.log('[ThreeItemGrid] Raw recommendations:', recs);
        
        // Transform to Product format
        const formattedProducts = recs.map((rec: any) => {
          console.log('[ThreeItemGrid] Processing product:', rec.title, 'Price:', rec.price);
          
          return {
            id: rec.id,
            handle: rec.handle,
            title: rec.title,
            thumbnail: rec.thumbnail || 'https://via.placeholder.com/300x300?text=No+Image',
            featuredImage: { url: rec.thumbnail || 'https://via.placeholder.com/300x300?text=No+Image' },
            priceRange: {
              maxVariantPrice: {
                amount: rec.price?.amount || '0',
                currencyCode: rec.price?.currencyCode || 'VND'
              }
            }
          };
        });
        
        console.log('[ThreeItemGrid] Formatted products:', formattedProducts);
        setProducts(formattedProducts);
      }
    } catch (error) {
      console.error('Failed to load featured recommendations:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <section className="mx-auto grid max-w-screen-2xl gap-4 px-4 pb-4 md:grid-cols-6 md:grid-rows-2 lg:h-[600px]">
        <div className="aspect-square animate-pulse rounded-lg bg-neutral-200 dark:bg-neutral-800 md:col-span-4 md:row-span-2" />
        <div className="aspect-square animate-pulse rounded-lg bg-neutral-200 dark:bg-neutral-800 md:col-span-2 md:row-span-1" />
        <div className="aspect-square animate-pulse rounded-lg bg-neutral-200 dark:bg-neutral-800 md:col-span-2 md:row-span-1" />
      </section>
    );
  }

  // If not enough products, return null or show partial (for now return null)
  if (products.length < 3) {
    return null;
  }

  const [firstProduct, secondProduct, thirdProduct] = products as [Product, Product, Product];

  return (
    <section className="mx-auto grid max-w-screen-2xl gap-4 px-4 pb-4 md:grid-cols-6 md:grid-rows-2 lg:h-[600px]">
      <ThreeItemGridItem size="full" item={firstProduct} priority={true} />
      <ThreeItemGridItem size="half" item={secondProduct} priority={true} />
      <ThreeItemGridItem size="half" item={thirdProduct} />
    </section>
  );
}

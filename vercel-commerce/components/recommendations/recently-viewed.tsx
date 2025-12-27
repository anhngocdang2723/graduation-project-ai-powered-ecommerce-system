'use client';

import { GridTileImage } from 'components/grid/tile';
import { getRecentlyViewed } from 'lib/tracking/user-behavior';
import Link from 'next/link';
import { useEffect, useState } from 'react';

export function RecentlyViewedProducts() {
  const [products, setProducts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRecentlyViewed();
  }, []);

  const loadRecentlyViewed = async () => {
    try {
      const handles = getRecentlyViewed(4);
      
      if (handles.length === 0) {
        setLoading(false);
        return;
      }

      // Fetch product details
      const productPromises = handles.map(async (handle) => {
        try {
          const response = await fetch(`/api/product/${handle}`);
          if (response.ok) {
            return await response.json();
          }
        } catch (error) {
          console.error(`Failed to fetch ${handle}:`, error);
        }
        return null;
      });

      const productsData = (await Promise.all(productPromises)).filter(p => p !== null);
      setProducts(productsData);
    } catch (error) {
      console.error('Failed to load recently viewed:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="mb-12">
        <h2 className="mb-6 text-2xl font-bold tracking-tight">Recently Viewed</h2>
        <div className="flex gap-4 overflow-x-auto pb-4 scrollbar-hide">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="min-w-[180px] animate-pulse md:min-w-[240px]">
              <div className="aspect-square rounded-lg bg-neutral-200 dark:bg-neutral-800" />
              <div className="mt-2 h-4 rounded bg-neutral-200 dark:bg-neutral-800" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (products.length === 0) {
    return null;
  }

  return (
    <div className="mb-12">
      <div className="mb-6 flex items-center justify-between">
        <h2 className="text-2xl font-bold tracking-tight">Recently Viewed</h2>
        <span className="text-sm text-neutral-500 dark:text-neutral-400">
          {products.length} {products.length === 1 ? 'item' : 'items'}
        </span>
      </div>
      <div className="flex gap-4 overflow-x-auto pb-4 scrollbar-hide">
        {products.map((product) => (
          <Link
            key={product.handle}
            href={`/product/${product.handle}`}
            className="group min-w-[180px] transition-transform hover:scale-105 md:min-w-[240px]"
          >
            <div className="aspect-square overflow-hidden rounded-lg">
              <GridTileImage
                alt={product.title}
                label={{
                  title: product.title,
                  amount: product.priceRange?.maxVariantPrice?.amount || '0',
                  currencyCode: product.priceRange?.maxVariantPrice?.currencyCode || 'VND',
                  position: 'bottom'
                }}
                src={product.thumbnail || product.featuredImage?.url}
                fill
                sizes="240px"
              />
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}

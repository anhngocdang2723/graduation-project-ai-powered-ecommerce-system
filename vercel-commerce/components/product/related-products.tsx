'use client';

import { GridTileImage } from '../grid/tile';
import { getUserId } from 'lib/tracking/user-behavior';
import Link from 'next/link';
import { useEffect, useState } from 'react';

interface RelatedProductsProps {
  productId: string;
  productHandle: string;
  categoryId?: string;
}

export function RelatedProducts({ productId, productHandle, categoryId }: RelatedProductsProps) {
  const [products, setProducts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [algorithm, setAlgorithm] = useState('');

  useEffect(() => {
    loadSimilarProducts();
  }, [productHandle]);

  const loadSimilarProducts = async () => {
    try {
      const userId = getUserId();
      const response = await fetch(
        `/api/recommendations?userId=${userId}&productHandle=${productHandle}&context=product_page&limit=6`
      );
      
      if (response.ok) {
        const data = await response.json();
        setProducts(data.recommendations || []);
        setAlgorithm(data.algorithm || '');
      }
    } catch (error) {
      console.error('Failed to load similar products:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="py-8">
        <div className="mb-6">
          <h2 className="text-2xl font-bold">You May Also Like</h2>
          <p className="text-neutral-600 dark:text-neutral-400">
            Similar products that might interest you
          </p>
        </div>
        <div className="flex gap-4 overflow-x-auto pb-4 scrollbar-hide">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="min-w-[180px] animate-pulse md:min-w-[200px]">
              <div className="aspect-square rounded-lg bg-neutral-200 dark:bg-neutral-800" />
              <div className="mt-2 h-4 rounded bg-neutral-200 dark:bg-neutral-800" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (products.length === 0) return null;

  return (
    <div className="py-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">You May Also Like</h2>
          <p className="text-neutral-600 dark:text-neutral-400">
            Similar products that might interest you
          </p>
        </div>
        {algorithm && (
          <span className="rounded-full bg-neutral-100 px-3 py-1 text-xs font-medium text-neutral-700 dark:bg-neutral-800 dark:text-neutral-300">
            {algorithm}
          </span>
        )}
      </div>

      <div className="flex gap-4 overflow-x-auto pb-4 scrollbar-hide">
        {products.map((product) => (
          <Link
            key={product.handle}
            href={`/product/${product.handle}`}
            className="group min-w-[180px] transition-transform hover:scale-105 md:min-w-[200px]"
          >
            <div className="aspect-square overflow-hidden rounded-lg">
              <GridTileImage
                alt={product.title}
                label={{
                  title: product.title,
                  amount: product.price?.amount || '0',
                  currencyCode: product.price?.currencyCode || 'VND',
                  position: 'bottom'
                }}
                src={product.thumbnail || product.featuredImage?.url}
                fill
                sizes="200px"
              />
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}

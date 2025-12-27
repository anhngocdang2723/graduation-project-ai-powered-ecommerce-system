'use client';

import { GridTileImage } from 'components/grid/tile';
import { getUserId } from 'lib/tracking/user-behavior';
import Link from 'next/link';
import { useEffect, useState } from 'react';
import { useLanguage } from 'lib/i18n/context';

export function PersonalizedRecommendations() {
  const { t } = useLanguage();
  const [topSelling, setTopSelling] = useState<any[]>([]);
  const [mostViewed, setMostViewed] = useState<any[]>([]);
  const [mostWishlisted, setMostWishlisted] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRecommendations();
  }, []);

  const loadRecommendations = async () => {
    try {
      const userId = getUserId();
      
      const [topSellingRes, mostViewedRes, mostWishlistedRes] = await Promise.all([
        fetch(`/api/recommendations?userId=${userId}&context=top_selling&limit=8`),
        fetch(`/api/recommendations?userId=${userId}&context=most_viewed&limit=8`),
        fetch(`/api/recommendations?userId=${userId}&context=most_wishlisted&limit=8`)
      ]);

      if (topSellingRes.ok) {
        const data = await topSellingRes.json();
        setTopSelling(data.recommendations || []);
      }
      
      if (mostViewedRes.ok) {
        const data = await mostViewedRes.json();
        setMostViewed(data.recommendations || []);
      }
      
      if (mostWishlistedRes.ok) {
        const data = await mostWishlistedRes.json();
        setMostWishlisted(data.recommendations || []);
      }
      
    } catch (error) {
      console.error('Failed to load recommendations:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="mb-8">
        <h2 className="mb-4 text-2xl font-bold">{t('recommendations.title')}</h2>
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="animate-pulse">
              <div className="aspect-square rounded-lg bg-neutral-200 dark:bg-neutral-800" />
              <div className="mt-2 h-4 rounded bg-neutral-200 dark:bg-neutral-800" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (topSelling.length === 0 && mostViewed.length === 0 && mostWishlisted.length === 0) {
    return null;
  }

  const renderProductList = (title: string, products: any[]) => {
    if (products.length === 0) return null;
    
    return (
      <div className="mb-10">
        <h3 className="mb-4 text-xl font-semibold tracking-tight">{title}</h3>
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
                    amount: product.price?.amount || '0',
                    currencyCode: product.price?.currencyCode || 'VND',
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
  };

  return (
    <div className="mb-12">
      <h2 className="mb-6 text-2xl font-bold tracking-tight">{t('recommendations.title')}</h2>
      
      {renderProductList(t('recommendations.bestSelling'), topSelling)}
      {renderProductList(t('recommendations.mostInterested'), mostViewed)}
      {renderProductList(t('recommendations.mostFavorited'), mostWishlisted)}
    </div>
  );
}

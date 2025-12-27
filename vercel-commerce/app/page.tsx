import { Carousel } from 'components/carousel';
import { CategoryGrid } from 'components/category-grid';
import { CollectionShowcase } from 'components/collection-showcase';
import { FeaturedProducts } from 'components/featured-products';
import { ThreeItemGrid as ThreeItemGridRecommended } from 'components/grid/three-items-recommended';
import Footer from 'components/layout/footer';
import { PersonalizedRecommendations } from 'components/recommendations/personalized';
import { RecentlyViewedProducts } from 'components/recommendations/recently-viewed';
import { Suspense } from 'react';

export const runtime = 'edge';

export const revalidate = 43200; // 12 hours

export const metadata = {
  description: 'High-performance ecommerce store built with Next.js, Vercel, and Medusa.',
  openGraph: {
    type: 'website'
  }
};

export default async function HomePage() {
  return (
    <>
      <ThreeItemGridRecommended />
      
      <Suspense fallback={<div className="h-64" />}>
        <Carousel />
      </Suspense>
      
      {/* Personalized sections */}
      <div className="mx-auto max-w-screen-2xl px-4 py-8">
        <RecentlyViewedProducts />
        <PersonalizedRecommendations />
      </div>
      
      <Suspense fallback={<div className="h-20" />}>
        <CategoryGrid />
      </Suspense>
      
      <Suspense fallback={<div className="h-96" />}>
        <CollectionShowcase />
      </Suspense>
      
      <Suspense fallback={<div className="h-96" />}>
        <FeaturedProducts />
      </Suspense>
      
      <Suspense>
        <Footer />
      </Suspense>
    </>
  );
}

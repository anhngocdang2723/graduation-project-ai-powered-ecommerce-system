'use client';

import { HeartIcon as HeartSolidIcon } from '@heroicons/react/24/solid';
import { ShoppingCartIcon } from '@heroicons/react/24/outline';
import { useLanguage } from 'lib/i18n/context';
import Link from 'next/link';
import Image from 'next/image';
import { useEffect, useState } from 'react';

interface WishlistItem {
  id: string;
  handle: string;
  addedAt: string;
}

interface ProductData {
  id: string;
  handle: string;
  title: string;
  thumbnail: string;
  price: string;
}

export function WishlistGrid() {
  const { t } = useLanguage();
  const [wishlistItems, setWishlistItems] = useState<WishlistItem[]>([]);
  const [products, setProducts] = useState<ProductData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadWishlist();

    const handleWishlistUpdate = () => {
      loadWishlist();
    };

    window.addEventListener('wishlist-updated', handleWishlistUpdate);
    return () => window.removeEventListener('wishlist-updated', handleWishlistUpdate);
  }, []);

  const loadWishlist = async () => {
    const stored = localStorage.getItem('wishlist');
    console.log('Wishlist from localStorage:', stored);
    const items: WishlistItem[] = stored ? JSON.parse(stored) : [];
    console.log('Parsed wishlist items:', items);
    setWishlistItems(items);

    // Fetch product details for each wishlist item
    const productPromises = items.map(async (item) => {
      try {
        const response = await fetch(`/api/product/${item.handle}`);
        console.log(`Fetch response for ${item.handle}:`, response.status);
        if (response.ok) {
          const product = await response.json();
          console.log('Product data:', product);
          return {
            id: item.id,
            handle: item.handle,
            title: product.title || 'Product',
            thumbnail: product.thumbnail || product.featuredImage?.url || '',
            price: product.variants?.[0]?.prices?.[0]?.amount 
              ? `$${(product.variants[0].prices[0].amount / 100).toFixed(2)}`
              : product.priceRange?.maxVariantPrice?.amount || 'N/A'
          };
        } else {
          console.error(`Failed to fetch ${item.handle}: ${response.status}`);
        }
      } catch (error) {
        console.error(`Failed to fetch product ${item.handle}:`, error);
      }
      return null;
    });

    const productsData = (await Promise.all(productPromises)).filter(
      (p): p is ProductData => p !== null
    );
    setProducts(productsData);
    setLoading(false);
  };

  const removeFromWishlist = (productId: string) => {
    const updated = wishlistItems.filter((item) => item.id !== productId);
    localStorage.setItem('wishlist', JSON.stringify(updated));
    setWishlistItems(updated);
    setProducts(products.filter((p) => p.id !== productId));
    window.dispatchEvent(new Event('wishlist-updated'));
  };

  if (loading) {
    return (
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="animate-pulse">
            <div className="aspect-square rounded-lg bg-neutral-200 dark:bg-neutral-800" />
            <div className="mt-3 h-4 rounded bg-neutral-200 dark:bg-neutral-800" />
            <div className="mt-2 h-4 w-20 rounded bg-neutral-200 dark:bg-neutral-800" />
          </div>
        ))}
      </div>
    );
  }

  if (products.length === 0) {
    return (
      <div className="flex min-h-[400px] flex-col items-center justify-center rounded-lg border border-neutral-200 bg-white p-12 dark:border-neutral-800 dark:bg-black">
        <HeartSolidIcon className="mb-4 h-16 w-16 text-neutral-300 dark:text-neutral-700" />
        <h2 className="mb-2 text-xl font-semibold">{t('wishlist.empty')}</h2>
        <p className="mb-6 text-neutral-600 dark:text-neutral-400">
          {t('wishlist.startAdding')}
        </p>
        <Link
          href="/search"
          className="rounded-full bg-blue-600 px-6 py-3 text-white transition hover:bg-blue-700"
        >
          {t('account.continueShopping')}
        </Link>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
      {products.map((product) => (
        <div
          key={product.id}
          className="group relative rounded-lg border border-neutral-200 bg-white p-4 transition hover:shadow-lg dark:border-neutral-800 dark:bg-black"
        >
          <button
            onClick={() => removeFromWishlist(product.id)}
            className="absolute right-2 top-2 z-10 rounded-full bg-white p-2 shadow-md transition hover:bg-red-50 dark:bg-neutral-900 dark:hover:bg-red-950"
            aria-label="Remove from wishlist"
          >
            <HeartSolidIcon className="h-5 w-5 text-red-500" />
          </button>

          <Link href={`/product/${product.handle}`}>
            <div className="aspect-square overflow-hidden rounded-lg bg-neutral-100 dark:bg-neutral-900">
              {product.thumbnail ? (
                <Image
                  src={product.thumbnail}
                  alt={product.title}
                  width={300}
                  height={300}
                  className="h-full w-full object-contain p-4 transition group-hover:scale-105"
                />
              ) : (
                <div className="flex h-full w-full items-center justify-center">
                  <span className="text-neutral-400">No image</span>
                </div>
              )}
            </div>

            <div className="mt-3">
              <h3 className="line-clamp-2 font-semibold text-neutral-900 dark:text-neutral-100">
                {product.title}
              </h3>
              <p className="mt-1 text-lg font-bold text-blue-600 dark:text-blue-400">
                {product.price}
              </p>
            </div>
          </Link>

          <button
            className="mt-4 flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-white transition hover:bg-blue-700"
            onClick={() => {
              // TODO: Implement add to cart
              console.log('Add to cart:', product.id);
            }}
          >
            <ShoppingCartIcon className="h-5 w-5" />
            {t('product.addToCart')}
          </button>
        </div>
      ))}
    </div>
  );
}

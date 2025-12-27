'use client';

import { useEffect } from 'react';
import { trackInteraction } from 'lib/tracking/user-behavior';

interface ProductTrackingProps {
  productId: string;
  productHandle: string;
  category?: string;
  price?: string;
}

export function ProductViewTracker({ productId, productHandle, category, price }: ProductTrackingProps) {
  useEffect(() => {
    // Track product view
    trackInteraction({
      productId,
      productHandle,
      interactionType: 'view',
      metadata: {
        category,
        price,
        viewedAt: new Date().toISOString(),
      },
    });
  }, [productId, productHandle, category, price]);

  return null; // This component doesn't render anything
}

export function trackAddToCart(productId: string, productHandle: string, quantity: number) {
  trackInteraction({
    productId,
    productHandle,
    interactionType: 'add_to_cart',
    metadata: {
      quantity,
    },
  });
}

export function trackWishlist(productId: string, productHandle: string, action: 'add' | 'remove') {
  trackInteraction({
    productId,
    productHandle,
    interactionType: 'wishlist',
    metadata: {
      action,
    },
  });
}

export function trackSearch(query: string, resultCount: number) {
  trackInteraction({
    interactionType: 'search',
    metadata: {
      query,
      resultCount,
    },
  });
}

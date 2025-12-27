'use client';

import { HeartIcon } from '@heroicons/react/24/outline';
import { HeartIcon as HeartSolidIcon } from '@heroicons/react/24/solid';
import { trackWishlist } from 'components/tracking/tracking-wrapper';
import { useState, useEffect } from 'react';

interface WishlistButtonProps {
  productId: string;
  productHandle: string;
  size?: 'sm' | 'md' | 'lg';
}

export default function WishlistButton({ productId, productHandle, size = 'md' }: WishlistButtonProps) {
  const [isInWishlist, setIsInWishlist] = useState(false);
  const [loading, setLoading] = useState(false);

  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-5 w-5',
    lg: 'h-6 w-6'
  };

  useEffect(() => {
    // Check if product is in wishlist
    const wishlist = JSON.parse(localStorage.getItem('wishlist') || '[]');
    setIsInWishlist(wishlist.some((item: any) => item.id === productId));
  }, [productId]);

  const toggleWishlist = async () => {
    setLoading(true);
    
    try {
      const wishlist = JSON.parse(localStorage.getItem('wishlist') || '[]');
      
      if (isInWishlist) {
        // Remove from wishlist
        const updated = wishlist.filter((item: any) => item.id !== productId);
        localStorage.setItem('wishlist', JSON.stringify(updated));
        setIsInWishlist(false);
        trackWishlist(productId, productHandle, 'remove');
      } else {
        // Add to wishlist
        const updated = [...wishlist, { id: productId, handle: productHandle, addedAt: new Date().toISOString() }];
        localStorage.setItem('wishlist', JSON.stringify(updated));
        setIsInWishlist(true);
        trackWishlist(productId, productHandle, 'add');
      }
      
      // Dispatch event for other components to listen
      window.dispatchEvent(new Event('wishlist-updated'));
    } catch (error) {
      console.error('Failed to update wishlist:', error);
    } finally {
      setLoading(false);
    }
  };

  const Icon = isInWishlist ? HeartSolidIcon : HeartIcon;

  return (
    <button
      onClick={toggleWishlist}
      disabled={loading}
      className={`rounded-full p-2 transition-all hover:bg-neutral-100 dark:hover:bg-neutral-900 ${
        loading ? 'opacity-50' : ''
      }`}
      aria-label={isInWishlist ? 'Remove from wishlist' : 'Add to wishlist'}
      title={isInWishlist ? 'Remove from wishlist' : 'Add to wishlist'}
    >
      <Icon
        className={`${sizeClasses[size]} ${
          isInWishlist ? 'text-red-500' : 'text-gray-600 dark:text-gray-400'
        }`}
      />
    </button>
  );
}

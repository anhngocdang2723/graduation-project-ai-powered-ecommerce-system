'use client';

import { CheckCircleIcon, ExclamationCircleIcon } from '@heroicons/react/24/outline';

interface StockDisplayProps {
  quantity: number;
  className?: string;
}

export function StockDisplay({ quantity, className = '' }: StockDisplayProps) {
  // Only show stock message when out of stock or low stock
  if (quantity === 0) {
    return (
      <div className={`flex items-center gap-2 text-red-600 dark:text-red-400 ${className}`}>
        <ExclamationCircleIcon className="h-5 w-5" />
        <span className="font-semibold">Out of Stock</span>
      </div>
    );
  }

  if (quantity <= 5) {
    return (
      <div className={`flex items-center gap-2 text-orange-600 dark:text-orange-400 ${className}`}>
        <ExclamationCircleIcon className="h-5 w-5" />
        <span className="font-semibold">Only {quantity} left in stock</span>
      </div>
    );
  }

  // Don't show stock indicator when product is normally in stock (> 5 items)
  return null;
}

interface StockBadgeProps {
  quantity: number;
}

export function StockBadge({ quantity }: StockBadgeProps) {
  if (quantity === 0) {
    return (
      <span className="absolute right-2 top-2 rounded-full bg-red-500 px-3 py-1 text-xs font-bold text-white">
        Out of Stock
      </span>
    );
  }

  if (quantity <= 5) {
    return (
      <span className="absolute right-2 top-2 rounded-full bg-orange-500 px-3 py-1 text-xs font-bold text-white">
        Low Stock
      </span>
    );
  }

  return null;
}

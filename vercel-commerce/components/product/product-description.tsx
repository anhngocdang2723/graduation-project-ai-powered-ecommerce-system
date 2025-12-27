'use client';

import { AddToCart } from 'components/cart/add-to-cart';
import Price from 'components/price';
import Prose from 'components/prose';
import { Product } from 'lib/medusa/types';
import WishlistButton from './wishlist-button';
import { StockDisplay } from './stock-display';
import { VariantSelector } from './variant-selector';
import { useState } from 'react';
import { MinusIcon, PlusIcon } from '@heroicons/react/24/outline';

export function ProductDescription({ product }: { product: Product }) {
  const [quantity, setQuantity] = useState(1);
  const maxQuantity = product.variants[0]?.inventory_quantity || 99;

  const handleQuantityChange = (delta: number) => {
    const newQuantity = quantity + delta;
    if (newQuantity >= 1 && newQuantity <= maxQuantity) {
      setQuantity(newQuantity);
    }
  };

  return (
    <>
      <div className="mb-6 flex flex-col border-b pb-6 dark:border-neutral-700">
        <div className="mb-2 flex items-start justify-between">
          <h1 className="text-5xl font-medium">{product.title}</h1>
          <WishlistButton productId={product.id!} productHandle={product.handle} size="lg" />
        </div>
        <div className="mr-auto w-auto rounded-full bg-blue-600 p-2 text-sm text-white">
          <Price
            amount={product.priceRange.maxVariantPrice.amount}
            currencyCode={product.priceRange.maxVariantPrice.currencyCode}
          />
        </div>
      </div>
      <VariantSelector options={product.options} variants={product.variants} />

      {/* Stock availability display - only shows when out of stock or low stock */}
      {product.variants && product.variants.length > 0 && (
        <div className="mb-6">
          <StockDisplay 
            quantity={product.variants[0]?.inventory_quantity || 0} 
          />
        </div>
      )}

      {product.descriptionHtml ? (
        <Prose
          className="mb-6 text-sm leading-tight dark:text-white/[60%]"
          html={product.descriptionHtml}
        />
      ) : null}

      {/* Quantity selector */}
      {product.availableForSale && (
        <div className="mb-6">
          <label className="mb-2 block text-sm font-medium text-neutral-700 dark:text-neutral-300">
            Quantity
          </label>
          <div className="flex items-center gap-4">
            <div className="flex h-11 items-center rounded-full border border-neutral-200 dark:border-neutral-700">
              <button
                onClick={() => handleQuantityChange(-1)}
                disabled={quantity <= 1}
                className="flex h-full items-center justify-center rounded-l-full px-4 transition hover:bg-neutral-100 disabled:cursor-not-allowed disabled:opacity-50 dark:hover:bg-neutral-800"
                aria-label="Decrease quantity"
              >
                <MinusIcon className="h-4 w-4" />
              </button>
              <span className="w-12 text-center text-sm font-medium">{quantity}</span>
              <button
                onClick={() => handleQuantityChange(1)}
                disabled={quantity >= maxQuantity}
                className="flex h-full items-center justify-center rounded-r-full px-4 transition hover:bg-neutral-100 disabled:cursor-not-allowed disabled:opacity-50 dark:hover:bg-neutral-800"
                aria-label="Increase quantity"
              >
                <PlusIcon className="h-4 w-4" />
              </button>
            </div>
            <span className="text-xs text-neutral-500 dark:text-neutral-400">
              {maxQuantity > 100 ? 'In Stock' : `Max: ${maxQuantity}`}
            </span>
          </div>
        </div>
      )}

      <AddToCart 
        variants={product.variants} 
        availableForSale={product.availableForSale}
        quantity={quantity}
      />
    </>
  );
}

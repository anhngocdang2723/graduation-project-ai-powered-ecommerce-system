'use client';

import Price from 'components/price';
import Prose from 'components/prose';
import { Product } from 'lib/medusa/types';
import { VariantSelector } from '../product/variant-selector';
import { UpdateCartItem } from './update-cart-item';

import { useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { createUrl } from 'lib/utils';

export function EditItemView({ 
  product, 
  lineId, 
  quantity,
  initialSelectedOptions 
}: { 
  product: Product; 
  lineId: string; 
  quantity: number;
  initialSelectedOptions: { name: string; value: string }[];
}) {
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    // If no search params are present, populate them from the initial selected options
    // Only run this once on mount or if initialSelectedOptions changes
    if (searchParams.toString() === '' && initialSelectedOptions.length > 0) {
      const newParams = new URLSearchParams();
      initialSelectedOptions.forEach((option) => {
        newParams.set(option.name.toLowerCase(), option.value);
      });
      
      const url = createUrl(window.location.pathname, newParams);
      router.replace(url);
    }
  }, [initialSelectedOptions, router]); // Removed searchParams from dependency array to prevent loop

  return (
    <>
      <div className="mb-6 flex flex-col border-b pb-6 dark:border-neutral-700">
        <h1 className="mb-2 text-5xl font-medium">{product.title}</h1>
        <div className="mr-auto w-auto rounded-full bg-blue-600 p-2 text-sm text-white">
          <Price
            amount={product.priceRange.maxVariantPrice.amount}
            currencyCode={product.priceRange.maxVariantPrice.currencyCode}
          />
        </div>
      </div>
      <VariantSelector options={product.options} variants={product.variants} />

      {product.descriptionHtml ? (
        <Prose
          className="mb-6 text-sm leading-tight dark:text-white/[60%]"
          html={product.descriptionHtml}
        />
      ) : null}

      <UpdateCartItem 
        lineId={lineId}
        variants={product.variants} 
        availableForSale={product.availableForSale} 
        currentQuantity={quantity}
      />
    </>
  );
}

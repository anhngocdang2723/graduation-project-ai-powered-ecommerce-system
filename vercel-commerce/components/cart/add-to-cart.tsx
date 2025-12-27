'use client';

import { PlusIcon } from '@heroicons/react/24/outline';
import clsx from 'clsx';
import { addItem } from 'components/cart/actions';
import { trackAddToCart } from 'components/tracking/tracking-wrapper';
import LoadingDots from 'components/loading-dots';
import { useLanguage } from 'lib/i18n/context';
import { ProductVariant } from 'lib/medusa/types';
import { useRouter, useSearchParams } from 'next/navigation';
import { useTransition } from 'react';

export function AddToCart({
  variants,
  availableForSale,
  quantity = 1
}: {
  variants: ProductVariant[];
  availableForSale: boolean;
  quantity?: number;
}) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isPending, startTransition] = useTransition();
  const { t } = useLanguage();
  const defaultVariantId = variants.length === 1 ? variants[0]?.id : undefined;
  const variant = variants.find((variant: ProductVariant) =>
    variant.selectedOptions.every(
      (option) => option.value === searchParams.get(option.name.toLowerCase())
    )
  );
  const selectedVariantId = variant?.id || defaultVariantId;
  const title = !availableForSale
    ? t('product.outOfStock')
    : !selectedVariantId
    ? t('product.selectOptions')
    : undefined;

  return (
    <button
      aria-label={t('product.addToCart')}
      disabled={isPending || !availableForSale || !selectedVariantId}
      title={title}
      onClick={() => {
        // Safeguard in case someone messes with `disabled` in devtools.
        if (!availableForSale || !selectedVariantId) {
          console.warn('Add to cart blocked:', { availableForSale, selectedVariantId });
          return;
        }

        console.log('Adding to cart:', { selectedVariantId, variant, quantity });

        startTransition(async () => {
          try {
            const error = await addItem(selectedVariantId, quantity);

            if (error) {
              console.error("Add to cart error:", error);
              alert(`Failed to add to cart: ${error}`);
              return;
            }

            console.log('Successfully added to cart');
            
            // Track add to cart event
            trackAddToCart(
              variant?.product?.id || '',
              variant?.product?.handle || '',
              quantity
            );
            
            router.refresh();
          } catch (e) {
             console.error("Add to cart exception:", e);
             alert("Failed to add item to cart. Please try again.");
          }
        });
      }}
      className={clsx(
        'relative flex w-full items-center justify-center rounded-full bg-blue-600 p-4 tracking-wide text-white hover:opacity-90',
        {
          'cursor-not-allowed opacity-60 hover:opacity-60': !availableForSale || !selectedVariantId,
          'cursor-not-allowed': isPending
        }
      )}
    >
      <div className="absolute left-0 ml-4">
        {!isPending ? <PlusIcon className="h-5" /> : <LoadingDots className="mb-3 bg-white" />}
      </div>
      <span>{availableForSale ? t('product.addToCart') : t('product.outOfStock')}</span>
    </button>
  );
}

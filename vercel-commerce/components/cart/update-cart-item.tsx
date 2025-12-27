'use client';

import { ArrowPathIcon } from '@heroicons/react/24/outline';
import clsx from 'clsx';
import { updateLineItemVariant } from 'components/cart/actions';
import LoadingDots from 'components/loading-dots';
import { useLanguage } from 'lib/i18n/context';
import { ProductVariant } from 'lib/medusa/types';
import { useRouter, useSearchParams } from 'next/navigation';
import { useState, useTransition } from 'react';
import { MinusIcon, PlusIcon } from '@heroicons/react/24/outline';

export function UpdateCartItem({
  lineId,
  variants,
  availableForSale,
  currentQuantity
}: {
  lineId: string;
  variants: ProductVariant[];
  availableForSale: boolean;
  currentQuantity: number;
}) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isPending, startTransition] = useTransition();
  const [quantity, setQuantity] = useState(currentQuantity);
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
    <div className="flex flex-col gap-4">
      <div className="flex items-center gap-4">
        <label className="text-sm font-medium text-gray-900 dark:text-white">Quantity</label>
        <div className="flex items-center rounded-full border border-neutral-200 dark:border-neutral-700">
          <button
            onClick={() => setQuantity(Math.max(1, quantity - 1))}
            className="p-2 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-l-full"
            disabled={quantity <= 1}
          >
            <MinusIcon className="h-4 w-4" />
          </button>
          <span className="px-4 text-sm">{quantity}</span>
          <button
            onClick={() => setQuantity(quantity + 1)}
            className="p-2 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-r-full"
          >
            <PlusIcon className="h-4 w-4" />
          </button>
        </div>
      </div>

      <button
        aria-label="Update Cart"
        disabled={isPending || !availableForSale || !selectedVariantId}
        title={title}
        onClick={() => {
          if (!availableForSale || !selectedVariantId) return;

          startTransition(async () => {
            const error = await updateLineItemVariant(lineId, selectedVariantId, quantity);

            if (error) {
              throw new Error(error.toString());
            }

            router.push('/cart');
            router.refresh();
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
          {!isPending ? <ArrowPathIcon className="h-5" /> : <LoadingDots className="mb-3 bg-white" />}
        </div>
        <span>Update Cart</span>
      </button>
    </div>
  );
}

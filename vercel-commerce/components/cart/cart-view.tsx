'use client';

import { useLanguage } from 'lib/i18n/context';
import type { Cart } from 'lib/medusa/types';
import Image from 'next/image';
import Link from 'next/link';
import Price from 'components/price';
import { DEFAULT_OPTION } from 'lib/constants';
import { createUrl } from 'lib/utils';
import EditItemQuantityButton from './edit-item-quantity-button';
import DeleteItemButton from './delete-item-button';
import { ShoppingCartIcon } from '@heroicons/react/24/outline';

export default function CartView({ cart }: { cart: Cart | undefined }) {
  const { t } = useLanguage();

  if (!cart || cart.lines.length === 0) {
    return (
      <div className="flex min-h-[50vh] flex-col items-center justify-center overflow-hidden">
        <ShoppingCartIcon className="h-16" />
        <p className="mt-6 text-center text-2xl font-bold">{t('cart.empty')}</p>
        <Link href="/" className="mt-4 rounded-full bg-blue-600 px-6 py-3 text-white hover:bg-blue-700">
            {t('nav.goHome')}
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-screen-2xl px-4 py-8">
      <h1 className="mb-8 text-3xl font-bold">{t('cart.title')}</h1>
      <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <ul className="divide-y divide-neutral-200 border-b border-t border-neutral-200 dark:divide-neutral-700 dark:border-neutral-700">
            {cart.lines.map((item, i) => {
              const merchandiseSearchParams = {} as any;
              item.merchandise.selectedOptions.forEach(({ name, value }) => {
                if (value !== DEFAULT_OPTION) {
                  merchandiseSearchParams[name.toLowerCase()] = value;
                }
              });
              const merchandiseUrl = `/cart/edit/${item.id}`;

              return (
                <li key={i} className="flex py-6">
                  <div className="relative h-24 w-24 flex-shrink-0 overflow-hidden rounded-md border border-neutral-200 dark:border-neutral-700">
                    <Image
                      src={item.merchandise.product.featuredImage.url}
                      alt={item.merchandise.product.featuredImage.altText || item.merchandise.product.title}
                      fill
                      className="object-cover object-center"
                    />
                  </div>

                  <div className="ml-4 flex flex-1 flex-col">
                    <div>
                      <div className="flex justify-between text-base font-medium text-gray-900 dark:text-white">
                        <h3>
                          <Link href={merchandiseUrl}>{item.merchandise.product.title}</Link>
                        </h3>
                        <Price
                          amount={item.cost.totalAmount.amount}
                          currencyCode={item.cost.totalAmount.currencyCode}
                        />
                      </div>
                      {item.merchandise.selectedOptions.length > 0 && (
                        <div className="mt-1 flex flex-wrap gap-2">
                          {item.merchandise.selectedOptions.map((option) => (
                            <span key={option.name} className="inline-flex items-center rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-800 dark:bg-gray-800 dark:text-gray-200">
                              {option.name}: {option.value}
                            </span>
                          ))}
                        </div>
                      )}
                      {item.merchandise.product.description && (
                         <p className="mt-1 line-clamp-2 text-xs text-gray-500 dark:text-gray-400">
                            {item.merchandise.product.description}
                         </p>
                      )}
                    </div>
                    <div className="flex flex-1 items-end justify-between text-sm">
                      <div className="flex items-center border border-neutral-200 dark:border-neutral-700 rounded-full">
                        <EditItemQuantityButton item={item} type="minus" />
                        <span className="px-2">{item.quantity}</span>
                        <EditItemQuantityButton item={item} type="plus" />
                      </div>
                      <DeleteItemButton item={item} />
                    </div>
                  </div>
                </li>
              );
            })}
          </ul>
        </div>

        <div className="lg:col-span-1">
          <div className="rounded-lg bg-gray-50 px-4 py-6 dark:bg-neutral-900 sm:p-6 lg:p-8">
            <h2 className="text-lg font-medium text-gray-900 dark:text-white">{t('cart.title')}</h2>
            <div className="mt-6 space-y-4">
              <div className="flex items-center justify-between border-b border-gray-200 pb-4 dark:border-gray-700">
                <div className="text-base font-medium text-gray-900 dark:text-white">{t('cart.subtotal')}</div>
                <Price
                  amount={cart.cost.subtotalAmount.amount}
                  currencyCode={cart.cost.subtotalAmount.currencyCode}
                />
              </div>
              <div className="flex items-center justify-between pt-4">
                <div className="text-base font-medium text-gray-900 dark:text-white">{t('cart.taxes')}</div>
                <Price
                  amount={cart.cost.totalTaxAmount.amount}
                  currencyCode={cart.cost.totalTaxAmount.currencyCode}
                />
              </div>
              <div className="flex items-center justify-between border-t border-gray-200 pt-4 dark:border-gray-700">
                <div className="text-base font-medium text-gray-900 dark:text-white">{t('cart.total')}</div>
                <Price
                  amount={cart.cost.totalAmount.amount}
                  currencyCode={cart.cost.totalAmount.currencyCode}
                />
              </div>
            </div>
            <div className="mt-6">
              <a
                href={cart.checkoutUrl}
                className="flex w-full items-center justify-center rounded-md border border-transparent bg-blue-600 px-6 py-3 text-base font-medium text-white shadow-sm hover:bg-blue-700"
              >
                {t('cart.proceedToCheckout')}
              </a>
            </div>
            
            <div className="mt-8 space-y-4 text-sm text-gray-500 dark:text-gray-400">
                <div>
                    <h3 className="font-semibold text-gray-900 dark:text-white">{t('cart.instructions')}</h3>
                    <p>{t('cart.instructionsText')}</p>
                </div>
                <div>
                    <h3 className="font-semibold text-gray-900 dark:text-white">{t('cart.notes')}</h3>
                    <p>{t('cart.notesText')}</p>
                </div>
                <div>
                    <h3 className="font-semibold text-gray-900 dark:text-white">{t('cart.fees')}</h3>
                    <p>{t('cart.feesText')}</p>
                </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

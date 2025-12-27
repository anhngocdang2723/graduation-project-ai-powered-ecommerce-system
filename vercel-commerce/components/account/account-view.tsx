'use client';

import { logoutAction } from 'components/auth/actions';
import AddressForm from 'components/auth/address-form';
import { useLanguage } from 'lib/i18n/context';
import Link from 'next/link';

export default function AccountView({ customer }: { customer: any }) {
  const { t } = useLanguage();

  return (
    <div className="mx-auto max-w-2xl py-24 px-4 sm:px-6 lg:px-8">
      <div className="md:flex md:items-center md:justify-between md:space-x-5">
        <div className="flex items-start space-x-5">
          <div className="pt-1.5">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{t('account.title')}</h1>
            <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
              {t('account.welcome')}, {customer.first_name}
            </p>
          </div>
        </div>
        <div className="mt-6 flex flex-col-reverse justify-stretch space-y-4 space-y-reverse sm:flex-row-reverse sm:justify-end sm:space-x-3 sm:space-y-0 sm:space-x-reverse md:mt-0 md:flex-row md:space-x-3">
          <Link
            href="/"
            className="inline-flex items-center justify-center rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
          >
            {t('account.continueShopping')}
          </Link>
          <form action={logoutAction}>
            <button
              type="submit"
              className="inline-flex items-center justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 dark:bg-black dark:text-white dark:ring-neutral-800 dark:hover:bg-neutral-900"
            >
              {t('account.logout')}
            </button>
          </form>
        </div>
      </div>

      <div className="mt-8 overflow-hidden bg-white shadow sm:rounded-lg dark:bg-neutral-900 dark:ring-1 dark:ring-white/10">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-base font-semibold leading-6 text-gray-900 dark:text-white">{t('account.profileInfo')}</h3>
          <p className="mt-1 max-w-2xl text-sm text-gray-500 dark:text-gray-400">{t('account.personalDetails')}</p>
        </div>
        <div className="border-t border-gray-200 dark:border-white/10">
          <dl>
            <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6 dark:bg-neutral-900/50">
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">{t('account.fullName')}</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0 dark:text-white">{customer.first_name} {customer.last_name}</dd>
            </div>
            <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6 dark:bg-neutral-900">
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">{t('account.email')}</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0 dark:text-white">{customer.email}</dd>
            </div>
            <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6 dark:bg-neutral-900/50">
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">{t('account.customerId')}</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0 dark:text-white">{customer.id}</dd>
            </div>
          </dl>
        </div>
      </div>

      <div className="mt-8 overflow-hidden bg-white shadow sm:rounded-lg dark:bg-neutral-900 dark:ring-1 dark:ring-white/10">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-base font-semibold leading-6 text-gray-900 dark:text-white">{t('account.addresses')}</h3>
        </div>
        <div className="border-t border-gray-200 px-4 py-5 sm:px-6 dark:border-white/10">
          {customer.addresses?.length > 0 ? (
            customer.addresses.map((addr: any) => (
              <div key={addr.id} className="mb-4 p-4 border rounded dark:border-neutral-700">
                <p>{addr.first_name} {addr.last_name}</p>
                <p>{addr.address_1}</p>
                <p>{addr.city}, {addr.postal_code}</p>
                <p>{addr.country_code?.toUpperCase()}</p>
              </div>
            ))
          ) : (
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">{t('account.noAddresses')}</p>
          )}
          <AddressForm />
        </div>
      </div>
    </div>
  );
}

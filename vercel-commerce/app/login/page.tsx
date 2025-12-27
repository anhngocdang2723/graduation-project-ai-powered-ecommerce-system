'use client';

import { loginAction } from 'components/auth/actions';
import { useLanguage } from 'lib/i18n/context';
import Link from 'next/link';
import { useFormState } from 'react-dom';

export default function LoginPage() {
  const [state, formAction] = useFormState(loginAction, null);
  const { t } = useLanguage();

  return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100vh-200px)] py-12 px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-bold tracking-tight text-gray-900 dark:text-white">
            {t('auth.signInTitle')}
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
            {t('auth.or')}{' '}
            <Link href="/register" className="font-medium text-blue-600 hover:text-blue-500 dark:text-blue-400">
              {t('auth.createAccount')}
            </Link>
          </p>
        </div>
        <form className="mt-8 space-y-6" action={formAction}>
          <div className="-space-y-px rounded-md shadow-sm">
            <div>
              <label htmlFor="email-address" className="sr-only">
                {t('auth.email')}
              </label>
              <input
                id="email-address"
                name="email"
                type="email"
                autoComplete="email"
                required
                className="relative block w-full rounded-t-md border-0 py-1.5 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:z-10 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6 dark:bg-black dark:ring-neutral-800 dark:text-white px-3"
                placeholder={t('auth.email')}
              />
            </div>
            <div>
              <label htmlFor="password" className="sr-only">
                {t('auth.password')}
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                className="relative block w-full rounded-b-md border-0 py-1.5 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:z-10 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6 dark:bg-black dark:ring-neutral-800 dark:text-white px-3"
                placeholder={t('auth.password')}
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              className="group relative flex w-full justify-center rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 dark:bg-white dark:text-black dark:hover:bg-neutral-200"
            >
              {t('auth.signInButton')}
            </button>
          </div>
          {state?.error && (
            <div className="text-red-500 text-sm text-center">{state.error}</div>
          )}
        </form>
      </div>
    </div>
  );
}

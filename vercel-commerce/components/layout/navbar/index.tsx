
import Cart from 'components/cart';
import OpenCart from 'components/cart/open-cart';
import { getCategories, getMenu } from 'lib/medusa';
import { Menu } from 'lib/medusa/types';
import Link from 'next/link';
import { Suspense } from 'react';
import { HeartIcon } from '@heroicons/react/24/outline';
import AccountLink from './account-link';
import CategoryNav from './category-nav';
import HomeLink from './home-link';
import LanguageToggle from './language-toggle';
import MobileMenu from './mobile-menu';
import RegionSwitcher from './region-switcher';
import Search from './search';
import ThemeToggle from './theme-toggle';
const { SITE_NAME } = process.env;

export default async function Navbar() {
  const menu = await getMenu('next-js-frontend-header-menu');
  const categories = await getCategories();

  return (
    <>
      <nav className="relative flex items-center justify-between p-4 lg:px-6">
        <div className="block flex-none md:hidden">
          <MobileMenu menu={menu} />
        </div>
        <div className="flex w-full items-center">
          <div className="flex w-full md:w-1/3">
            <HomeLink siteName={SITE_NAME || ''} />
            {menu.length ? (
              <ul className="hidden gap-6 text-sm md:flex md:items-center">
                {menu.map((item: Menu) => (
                  <li key={item.title}>
                    <Link
                      href={item.path}
                      className="text-neutral-500 underline-offset-4 hover:text-black hover:underline dark:text-neutral-400 dark:hover:text-neutral-300"
                    >
                      {item.title}
                    </Link>
                  </li>
                ))}
                <li>
                  <Link
                    href="/collections"
                    className="text-neutral-500 underline-offset-4 hover:text-black hover:underline dark:text-neutral-400 dark:hover:text-neutral-300"
                  >
                    Collections
                  </Link>
                </li>
              </ul>
            ) : null}
          </div>
          <div className="hidden justify-center md:flex md:w-1/3">
            <Search categories={categories} />
          </div>
          <div className="flex justify-end md:w-1/3 gap-4 items-center">
            <RegionSwitcher />
            <LanguageToggle />
            <ThemeToggle />
            <Link
              href="/wishlist"
              className="transition hover:opacity-70"
              aria-label="Wishlist"
            >
              <HeartIcon className="h-6 w-6" />
            </Link>
            <AccountLink />
            <Suspense fallback={<OpenCart />}>
              <Cart />
            </Suspense>
          </div>
        </div>
      </nav>
      <Suspense fallback={<div className="h-12" />}>
        <CategoryNav />
      </Suspense>
    </>
  );
}

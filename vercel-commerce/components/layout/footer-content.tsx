'use client';

import MedusaIcon from 'components/icons/medusa';
import FooterMenu from 'components/layout/footer-menu';
import LogoSquare from 'components/logo-square';
import { useLanguage } from 'lib/i18n/context';
import { Menu } from 'lib/medusa/types';
import Link from 'next/link';
import { Suspense } from 'react';

export default function FooterContent({
  menu,
  copyrightDate,
  copyrightName,
  siteName
}: {
  menu: Menu[];
  copyrightDate: string;
  copyrightName: string;
  siteName: string;
}) {
  const { t } = useLanguage();
  const skeleton = 'w-full h-6 animate-pulse rounded bg-neutral-200 dark:bg-neutral-700';

  return (
    <footer className="text-sm text-neutral-500 dark:text-neutral-400">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-6 border-t border-neutral-200 px-6 py-12 text-sm dark:border-neutral-700 md:flex-row md:gap-12 md:px-4 xl:px-0">
        <div>
          <Link className="flex items-center gap-2 text-black dark:text-white md:pt-1" href="/">
            <LogoSquare size="sm" />
            <span className="uppercase">{siteName}</span>
          </Link>
        </div>
        <Suspense
          fallback={
            <div className="flex h-[188px] w-[200px] flex-col gap-2">
              <div className={skeleton} />
              <div className={skeleton} />
              <div className={skeleton} />
              <div className={skeleton} />
              <div className={skeleton} />
              <div className={skeleton} />
            </div>
          }
        >
          <FooterMenu menu={menu} />
        </Suspense>
        <div className="md:ml-auto">
          <a
            className="flex h-8 flex-none items-center justify-center rounded-md border border-neutral-200 bg-white text-xs text-black dark:border-neutral-700 dark:bg-black dark:text-white"
            aria-label="Deploy on Vercel"
            href="https://vercel.com/templates/next.js/nextjs-commerce"
          >
            <span className="px-3">▲</span>
            <hr className="h-full border-r border-neutral-200 dark:border-neutral-700" />
            <span className="px-3">{t('footer.deploy')}</span>
          </a>
        </div>
      </div>
      <div className="border-t border-neutral-200 py-6 text-sm dark:border-neutral-700">
        <div className="mx-auto flex w-full max-w-7xl flex-col items-center gap-1 px-4 md:flex-row md:gap-0 md:px-4 xl:px-0">
          <p>
            &copy; {copyrightDate} {copyrightName}
            {copyrightName.length && !copyrightName.endsWith('.') ? '.' : ''} {t('footer.rightsReserved')}
          </p>
          <hr className="mx-4 hidden h-4 w-[1px] border-l border-neutral-400 md:inline-block" />
          <p>{t('footer.designedIn')}</p>
          <p className="md:ml-auto">
            {t('footer.craftedBy')}{' '}
            <a
              rel="noopener noreferrer"
              href="https://medusajs.com"
              aria-label="Vmedusajs.com Link"
              target="_blank"
              className="text-black dark:text-white"
            >
              <MedusaIcon className="ml-3 inline-block h-6" />
            </a>
          </p>
        </div>
      </div>
    </footer>
  );
}

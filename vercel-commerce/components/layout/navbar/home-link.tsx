'use client';

import LogoSquare from 'components/logo-square';
import { useLanguage } from 'lib/i18n/context';
import Link from 'next/link';

export default function HomeLink({ siteName }: { siteName: string }) {
  const { t } = useLanguage();

  return (
    <Link
      href="/"
      aria-label={t('nav.goHome')}
      className="mr-2 flex w-full items-center justify-center md:w-auto lg:mr-6"
    >
      <LogoSquare />
      <div className="ml-2 flex-none text-sm font-medium uppercase md:hidden lg:block">
        {siteName}
      </div>
    </Link>
  );
}

'use client';

import UserIcon from 'components/icons/user';
import { useLanguage } from 'lib/i18n/context';
import Link from 'next/link';

export default function AccountLink() {
  const { t } = useLanguage();

  return (
    <Link href="/account" aria-label={t('nav.account')} className="flex items-center">
      <UserIcon className="h-6 w-6" />
    </Link>
  );
}

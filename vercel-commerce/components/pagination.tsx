'use client';

import Link from 'next/link';
import { usePathname, useSearchParams } from 'next/navigation';
import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/24/outline';
import { useLanguage } from 'lib/i18n/context';

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  baseUrl?: string;
}

export function Pagination({ currentPage, totalPages, baseUrl }: PaginationProps) {
  const { t } = useLanguage();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const createPageUrl = (page: number) => {
    const params = new URLSearchParams(searchParams);
    params.set('page', page.toString());
    const url = baseUrl || pathname;
    return `${url}?${params.toString()}`;
  };

  const getPageNumbers = () => {
    const pages: (number | string)[] = [];
    const maxVisible = 7;

    if (totalPages <= maxVisible) {
      // Show all pages if total is small
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      // Always show first page
      pages.push(1);

      if (currentPage > 3) {
        pages.push('...');
      }

      // Show pages around current page
      const start = Math.max(2, currentPage - 1);
      const end = Math.min(totalPages - 1, currentPage + 1);

      for (let i = start; i <= end; i++) {
        pages.push(i);
      }

      if (currentPage < totalPages - 2) {
        pages.push('...');
      }

      // Always show last page
      pages.push(totalPages);
    }

    return pages;
  };

  if (totalPages <= 1) return null;

  const pages = getPageNumbers();

  return (
    <nav className="flex flex-col items-center gap-4 py-8 sm:flex-row sm:justify-between" aria-label="Pagination">
      <div className="text-sm text-neutral-600 dark:text-neutral-400">
        Showing page <span className="font-semibold">{currentPage}</span> of{' '}
        <span className="font-semibold">{totalPages}</span>
      </div>

      <div className="flex items-center gap-2">
        {/* Previous Button */}
        {currentPage > 1 ? (
          <Link
            href={createPageUrl(currentPage - 1)}
            className="flex h-10 items-center gap-2 rounded-lg border border-neutral-300 px-4 transition hover:bg-neutral-100 dark:border-neutral-700 dark:hover:bg-neutral-900"
            aria-label="Previous page"
          >
            <ChevronLeftIcon className="h-4 w-4" />
            <span className="hidden sm:inline">{t('pagination.previous')}</span>
          </Link>
        ) : (
          <div className="flex h-10 items-center gap-2 rounded-lg border border-neutral-200 px-4 text-neutral-400 dark:border-neutral-800">
            <ChevronLeftIcon className="h-4 w-4" />
            <span className="hidden sm:inline">{t('pagination.previous')}</span>
          </div>
        )}

        {/* Page Numbers */}
        <div className="flex items-center gap-1">
          {pages.map((page, index) => {
            if (page === '...') {
              return (
                <span
                  key={`ellipsis-${index}`}
                  className="flex h-10 w-10 items-center justify-center text-neutral-600 dark:text-neutral-400"
                >
                  ...
                </span>
              );
            }

            const pageNumber = page as number;
            const isActive = pageNumber === currentPage;

            return (
              <Link
                key={pageNumber}
                href={createPageUrl(pageNumber)}
                className={`flex h-10 w-10 items-center justify-center rounded-lg font-semibold transition ${
                  isActive
                    ? 'bg-blue-600 text-white shadow-lg'
                    : 'border border-neutral-300 hover:bg-neutral-100 dark:border-neutral-700 dark:hover:bg-neutral-900'
                }`}
                aria-label={`Page ${pageNumber}`}
                aria-current={isActive ? 'page' : undefined}
              >
                {pageNumber}
              </Link>
            );
          })}
        </div>

        {/* Next Button */}
        {currentPage < totalPages ? (
          <Link
            href={createPageUrl(currentPage + 1)}
            className="flex h-10 items-center gap-2 rounded-lg border border-neutral-300 px-4 transition hover:bg-neutral-100 dark:border-neutral-700 dark:hover:bg-neutral-900"
            aria-label="Next page"
          >
            <span className="hidden sm:inline">{t('pagination.next')}</span>
            <ChevronRightIcon className="h-4 w-4" />
          </Link>
        ) : (
          <div className="flex h-10 items-center gap-2 rounded-lg border border-neutral-200 px-4 text-neutral-400 dark:border-neutral-800">
            <span className="hidden sm:inline">{t('pagination.next')}</span>
            <ChevronRightIcon className="h-4 w-4" />
          </div>
        )}
      </div>
    </nav>
  );
}

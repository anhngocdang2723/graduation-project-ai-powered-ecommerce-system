'use client';

import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import { useLanguage } from 'lib/i18n/context';
import { createUrl } from 'lib/utils';
import { useRouter, useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';

interface SearchProps {
  categories?: Array<{ id: string; title: string; handle: string }>;
}

export default function Search({ categories = [] }: SearchProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [searchValue, setSearchValue] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const { t } = useLanguage();

  useEffect(() => {
    setSearchValue(searchParams?.get('q') || '');
  }, [searchParams, setSearchValue]);

  function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();

    const val = e.target as HTMLFormElement;
    const search = val.search as HTMLInputElement;
    const newParams = new URLSearchParams(searchParams.toString());

    if (search.value) {
      newParams.set('q', search.value);
    } else {
      newParams.delete('q');
    }

    // Navigate to category page or general search
    if (selectedCategory !== 'all') {
      router.push(createUrl(`/categories/${selectedCategory}`, newParams));
    } else {
      router.push(createUrl('/search', newParams));
    }
  }

  return (
    <form onSubmit={onSubmit} className="relative flex w-full max-w-[550px] lg:w-80 xl:w-full">
      {categories.length > 0 && (
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="rounded-l-lg border border-r-0 bg-neutral-100 px-3 py-2 text-sm text-black dark:border-neutral-800 dark:bg-neutral-900 dark:text-white"
        >
          <option value="all">All</option>
          {categories.slice(0, 10).map((cat) => (
            <option key={cat.id} value={cat.handle}>
              {cat.title}
            </option>
          ))}
        </select>
      )}
      <div className="relative flex-1">
        <input
          type="text"
          name="search"
          placeholder={t('nav.search')}
          autoComplete="off"
          value={searchValue}
          onChange={(e) => setSearchValue(e.target.value)}
          className={`w-full border bg-white px-4 py-2 text-sm text-black placeholder:text-neutral-500 dark:border-neutral-800 dark:bg-transparent dark:text-white dark:placeholder:text-neutral-400 ${
            categories.length > 0 ? 'rounded-r-lg' : 'rounded-lg'
          }`}
        />
        <button
          type="submit"
          className="absolute right-0 top-0 mr-3 flex h-full items-center"
          aria-label="Search"
        >
          <MagnifyingGlassIcon className="h-4" />
        </button>
      </div>
    </form>
  );
}

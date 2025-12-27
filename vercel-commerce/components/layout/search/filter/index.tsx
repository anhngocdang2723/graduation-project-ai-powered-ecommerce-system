'use client';

import { SortFilterItem } from 'lib/constants';
import FilterItemDropdown from './dropdown';
import { FilterItem } from './item';
import { useLanguage } from 'lib/i18n/context';

export type ListItem = SortFilterItem | PathFilterItem;
export type PathFilterItem = { title: string; path: string };

function FilterItemList({ list }: { list: ListItem[] }) {
  return (
    <>
      {list.map((item: ListItem, i) => (
        <FilterItem key={i} item={item} />
      ))}
    </>
  );
}

export default function FilterList({ list, title }: { list: ListItem[]; title?: string }) {
  const { t } = useLanguage();
  const translatedTitle = title === 'Sort by' ? t('sort.sortBy') : title;

  return (
    <>
      <nav>
        {title ? <h3 className="hidden text-xs text-neutral-500 md:block">{translatedTitle}</h3> : null}
        <ul className="hidden md:block">
          <FilterItemList list={list} />
        </ul>
        <ul className="md:hidden">
          <FilterItemDropdown list={list} />
        </ul>
      </nav>
    </>
  );
}

import { getCategories } from 'lib/medusa';
import Link from 'next/link';

export default async function CategoryNav() {
  const categories = await getCategories();
  
  // Show top 10 categories in nav
  const topCategories = categories.slice(0, 10);

  if (!topCategories.length) return null;

  return (
    <div className="border-b border-neutral-200 bg-white dark:border-neutral-800 dark:bg-neutral-900">
      <div className="mx-auto max-w-screen-2xl px-4">
        <div className="flex gap-6 overflow-x-auto py-3 scrollbar-hide">
          <Link
            href="/search"
            className="whitespace-nowrap text-sm font-medium text-neutral-700 hover:text-blue-600 dark:text-neutral-300 dark:hover:text-blue-500"
          >
            All Products
          </Link>
          {topCategories.map((category) => (
            <Link
              key={category.id}
              href={category.path}
              className="whitespace-nowrap text-sm font-medium text-neutral-700 hover:text-blue-600 dark:text-neutral-300 dark:hover:text-blue-500"
            >
              {category.title}
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}

import { getCategories } from 'lib/medusa';
import Link from 'next/link';
import { Suspense } from 'react';

export const metadata = {
  title: 'Categories',
  description: 'Browse products by category'
};

export const runtime = 'edge';

function CategoryCard({ category }: { category: any }) {
  return (
    <Link
      href={category.path}
      className="group relative overflow-hidden rounded-lg border border-neutral-200 transition hover:shadow-lg dark:border-neutral-800"
    >
      <div className="aspect-square bg-gradient-to-br from-blue-500 to-purple-600 p-6 transition group-hover:scale-105">
        <div className="flex h-full flex-col justify-end">
          <h3 className="text-xl font-bold text-white">{category.title}</h3>
          {category.description && (
            <p className="mt-1 text-sm text-white/80">{category.description}</p>
          )}
          <p className="mt-1 text-sm text-white/80">
            Xem thêm →
          </p>
        </div>
      </div>
    </Link>
  );
}

async function Categories() {
  const categories = await getCategories();

  return (
    <div className="mx-auto max-w-screen-2xl px-4 py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Danh mục sản phẩm</h1>
        <p className="mt-2 text-neutral-600 dark:text-neutral-400">
          Tìm sản phẩm theo danh mục
        </p>
      </div>

      {categories.length === 0 ? (
        <p className="py-12 text-center text-lg text-neutral-500">
          No categories found.
        </p>
      ) : (
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          {categories.map((category) => (
            <CategoryCard key={category.id} category={category} />
          ))}
        </div>
      )}
    </div>
  );
}

export default function CategoriesPage() {
  return (
    <Suspense
      fallback={
        <div className="mx-auto max-w-screen-2xl px-4 py-12">
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            {[...Array(4)].map((_, i) => (
              <div
                key={i}
                className="aspect-square animate-pulse rounded-lg bg-neutral-200 dark:bg-neutral-800"
              />
            ))}
          </div>
        </div>
      }
    >
      <Categories />
    </Suspense>
  );
}

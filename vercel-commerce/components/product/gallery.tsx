'use client';

import { ArrowLeftIcon, ArrowRightIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import { GridTileImage } from 'components/grid/tile';
import { useLanguage } from 'lib/i18n/context';
import { createUrl } from 'lib/utils';
import Image from 'next/image';
import Link from 'next/link';
import { usePathname, useSearchParams } from 'next/navigation';
import { useState } from 'react';
import { ImageZoom } from './image-zoom';

export function Gallery({ images }: { images: { src: string; altText: string }[] }) {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const imageSearchParam = searchParams.get('image');
  const imageIndex = imageSearchParam ? parseInt(imageSearchParam) : 0;
  const { t } = useLanguage();
  const [showZoom, setShowZoom] = useState(false);

  const nextSearchParams = new URLSearchParams(searchParams.toString());
  const nextImageIndex = imageIndex + 1 < images.length ? imageIndex + 1 : 0;
  nextSearchParams.set('image', nextImageIndex.toString());
  const nextUrl = createUrl(pathname, nextSearchParams);

  const previousSearchParams = new URLSearchParams(searchParams.toString());
  const previousImageIndex = imageIndex === 0 ? images.length - 1 : imageIndex - 1;
  previousSearchParams.set('image', previousImageIndex.toString());
  const previousUrl = createUrl(pathname, previousSearchParams);

  const buttonClassName =
    'h-full px-6 transition-all ease-in-out hover:scale-110 hover:text-black dark:hover:text-white flex items-center justify-center';

  return (
    <>
      <div className="relative aspect-square h-full max-h-[550px] w-full overflow-hidden">
        {images[imageIndex] && (
          <>
            <Image
              className="h-full w-full object-contain"
              fill
              sizes="(min-width: 1024px) 66vw, 100vw"
              alt={images[imageIndex]?.altText as string}
              src={images[imageIndex]?.src as string}
              priority={true}
            />
            <button
              onClick={() => setShowZoom(true)}
              className="absolute right-4 top-4 rounded-full bg-white/80 p-3 shadow-lg backdrop-blur-sm transition hover:bg-white dark:bg-black/80 dark:hover:bg-black"
              aria-label="Zoom image"
            >
              <MagnifyingGlassIcon className="h-5 w-5" />
            </button>
          </>
        )}

        {images.length > 1 ? (
          <div className="absolute bottom-[15%] flex w-full justify-center">
            <div className="mx-auto flex h-11 items-center rounded-full border border-white bg-neutral-50/80 text-neutral-500 backdrop-blur dark:border-black dark:bg-neutral-900/80">
              <Link
                aria-label={t('product.previousImage')}
                href={previousUrl}
                className={buttonClassName}
                scroll={false}
              >
                <ArrowLeftIcon className="h-5" />
              </Link>
              <div className="mx-1 h-6 w-px bg-neutral-500"></div>
              <Link
                aria-label={t('product.nextImage')}
                href={nextUrl}
                className={buttonClassName}
                scroll={false}
              >
                <ArrowRightIcon className="h-5" />
              </Link>
            </div>
          </div>
        ) : null}
      </div>

      {images.length > 1 ? (
        <ul className="my-12 flex items-center justify-center gap-2 overflow-auto py-1 lg:mb-0">
          {images.map((image, index) => {
            const isActive = index === imageIndex;
            const imageSearchParams = new URLSearchParams(searchParams.toString());

            imageSearchParams.set('image', index.toString());

            return (
              <li key={image.src} className="h-auto w-20">
                <Link
                  aria-label="Enlarge product image"
                  href={createUrl(pathname, imageSearchParams)}
                  scroll={false}
                  className="h-full w-full"
                >
                  <GridTileImage
                    alt={image.altText}
                    src={image.src}
                    width={80}
                    height={80}
                    active={isActive}
                  />
                </Link>
              </li>
            );
          })}
        </ul>
      ) : null}
      
      {showZoom && images[imageIndex] && (
        <ImageZoom
          src={images[imageIndex]!.src}
          alt={images[imageIndex]!.altText}
          onClose={() => setShowZoom(false)}
        />
      )}
    </>
  );
}

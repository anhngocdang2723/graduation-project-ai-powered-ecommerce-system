'use client';

import { useState } from 'react';
import Image from 'next/image';
import { XMarkIcon, MagnifyingGlassMinusIcon, MagnifyingGlassPlusIcon } from '@heroicons/react/24/outline';

interface ImageZoomProps {
  src: string;
  alt: string;
  onClose: () => void;
}

export function ImageZoom({ src, alt, onClose }: ImageZoomProps) {
  const [zoom, setZoom] = useState(1);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  const handleZoomIn = () => {
    setZoom((prev) => Math.min(prev + 0.5, 3));
  };

  const handleZoomOut = () => {
    setZoom((prev) => Math.max(prev - 0.5, 1));
    if (zoom <= 1.5) {
      setPosition({ x: 0, y: 0 });
    }
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if (zoom > 1) {
      setIsDragging(true);
      setDragStart({
        x: e.clientX - position.x,
        y: e.clientY - position.y
      });
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging && zoom > 1) {
      setPosition({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y
      });
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 p-4"
      onClick={onClose}
    >
      <button
        onClick={onClose}
        className="absolute right-4 top-4 rounded-full bg-white/10 p-2 backdrop-blur-sm transition hover:bg-white/20"
        aria-label="Close zoom"
      >
        <XMarkIcon className="h-6 w-6 text-white" />
      </button>

      <div className="absolute bottom-4 left-1/2 flex -translate-x-1/2 gap-2 rounded-full bg-white/10 p-2 backdrop-blur-sm">
        <button
          onClick={(e) => {
            e.stopPropagation();
            handleZoomOut();
          }}
          className="rounded-full p-2 transition hover:bg-white/20"
          aria-label="Zoom out"
        >
          <MagnifyingGlassMinusIcon className="h-5 w-5 text-white" />
        </button>
        <span className="flex items-center px-3 text-sm font-semibold text-white">
          {Math.round(zoom * 100)}%
        </span>
        <button
          onClick={(e) => {
            e.stopPropagation();
            handleZoomIn();
          }}
          className="rounded-full p-2 transition hover:bg-white/20"
          aria-label="Zoom in"
        >
          <MagnifyingGlassPlusIcon className="h-5 w-5 text-white" />
        </button>
      </div>

      <div
        className="relative max-h-[90vh] max-w-[90vw] overflow-hidden"
        onClick={(e) => e.stopPropagation()}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        style={{ cursor: zoom > 1 ? (isDragging ? 'grabbing' : 'grab') : 'zoom-in' }}
      >
        <div
          style={{
            transform: `scale(${zoom}) translate(${position.x / zoom}px, ${position.y / zoom}px)`,
            transition: isDragging ? 'none' : 'transform 0.3s ease'
          }}
        >
          <Image
            src={src}
            alt={alt}
            width={1200}
            height={1200}
            className="h-auto w-auto max-h-[90vh] max-w-[90vw] object-contain"
            priority
          />
        </div>
      </div>
    </div>
  );
}

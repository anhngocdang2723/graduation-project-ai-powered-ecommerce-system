'use client';

import { usePathname, useRouter, useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';

export default function RegionSwitcher() {
  const [regions, setRegions] = useState<any[]>([]);
  const [currentRegion, setCurrentRegion] = useState<string>('');
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  useEffect(() => {
    // Fetch regions
    fetch('/api/regions')
      .then((res) => res.json())
      .then((data) => {
        const fetchedRegions = data.regions || [];
        setRegions(fetchedRegions);
        // Try to get current region from cookie or default
        const match = document.cookie.match(new RegExp('(^| )_medusa_region_id=([^;]+)'));
        if (match && match[2]) {
          setCurrentRegion(match[2]);
        } else if (fetchedRegions.length > 0) {
          setCurrentRegion(fetchedRegions[0].id);
        }
      })
      .catch((err) => {
        console.error('Failed to fetch regions:', err);
        setRegions([]);
      });
  }, []);

  const handleRegionChange = (regionId: string) => {
    setCurrentRegion(regionId);
    // Set cookie
    document.cookie = `_medusa_region_id=${regionId}; path=/; max-age=31536000`; // 1 year
    
    // Refresh page to apply changes
    router.refresh();
  };

  if (!regions || regions.length === 0) return null;

  return (
    <select
      value={currentRegion}
      onChange={(e) => handleRegionChange(e.target.value)}
      className="bg-transparent text-sm font-medium text-neutral-500 hover:text-black dark:text-neutral-400 dark:hover:text-neutral-300 border-none focus:ring-0 cursor-pointer"
    >
      {regions.map((region) => (
        <option key={region.id} value={region.id}>
          {region.name} ({region.currency_code.toUpperCase()})
        </option>
      ))}
    </select>
  );
}

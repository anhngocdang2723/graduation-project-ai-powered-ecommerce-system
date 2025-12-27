'use client';

export type InteractionType = 'view' | 'add_to_cart' | 'wishlist' | 'purchase' | 'search';

export interface UserInteraction {
  productId?: string;
  productHandle?: string;
  interactionType: InteractionType;
  timestamp: number;
  sessionId: string;
  metadata?: Record<string, any>;
}

// Get or create session ID
export function getSessionId(): string {
  if (typeof window === 'undefined') return '';
  
  let sessionId = sessionStorage.getItem('session_id');
  if (!sessionId) {
    sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    sessionStorage.setItem('session_id', sessionId);
  }
  return sessionId;
}

// Get user ID (from localStorage or cookie)
export function getUserId(): string {
  if (typeof window === 'undefined') return '';
  
  let userId = localStorage.getItem('user_id');
  if (!userId) {
    userId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('user_id', userId);
  }
  return userId;
}

// Track interaction locally
export function trackInteraction(interaction: Omit<UserInteraction, 'timestamp' | 'sessionId'>) {
  if (typeof window === 'undefined') return;
  
  const fullInteraction: UserInteraction = {
    ...interaction,
    timestamp: Date.now(),
    sessionId: getSessionId(),
  };

  // DEDUPLICATION: Check if same interaction exists in last 5 seconds
  const interactions = getStoredInteractions();
  const recentSimilar = interactions.find(existing => 
    existing.productId === fullInteraction.productId &&
    existing.interactionType === fullInteraction.interactionType &&
    Math.abs(existing.timestamp - fullInteraction.timestamp) < 5000 // 5 seconds
  );

  if (recentSimilar) {
    console.log('[Tracking] Duplicate interaction prevented:', fullInteraction);
    return;
  }

  // Store in localStorage
  interactions.push(fullInteraction);
  
  // Keep only last 100 interactions
  const recentInteractions = interactions.slice(-100);
  localStorage.setItem('user_interactions', JSON.stringify(recentInteractions));

  console.log('[Tracking] New interaction:', fullInteraction);

  // Send to backend (async, don't wait)
  sendToBackend(fullInteraction).catch(console.error);
}

// Get stored interactions
export function getStoredInteractions(): UserInteraction[] {
  if (typeof window === 'undefined') return [];
  
  try {
    const data = localStorage.getItem('user_interactions');
    return data ? JSON.parse(data) : [];
  } catch {
    return [];
  }
}

// Send interaction to backend
async function sendToBackend(interaction: UserInteraction) {
  try {
    const userId = getUserId();
    await fetch('/api/recommendations/track', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        userId,
        ...interaction,
      }),
    });
  } catch (error) {
    console.error('Failed to track interaction:', error);
  }
}

// Get user's viewed categories
export function getViewedCategories(): Map<string, number> {
  const interactions = getStoredInteractions();
  const categoryViews = new Map<string, number>();

  interactions
    .filter(i => i.interactionType === 'view' && i.metadata?.category)
    .forEach(i => {
      const category = i.metadata!.category;
      categoryViews.set(category, (categoryViews.get(category) || 0) + 1);
    });

  return categoryViews;
}

// Get recently viewed products
export function getRecentlyViewed(limit: number = 10): string[] {
  const interactions = getStoredInteractions();
  const productIds = interactions
    .filter(i => i.interactionType === 'view' && i.productHandle)
    .reverse()
    .map(i => i.productHandle!)
    .filter((handle, index, self) => self.indexOf(handle) === index) // unique
    .slice(0, limit);

  return productIds;
}

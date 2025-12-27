'use client';

import StarRating from './star-rating';
import { useState } from 'react';
import { useLanguage } from 'lib/i18n/context';

interface Review {
  id: string;
  author: string;
  rating: number;
  comment: string;
  date: string;
  verified?: boolean;
}

interface ProductReviewsProps {
  productId: string;
  reviews?: Review[];
  averageRating?: number;
  totalReviews?: number;
}

export default function ProductReviews({
  productId,
  reviews = [],
  averageRating = 0,
  totalReviews = 0
}: ProductReviewsProps) {
  const { t } = useLanguage();
  const [showReviewForm, setShowReviewForm] = useState(false);
  const [newRating, setNewRating] = useState(5);
  const [newComment, setNewComment] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmitReview = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      // TODO: Implement API call to submit review
      const response = await fetch('/api/reviews', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          productId,
          rating: newRating,
          comment: newComment
        })
      });

      if (response.ok) {
        setNewComment('');
        setNewRating(5);
        setShowReviewForm(false);
        // TODO: Refresh reviews list
      }
    } catch (error) {
      console.error('Failed to submit review:', error);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="mt-8">
      <h2 className="mb-4 text-2xl font-bold">Customer Reviews</h2>
      
      {/* Overall Rating Summary */}
      <div className="mb-6 flex items-center gap-4 rounded-lg border border-neutral-200 p-4 dark:border-neutral-800">
        <div className="text-center">
          <div className="text-4xl font-bold">{averageRating.toFixed(1)}</div>
          <StarRating rating={averageRating} size="sm" />
          <div className="mt-1 text-sm text-gray-600 dark:text-gray-400">
            {totalReviews} {totalReviews === 1 ? 'review' : 'reviews'}
          </div>
        </div>
        <div className="flex-1">
          <button
            onClick={() => setShowReviewForm(!showReviewForm)}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            Write a Review
          </button>
        </div>
      </div>

      {/* Review Form */}
      {showReviewForm && (
        <form onSubmit={handleSubmitReview} className="mb-6 rounded-lg border border-neutral-200 p-4 dark:border-neutral-800">
          <h3 className="mb-3 font-semibold">Write Your Review</h3>
          <div className="mb-3">
            <label className="mb-2 block text-sm font-medium">Rating</label>
            <StarRating
              rating={newRating}
              interactive
              onRate={setNewRating}
              size="lg"
            />
          </div>
          <div className="mb-3">
            <label className="mb-2 block text-sm font-medium">Comment</label>
            <textarea
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              required
              rows={4}
              className="w-full rounded-lg border border-neutral-300 p-3 dark:border-neutral-700 dark:bg-black"
              placeholder="Share your experience with this product..."
            />
          </div>
          <div className="flex gap-2">
            <button
              type="submit"
              disabled={submitting}
              className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {submitting ? 'Submitting...' : 'Submit Review'}
            </button>
            <button
              type="button"
              onClick={() => setShowReviewForm(false)}
              className="rounded-lg border border-neutral-300 px-4 py-2 text-sm font-medium hover:bg-neutral-100 dark:border-neutral-700 dark:hover:bg-neutral-900"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {/* Reviews List */}
      <div className="space-y-4">
        {reviews.length === 0 ? (
          <p className="text-gray-600 dark:text-gray-400">No reviews yet. Be the first to review this product!</p>
        ) : (
          reviews.map((review) => (
            <div
              key={review.id}
              className="rounded-lg border border-neutral-200 p-4 dark:border-neutral-800"
            >
              <div className="mb-2 flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-semibold">{review.author}</span>
                    {review.verified && (
                      <span className="rounded bg-green-100 px-2 py-0.5 text-xs font-medium text-green-800 dark:bg-green-900 dark:text-green-200">
                        Verified Purchase
                      </span>
                    )}
                  </div>
                  <StarRating rating={review.rating} size="sm" />
                </div>
                <span className="text-sm text-gray-500">
                  {new Date(review.date).toLocaleDateString()}
                </span>
              </div>
              <p className="text-gray-700 dark:text-gray-300">{review.comment}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

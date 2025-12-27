import { StarIcon } from '@heroicons/react/24/solid';
import { StarIcon as StarOutlineIcon } from '@heroicons/react/24/outline';

interface StarRatingProps {
  rating: number;
  maxRating?: number;
  size?: 'sm' | 'md' | 'lg';
  showNumber?: boolean;
  interactive?: boolean;
  onRate?: (rating: number) => void;
}

export default function StarRating({
  rating,
  maxRating = 5,
  size = 'md',
  showNumber = false,
  interactive = false,
  onRate
}: StarRatingProps) {
  const sizeClasses = {
    sm: 'h-3 w-3',
    md: 'h-4 w-4',
    lg: 'h-5 w-5'
  };

  const stars = Array.from({ length: maxRating }, (_, i) => i + 1);

  return (
    <div className="flex items-center gap-1">
      {stars.map((star) => {
        const isFilled = star <= Math.round(rating);
        const StarComponent = isFilled ? StarIcon : StarOutlineIcon;
        
        return (
          <button
            key={star}
            type="button"
            disabled={!interactive}
            onClick={() => interactive && onRate?.(star)}
            className={`${interactive ? 'cursor-pointer hover:scale-110 transition-transform' : 'cursor-default'}`}
          >
            <StarComponent
              className={`${sizeClasses[size]} ${
                isFilled ? 'text-yellow-400' : 'text-gray-300 dark:text-gray-600'
              }`}
            />
          </button>
        );
      })}
      {showNumber && (
        <span className="ml-1 text-sm text-gray-600 dark:text-gray-400">
          {rating.toFixed(1)}
        </span>
      )}
    </div>
  );
}

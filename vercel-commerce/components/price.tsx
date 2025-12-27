import clsx from 'clsx';

type PriceProps = {
  amount: string;
  className?: string;
  currencyCode: string;
  currencyCodeClassName?: string;
} & React.ComponentProps<'p'>;

export default function Price({
  amount,
  className,
  currencyCode = 'USD',
  currencyCodeClassName,
  ...props
}: PriceProps) {
  // Check if amount is already formatted (contains currency symbols)
  const hasSymbol = amount.includes('₫') || amount.includes('$') || amount.includes('€');
  
  // Debug logging
  if (typeof window !== 'undefined' && amount === '0') {
    console.warn('[Price] Displaying 0 - amount:', amount, 'currencyCode:', currencyCode, 'hasSymbol:', hasSymbol);
  }
  
  if (hasSymbol) {
    // Already formatted - display as is
    return (
      <p suppressHydrationWarning={true} className={className} {...props}>
        {amount}
      </p>
    );
  }
  
  // Not formatted - apply Intl formatting
  return (
    <p suppressHydrationWarning={true} className={className} {...props}>
      {`${new Intl.NumberFormat(undefined, {
        style: 'currency',
        currency: currencyCode || 'USD',
        currencyDisplay: 'narrowSymbol'
      }).format(parseFloat(amount))}`}
      <span className={clsx('ml-1 inline', currencyCodeClassName)}>{`${currencyCode || 'USD'}`}</span>
    </p>
  );
}

import { isEmpty } from '../utils';
import { MedusaProductVariant, Money, RegionInfo } from './types';

type ComputeAmountParams = {
  amount: number;
  region: RegionInfo;
  includeTaxes?: boolean;
};

/**
 * Takes an amount, a region, and returns the amount as a decimal including or excluding taxes
 */
export const computeAmount = ({ amount, region, includeTaxes = true }: ComputeAmountParams) => {
  const toDecimal = convertToDecimal(amount, region.currency_code);

  const taxRate = includeTaxes ? getTaxRate(region) : 0;

  const amountWithTaxes = toDecimal * (1 + taxRate);

  return amountWithTaxes;
};

/**
 * Takes a product variant, and returns the amount as a decimal including or excluding taxes and the currency code
 */
export const calculateVariantAmount = (variant: MedusaProductVariant): Money => {
  if (!variant) {
    return {
      amount: '0',
      currencyCode: 'USD'
    };
  }

  if (variant.calculated_price) {
    return {
      amount: convertToDecimal(variant.calculated_price.calculated_amount, variant.calculated_price.currency_code).toString(),
      currencyCode: variant.calculated_price.currency_code.toUpperCase()
    };
  }

  const currencyCode = variant.prices?.[0]?.currency_code ?? 'USD';
  const amount = convertToDecimal(variant.prices?.[0]?.amount || 0, currencyCode).toString();
  return {
    amount,
    currencyCode
  };
};

// we should probably add a more extensive list
const noDivisionCurrencies = ['krw', 'jpy', 'vnd'];

export const convertToDecimal = (amount: number, currencyCode = 'USD') => {
  const divisor = noDivisionCurrencies.includes(currencyCode.toLowerCase()) ? 1 : 100;

  return Math.floor(amount || 0) / divisor;
};

const getTaxRate = (region?: RegionInfo) => {
  return region && !isEmpty(region) ? (region?.tax_rate || 0) / 100 : 0;
};

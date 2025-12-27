import { isMedusaError } from 'lib/type-guards';

import { TAGS } from 'lib/constants';
import { mapOptionIds } from 'lib/utils';
import { revalidateTag } from 'next/cache';
import { headers } from 'next/headers';
import { NextRequest, NextResponse } from 'next/server';
import { calculateVariantAmount, computeAmount, convertToDecimal } from './helpers';
import {
  Cart,
  CartItem,
  Image,
  MedusaCart,
  MedusaImage,
  MedusaLineItem,
  MedusaProduct,
  MedusaProductCollection,
  MedusaProductOption,
  MedusaProductVariant,
  Product,
  ProductCategory,
  ProductCollection,
  ProductOption,
  ProductVariant,
  SelectedOption
} from './types';

const ENDPOINT = process.env.NEXT_PUBLIC_MEDUSA_BACKEND_API ?? 'http://localhost:9000';
const MEDUSA_API_KEY = process.env.MEDUSA_API_KEY ?? '';

export default async function medusaRequest({
  cache = 'no-store',
  method,
  path,
  payload,
  tags
}: {
  cache?: RequestCache;
  method: string;
  path: string;
  payload?: Record<string, unknown> | undefined;
  tags?: string[];
}) {
  const options: RequestInit = {
    method,
    headers: {
      'Content-Type': 'application/json',
      'x-publishable-api-key': MEDUSA_API_KEY
    },
    cache,
    ...(tags && { next: { tags } })
  };

  if (path.includes('/carts')) {
    options.cache = 'no-cache';
  }

  if (payload) {
    options.body = JSON.stringify(payload);
  }

  try {
    const result = await fetch(`${ENDPOINT}/store${path}`, options);

    const body = await result.json();

    if (body.errors) {
      console.error(`[medusaRequest] API Error for ${method} ${path}:`, body.errors);
      throw body.errors[0];
    }

    if (!result.ok) {
      console.error(`[medusaRequest] HTTP ${result.status} for ${method} ${path}:`, body);
    }

    return {
      status: result.status,
      body
    };
  } catch (e) {
    console.error(`[medusaRequest] Exception for ${method} ${path}:`, e);
    if (isMedusaError(e)) {
      throw {
        status: e.status || 500,
        message: e.message
      };
    }

    throw {
      error: e
    };
  }
}

import { cookies } from 'next/headers';

let cachedRegionId: string | null = null;
let validRegionIds: Set<string> | null = null;

async function getValidRegions(): Promise<string[]> {
  try {
    const res = await medusaRequest({ method: 'GET', path: '/regions', tags: ['regions'] });
    if (res.body.regions && res.body.regions.length > 0) {
      return res.body.regions.map((r: any) => r.id);
    }
  } catch (e) {
    console.error('Failed to fetch regions', e);
  }
  return [];
}

async function getRegionId(): Promise<string> {
  // Fetch valid regions first
  if (!validRegionIds) {
    const regions = await getValidRegions();
    validRegionIds = new Set(regions);
  }

  // 1. Check cookie - but validate it still exists
  const regionCookie = cookies().get('_medusa_region_id');
  if (regionCookie?.value && validRegionIds.has(regionCookie.value)) {
    return regionCookie.value;
  }

  // 2. Check cache (fallback)
  if (cachedRegionId && validRegionIds.has(cachedRegionId)) {
    return cachedRegionId;
  }
  
  // 3. Get first valid region
  if (validRegionIds.size > 0) {
    cachedRegionId = Array.from(validRegionIds)[0] ?? null;
    return cachedRegionId ?? '';
  }
  
  // 4. If no valid regions found, try to fetch again (maybe first time failed?)
  try {
      const regions = await getValidRegions();
      if (regions.length > 0) {
          validRegionIds = new Set(regions);
          cachedRegionId = regions[0] ?? null;
          return cachedRegionId ?? '';
      }
  } catch (e) {
      console.error("Retry getValidRegions failed", e);
  }

  return '';
}

const reshapeCart = (cart: MedusaCart | undefined | null): Cart | null => {
  // Handle case where cart or region might be undefined
  if (!cart) {
    return null;
  }

  // Check if cart is completed
  if (cart.completed_at || cart.payment_authorized_at) {
    console.log(`[reshapeCart] Cart ${cart.id} is completed/paid. Returning null to force new cart creation.`);
    return null;
  }

  const currencyCode = cart.region?.currency_code?.toUpperCase() || 'USD';
  console.log(`[reshapeCart] Cart region currency: ${cart.region?.currency_code}, using: ${currencyCode}`);
  console.log(`[reshapeCart] Cart totals - subtotal: ${cart.subtotal}, total: ${cart.total}, tax_total: ${cart.tax_total}`);
  
  const lines = cart?.items?.map((item) => reshapeLineItem(item, currencyCode)) || [];
  const totalQuantity = lines.reduce((a, b) => a + b.quantity, 0);
  const checkoutUrl = '/checkout'; // todo: implement medusa checkout flow

  let subtotalAmount = '0';
  if (cart.subtotal !== undefined && cart.subtotal !== null) {
    subtotalAmount = cart.region 
      ? computeAmount({ amount: cart.subtotal, region: cart.region }).toString()
      : (cart.subtotal / 100).toString(); // Fallback: assume cents
  }

  let totalAmount = '0';
  if (cart.total !== undefined && cart.total !== null) {
    totalAmount = cart.region 
      ? computeAmount({ amount: cart.total, region: cart.region }).toString()
      : (cart.total / 100).toString();
  }

  let totalTaxAmount = '0';
  if (cart.tax_total !== undefined && cart.tax_total !== null) {
    totalTaxAmount = cart.region 
      ? computeAmount({ amount: cart.tax_total, region: cart.region }).toString()
      : (cart.tax_total / 100).toString();
  }

  const cost = {
    subtotalAmount: {
      amount: subtotalAmount,
      currencyCode: currencyCode
    },
    totalAmount: {
      amount: totalAmount,
      currencyCode: currencyCode
    },
    totalTaxAmount: {
      amount: totalTaxAmount,
      currencyCode: currencyCode
    }
  };

  return {
    ...cart,
    totalQuantity,
    checkoutUrl,
    lines,
    cost
  };
};

const reshapeLineItem = (lineItem: MedusaLineItem, currencyCode: string = 'USD'): CartItem => {
  // Debug logging
  console.log('Reshaping line item:', JSON.stringify(lineItem, null, 2));
  
  const product = {
    title: lineItem.title,
    priceRange: {
      maxVariantPrice: calculateVariantAmount(lineItem.variant)
    },
    updatedAt: lineItem.updated_at,
    createdAt: lineItem.created_at,
    tags: [],
    descriptionHtml: lineItem.description ?? '',
    featuredImage: {
      url: lineItem.thumbnail ?? '',
      altText: lineItem.title ?? ''
    },
    availableForSale: true,
    variants: [lineItem.variant && reshapeProductVariant(lineItem.variant)].filter(Boolean) as ProductVariant[],
    handle: lineItem.variant?.product?.handle ?? lineItem.product_handle ?? '',
    options: [] as ProductOption[]
  };

  const selectedOptions =
    lineItem.variant?.options?.map((option) => {
      // Try to find the option name from various sources
      let optionName = 'Option';
      
      // 1. Direct relation if expanded (Preferred)
      if (option.option?.title) {
        optionName = option.option.title;
      } 
      // 2. Look up in product options if available
      else if (lineItem.variant?.product?.options) {
        const productOption = lineItem.variant.product.options.find((o) => o && o.id === option.option_id);
        if (productOption?.title) {
          optionName = productOption.title;
        }
      }
      
      return {
        name: optionName,
        value: option.value
      };
    }) || [];

  const merchandise = {
    id: lineItem.variant_id || lineItem.id,
    selectedOptions,
    product,
    title: lineItem.description ?? ''
  };

  console.log(`[reshapeLineItem] Line item totals - total: ${lineItem.total}, subtotal: ${lineItem.subtotal}, unit_price: ${lineItem.unit_price}, quantity: ${lineItem.quantity}, currencyCode: ${currencyCode}`);
  
  const rawAmount = lineItem.total || lineItem.subtotal || (lineItem.unit_price * lineItem.quantity);
  const convertedAmount = convertToDecimal(rawAmount, currencyCode);
  
  console.log(`[reshapeLineItem] Raw amount: ${rawAmount}, Converted: ${convertedAmount}, Currency: ${currencyCode}`);

  const cost = {
    totalAmount: {
      amount: convertedAmount.toString(),
      currencyCode: currencyCode
    }
  };
  const quantity = lineItem.quantity;

  return {
    ...lineItem,
    merchandise,
    cost,
    quantity
  };
};

const reshapeImages = (images?: MedusaImage[], productTitle?: string): Image[] => {
  if (!images) return [];
  return images.map((image) => {
    const filename = image.url.match(/.*\/(.*)\..*/)![1];
    return {
      ...image,
      altText: `${productTitle} - ${filename}`
    };
  });
};

const reshapeProduct = (product: MedusaProduct): Product => {
  const variant = product.variants?.[0];

  let amount = '0';
  let currencyCode = 'USD';

  if (variant) {
    const price = calculateVariantAmount(variant);
    amount = price.amount;
    currencyCode = price.currencyCode;
  }

  const priceRange = {
    maxVariantPrice: {
      amount,
      currencyCode
    }
  };

  const updatedAt = product.updated_at;
  const createdAt = product.created_at;
  const tags = product.tags?.map((tag) => tag.value) || [];
  const descriptionHtml = product.description ?? '';
  const featuredImageFilename = product.thumbnail?.match(/.*\/(.*)\..*/)![1];
  const featuredImage = {
    url: product.thumbnail ?? '',
    altText: product.thumbnail ? `${product.title} - ${featuredImageFilename}` : ''
  };
  const availableForSale = product.variants?.[0]?.purchasable || true;
  const images = reshapeImages(product.images, product.title);

  const variants = product.variants.map((variant) =>
    reshapeProductVariant(variant, product.options)
  );

  let options = [] as ProductOption[];
  product.options && (options = product.options.map((option) => reshapeProductOption(option)));

  return {
    ...product,
    images,
    featuredImage,
    priceRange,
    updatedAt,
    createdAt,
    tags,
    descriptionHtml,
    availableForSale,
    options,
    variants
  };
};

const reshapeProductOption = (productOption: MedusaProductOption): ProductOption => {
  const availableForSale = productOption.product?.variants?.[0]?.purchasable || true;
  const name = productOption.title;
  let values = productOption.values?.map((option) => option.value) || [];
  values = [...new Set(values)];

  return {
    ...productOption,
    availableForSale,
    name,
    values
  };
};

const reshapeProductVariant = (
  productVariant: MedusaProductVariant,
  productOptions?: MedusaProductOption[]
): ProductVariant => {
  let selectedOptions: SelectedOption[] = [];
  if (productOptions && productVariant.options) {
    const optionIdMap = mapOptionIds(productOptions);
    selectedOptions = productVariant.options.map((option) => ({
      name: optionIdMap[option.option_id] ?? '',
      value: option.value
    }));
  }
  const availableForSale = productVariant.purchasable || true;
  const price = calculateVariantAmount(productVariant);

  return {
    ...productVariant,
    availableForSale,
    selectedOptions,
    price
  };
};

const reshapeCategory = (category: ProductCategory): ProductCollection => {
  const description = category.description || category.metadata?.description?.toString() || '';
  const seo = {
    title: category?.metadata?.seo_title?.toString() || category.name || '',
    description: category?.metadata?.seo_description?.toString() || category.description || ''
  };
  // Use /categories/ path for category URLs
  const path = `/categories/${category.handle}`;
  const updatedAt = category.updated_at;
  const title = category.name;

  return {
    ...category,
    description,
    seo,
    title,
    path,
    updatedAt
  };
};

export async function createCart(): Promise<Cart | null> {
  try {
    // Get region_id to create cart with proper currency
    const regionId = await getRegionId();
    
    console.log('Creating cart with region_id:', regionId);
    
    const payload: any = {};
    if (regionId) {
      payload.region_id = regionId;
    }
    
    const res = await medusaRequest({ 
      method: 'POST', 
      path: '/carts',
      payload
    });
    
    if (!res.body.cart) {
      console.error('Failed to create cart: no cart in response. Body:', JSON.stringify(res.body));
      return null;
    }
    
    return reshapeCart(res.body.cart);
  } catch (e) {
    console.error('Exception in createCart:', e);
    return null;
  }
}

export async function addToCart(
  cartId: string,
  lineItem: { variantId: string; quantity: number }
): Promise<Cart | null> {
  try {
    console.log(`[addToCart] Adding to cart ${cartId}:`, lineItem);
    const res = await medusaRequest({
      method: 'POST',
      path: `/carts/${cartId}/line-items`,
      payload: {
        variant_id: lineItem?.variantId,
        quantity: lineItem?.quantity
      },
      tags: ['cart']
    });
    
    console.log(`[addToCart] Response status: ${res.status}, body:`, JSON.stringify(res.body));
    
    if (res.status !== 200 && res.status !== 201) {
      console.error(`[addToCart] Failed with status ${res.status}:`, res.body);
      return null;
    }
    
    // Re-fetch to get expanded fields
    const cart = await getCart(cartId);
    console.log(`[addToCart] Cart after adding:`, cart ? `${cart.lines.length} items, total: ${cart.totalQuantity}` : 'null');
    return cart;
  } catch (e) {
    console.error(`[addToCart] Exception:`, e);
    return null;
  }
}

export async function removeFromCart(cartId: string, lineItemId: string): Promise<Cart | null> {
  const res = await medusaRequest({
    method: 'DELETE',
    path: `/carts/${cartId}/line-items/${lineItemId}`,
    tags: ['cart']
  });
  
  // Re-fetch to get expanded fields
  return getCart(cartId);
}

export async function updateCart(
  cartId: string,
  { lineItemId, quantity }: { lineItemId: string; quantity: number }
): Promise<Cart | null> {
  const res = await medusaRequest({
    method: 'POST',
    path: `/carts/${cartId}/line-items/${lineItemId}`,
    payload: {
      quantity
    },
    tags: ['cart']
  });
  
  // Re-fetch to get expanded fields
  return getCart(cartId);
}

export async function getCart(cartId: string): Promise<Cart | null> {
  try {
    // Explicitly request all nested relations needed for option display
    // We need specific fields:
    // - items.variant.options.value: The selected value (e.g. "XL")
    // - items.variant.options.option.title: The option name (e.g. "Size")
    const res = await medusaRequest({ 
      method: 'GET', 
      path: `/carts/${cartId}?fields=+items,+items.variant,+items.variant.product,+items.variant.product.options,+items.variant.product.options.title,+items.variant.product.options.values,+items.variant.options,+items.variant.options.value,+items.variant.options.option,+items.variant.options.option.title,+region`, 
      tags: ['cart'] 
    });
    
    const cart = res.body.cart;

    if (!cart) {
      console.log(`[getCart] Cart ${cartId} not found in response. Status: ${res.status}`);
      console.log(`[getCart] Response body:`, JSON.stringify(res.body));
      return null;
    }

    return reshapeCart(cart);
  } catch (e) {
    console.error(`[getCart] Error fetching cart ${cartId}:`, e);
    return null;
  }
}

export async function getCategories(): Promise<ProductCollection[]> {
  const res = await medusaRequest({
    method: 'GET',
    path: '/product-categories',
    tags: ['categories']
  });

  // Reshape categories and hide categories starting with 'hidden'
  const categories = (res.body.product_categories || [])
    .map((collection: ProductCategory) => reshapeCategory(collection))
    .filter((collection: MedusaProductCollection) => !collection.handle.startsWith('hidden'));

  return categories;
}

export async function getCollections(): Promise<ProductCollection[]> {
  const res = await medusaRequest({
    method: 'GET',
    path: '/collections',
    tags: ['collections']
  });

  const collections = (res.body.collections || [])
    .map((collection: any) => ({
      id: collection.id,
      handle: collection.handle,
      title: collection.title,
      description: collection.metadata?.description || '',
      seo: {
        title: collection.title,
        description: collection.metadata?.description || ''
      },
      path: `/collections/${collection.handle}`,
      updatedAt: collection.updated_at
    }))
    .filter((collection: any) => !collection.handle.startsWith('hidden'));

  return collections;
}

export async function getCategory(handle: string): Promise<ProductCollection | undefined> {
  const res = await medusaRequest({
    method: 'GET',
    path: `/product-categories?handle=${handle}`,
    tags: ['categories', 'products']
  });
  return res.body.product_categories?.[0];
}

export async function getCategoryProducts(
  handle: string,
  reverse?: boolean,
  sortKey?: string,
  limit = 100,
  offset = 0
): Promise<Product[]> {
  const res = await medusaRequest({
    method: 'GET',
    path: `/product-categories?handle=${handle}`,
    tags: ['categories']
  });

  if (!res) {
    return [];
  }

  const category = res.body.product_categories?.[0];

  if (!category) {
    return [];
  }

  const category_products = await getProducts({ reverse, sortKey, categoryId: category.id, limit, offset });

  return category_products;
}

export async function getCollectionProducts(
  collectionId: string,
  reverse?: boolean,
  sortKey?: string,
  limit = 100,
  offset = 0
): Promise<Product[]> {
  return getProducts({ reverse, sortKey, collectionId, limit, offset });
}

export async function getProduct(handle: string): Promise<Product> {
  const regionId = await getRegionId();
  const res = await medusaRequest({
    method: 'GET',
    path: `/products?handle=${handle}&limit=1&region_id=${regionId}&fields=+variants.calculated_price,+variants.inventory_quantity`,
    tags: ['products']
  });
  const product = res.body.products[0];
  return reshapeProduct(product);
}

export async function getProducts({
  query,
  reverse,
  sortKey,
  categoryId,
  collectionId,
  limit = 100,
  offset = 0
}: {
  query?: string;
  reverse?: boolean;
  sortKey?: string;
  categoryId?: string;
  collectionId?: string;
  limit?: number;
  offset?: number;
}): Promise<Product[]> {
  let res;
  const regionId = await getRegionId();
  const params = `limit=${limit}&offset=${offset}&region_id=${regionId}&fields=+variants.calculated_price,+variants.inventory_quantity`;

  if (query) {
    res = await medusaRequest({
      method: 'GET',
      path: `/products?q=${query}&${params}`,
      tags: ['products']
    });
  } else if (categoryId) {
    res = await medusaRequest({
      method: 'GET',
      path: `/products?category_id=${categoryId}&${params}`,
      tags: ['products']
    });
  } else if (collectionId) {
    res = await medusaRequest({
      method: 'GET',
      path: `/products?collection_id[]=${collectionId}&${params}`,
      tags: ['products', 'collections']
    });
  } else {
    res = await medusaRequest({ method: 'GET', path: `/products?${params}`, tags: ['products'] });
  }

  if (!res) {
    console.error("Couldn't fetch products");
    return [];
  }

  if (!res?.body?.products) {
    return [];
  }

  let products: Product[] = res.body.products.map((product: MedusaProduct) =>
    reshapeProduct(product)
  );

  sortKey === 'PRICE' &&
    products.sort(
      (a, b) =>
        parseFloat(a.priceRange.maxVariantPrice.amount) -
        parseFloat(b.priceRange.maxVariantPrice.amount)
    );

  sortKey === 'CREATED_AT' &&
    products.sort((a, b) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime());

  reverse && products.reverse();

  return products;
}

export async function getMenu(menu: string): Promise<any[]> {
  if (menu === 'next-js-frontend-header-menu') {
    const categories = await getCategories();
    return categories.map((cat) => ({
      title: cat.title,
      path: cat.path
    }));
  }

  if (menu === 'next-js-frontend-footer-menu') {
    return [
      { title: 'About Medusa', path: 'https://medusajs.com/' },
      { title: 'Medusa Docs', path: 'https://docs.medusajs.com/' },
      { title: 'Medusa Blog', path: 'https://medusajs.com/blog' }
    ];
  }

  return [];
}

export async function medusaRegister(payload: any) {
  const res = await fetch(`${ENDPOINT}/auth/customer/emailpass/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-publishable-api-key': MEDUSA_API_KEY
    },
    body: JSON.stringify(payload)
  });
  
  const body = await res.json();
  if (res.status !== 200) {
    throw new Error(body.message || 'Registration failed');
  }
  return body;
}

export async function medusaLogin(payload: any) {
  const res = await fetch(`${ENDPOINT}/auth/customer/emailpass`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-publishable-api-key': MEDUSA_API_KEY
    },
    body: JSON.stringify(payload)
  });

  const body = await res.json();
  if (res.status !== 200) {
    throw new Error(body.message || 'Login failed');
  }
  return body;
}

export async function createCustomer(token: string, payload: any) {
  const res = await fetch(`${ENDPOINT}/store/customers`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-publishable-api-key': MEDUSA_API_KEY,
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(payload)
  });
  
  const body = await res.json();
  if (res.status !== 200) {
    throw new Error(body.message || 'Customer creation failed');
  }
  return body;
}

export async function getCustomer(token: string) {
  const res = await fetch(`${ENDPOINT}/store/customers/me`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'x-publishable-api-key': MEDUSA_API_KEY,
      'Authorization': `Bearer ${token}`
    }
  });
  
  if (res.status !== 200) {
    return null;
  }
  
  const body = await res.json();
  return body.customer;
}

export async function addAddress(token: string, payload: any) {
  const res = await fetch(`${ENDPOINT}/store/customers/me/addresses`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-publishable-api-key': MEDUSA_API_KEY,
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(payload)
  });
  
  const body = await res.json();
  if (res.status !== 200) {
    throw new Error(body.message || 'Failed to add address');
  }
  return body.customer;
}

// This is called from `app/api/revalidate.ts` so providers can control revalidation logic.
export async function revalidate(req: NextRequest): Promise<NextResponse> {
  // We always need to respond with a 200 status code to Medusa,
  // otherwise it will continue to retry the request.
  const collectionWebhooks = ['categories/create', 'categories/delete', 'categories/update'];
  const productWebhooks = ['products/create', 'products/delete', 'products/update'];
  const topic = headers().get('x-medusa-topic') || 'unknown';
  const secret = req.nextUrl.searchParams.get('secret');
  const isCollectionUpdate = collectionWebhooks.includes(topic);
  const isProductUpdate = productWebhooks.includes(topic);

  if (!secret || secret !== process.env.MEDUSA_REVALIDATION_SECRET) {
    console.error('Invalid revalidation secret.');
    return NextResponse.json({ status: 200 });
  }

  if (!isCollectionUpdate && !isProductUpdate) {
    // We don't need to revalidate anything for any other topics.
    return NextResponse.json({ status: 200 });
  }

  if (isCollectionUpdate) {
    revalidateTag(TAGS.categories);
  }

  if (isProductUpdate) {
    revalidateTag(TAGS.products);
  }

  return NextResponse.json({ status: 200, revalidated: true, now: Date.now() });
}

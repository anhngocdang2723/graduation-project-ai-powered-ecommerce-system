const fs = require('fs');
const path = require('path');

// Load env vars
const envPath = path.resolve(__dirname, '.env.local');
let MEDUSA_BACKEND_API = 'http://localhost:9000';
let MEDUSA_API_KEY = '';

if (fs.existsSync(envPath)) {
  const envConfig = fs.readFileSync(envPath, 'utf8');
  envConfig.split('\n').forEach(line => {
    const [key, value] = line.split('=');
    if (key && value) {
      const cleanValue = value.replace(/"/g, '').trim();
      if (key.trim() === 'NEXT_PUBLIC_MEDUSA_BACKEND_API') MEDUSA_BACKEND_API = cleanValue;
      if (key.trim() === 'MEDUSA_API_KEY') MEDUSA_API_KEY = cleanValue;
    }
  });
}

async function medusaRequest(path) {
  const url = `${MEDUSA_BACKEND_API}/store${path}`;
  const headers = {
    'Content-Type': 'application/json',
    'x-publishable-api-key': MEDUSA_API_KEY
  };

  console.log(`Fetching: GET ${url}`);
  try {
    const res = await fetch(url, { method: 'GET', headers });
    if (!res.ok) {
        console.log(`Error: ${res.status} ${res.statusText}`);
        console.log(await res.text());
        return null;
    }
    return await res.json();
  } catch (error) {
    console.error('Fetch error:', error.message);
    return null;
  }
}

async function verify() {
  console.log('--- Verifying Homepage Data ---');
  
  const collections = ['hidden-homepage-featured-items', 'hidden-homepage-carousel'];

  for (const handle of collections) {
      console.log(`\nChecking '${handle}'...`);
      // 1. Get Category
      const catRes = await medusaRequest(`/product-categories?handle=${handle}`);
      
      if (!catRes || !catRes.product_categories || catRes.product_categories.length === 0) {
          console.log(`❌ Category '${handle}' NOT FOUND.`);
          continue;
      }

      const category = catRes.product_categories[0];
      console.log(`✅ Category found: ${category.id} (${category.name})`);

      // 2. Get Products in Category
      const prodRes = await medusaRequest(`/products?category_id[]=${category.id}`);
      
      if (!prodRes || !prodRes.products || prodRes.products.length === 0) {
          console.log(`❌ No products found in category '${handle}'.`);
      } else {
          console.log(`✅ Found ${prodRes.products.length} products:`);
          prodRes.products.forEach(p => console.log(`   - ${p.title} (${p.id})`));
      }
  }
}

verify();

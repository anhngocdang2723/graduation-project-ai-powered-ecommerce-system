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
    console.log(`Status: ${res.status} ${res.statusText}`);
    const text = await res.text();
    try {
      const json = JSON.parse(text);
      return json;
    } catch (e) {
      console.log('Response is not JSON:', text);
      return null;
    }
  } catch (error) {
    console.error('Fetch error:', error.message);
    return null;
  }
}

async function debug() {
  console.log('--- Debugging Category Fetch ---');
  
  // 1. Fetch without expand (known to work based on previous test)
  console.log('\n1. Fetching "shirts" WITHOUT expand...');
  const res1 = await medusaRequest('/product-categories?handle=shirts');
  if (res1 && res1.product_categories && res1.product_categories.length > 0) {
    console.log('✅ Found:', res1.product_categories[0].id);
  } else {
    console.log('❌ Not found or empty.');
    console.log('Response:', JSON.stringify(res1, null, 2));
  }

  // 2. Fetch WITH expand (as used in the failing code)
  console.log('\n2. Fetching "shirts" WITH expand=products...');
  const res2 = await medusaRequest('/product-categories?handle=shirts&expand=products');
  if (res2 && res2.product_categories && res2.product_categories.length > 0) {
    console.log('✅ Found:', res2.product_categories[0].id);
  } else {
    console.log('❌ Not found or empty.');
    console.log('Response:', JSON.stringify(res2, null, 2));
  }
  
  // 3. Fetch WITH fields (Medusa v2 style?)
  console.log('\n3. Fetching "shirts" WITH fields=*...');
  const res3 = await medusaRequest('/product-categories?handle=shirts&fields=*');
  if (res3 && res3.product_categories && res3.product_categories.length > 0) {
    console.log('✅ Found:', res3.product_categories[0].id);
  } else {
    console.log('❌ Not found or empty.');
    console.log('Response:', JSON.stringify(res3, null, 2));
  }
}

debug();

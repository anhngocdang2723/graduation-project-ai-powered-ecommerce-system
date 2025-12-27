# 🚀 Medusa v2 Setup Guide

Tài liệu hướng dẫn setup Medusa từ đầu - dùng khi:
- Build lại Docker
- Xóa database
- Deploy lên VPS mới

---

## 📚 Kiến thức cơ bản

### 1. Medusa Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         MEDUSA STORE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │    STORE     │    │    ADMIN     │    │     API      │      │
│  │  (Frontend)  │    │   Dashboard  │    │   Backend    │      │
│  │  Port 3000   │    │  Port 9000   │    │  Port 9000   │      │
│  └──────┬───────┘    └──────┬───────┘    └──────────────┘      │
│         │                   │                                   │
│         ▼                   ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    MEDUSA BACKEND                        │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │   │
│  │  │ Products│ │ Regions │ │  Cart   │ │ Orders  │       │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    PostgreSQL + Redis                    │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Core Concepts

#### 🌍 Region (Khu vực bán hàng)
Region đại diện cho một khu vực địa lý mà store bán hàng.

| Thuộc tính | Mô tả | Ví dụ |
|------------|-------|-------|
| `name` | Tên region | "Europe", "Vietnam" |
| `currency_code` | Mã tiền tệ | "eur", "vnd", "usd" |
| `countries` | Danh sách quốc gia | DE, FR, VN |
| `tax_rate` | Thuế suất | 10% |

**Tại sao cần Region?**
- Cart (giỏ hàng) BẮT BUỘC phải thuộc về 1 Region
- Region quyết định: tiền tệ, thuế, shipping options
- Không có Region → Không tạo được Cart → Không mua được hàng

#### 📦 Sales Channel (Kênh bán hàng)
Nơi sản phẩm được bán (website, app, marketplace...).

```
Sales Channel "Website"  ──┬── Product A
                           ├── Product B
                           └── Product C

Sales Channel "Mobile App" ──┬── Product A
                             └── Product D
```

#### 🔑 Publishable API Key
Key để Frontend gọi API. Mỗi key được link với Sales Channel.

```
Frontend (Store) 
    │
    │  x-publishable-api-key: pk_xxx...
    ▼
Medusa Backend
    │
    │  Check: Key này thuộc Sales Channel nào?
    ▼
Trả về Products của Sales Channel đó
```

### 3. Data Flow khi mua hàng

```
1. User vào Store
   │
   ▼
2. Fetch Regions → Chọn Region (VD: Europe/EUR)
   │
   ▼
3. Fetch Products → Hiển thị sản phẩm với giá EUR
   │
   ▼
4. Add to Cart → Tạo Cart với region_id
   │
   ▼
5. Checkout → Nhập shipping, payment
   │
   ▼
6. Place Order → Tạo Order
```

---

## 🔧 Setup Steps

### Bước 1: Khởi động Docker

```bash
cd my-medusa-store
docker compose up -d
```

Chờ ~30s để services khởi động hoàn tất.

### Bước 2: Chạy Migration (nếu DB mới)

```bash
docker compose exec medusa npx medusa db:migrate
```

### Bước 3: Seed Data

Chạy script seed để tạo dữ liệu mẫu:

```bash
docker compose exec medusa npx medusa exec ./src/scripts/seed.ts
```

Script này tạo:
- ✅ Regions (Europe/EUR)
- ✅ Tax Regions
- ✅ Stock Locations
- ✅ Fulfillment Providers
- ✅ Publishable API Key
- ✅ Products (4 sản phẩm mẫu)
- ✅ Inventory Levels

### Bước 4: Tạo Admin User

```bash
docker compose exec medusa npx medusa user -e admin@medusa-test.com -p supersecret
```

### Bước 5: Lấy Publishable API Key

**Cách 1: Từ Admin UI**
1. Truy cập: http://localhost:9000/app
2. Login với admin account
3. Vào Settings → Publishable API Keys
4. Copy key (format: `pk_xxx...`)

**Cách 2: Từ Database (pgAdmin)**
1. Truy cập pgAdmin: http://localhost:5050
2. Login: admin@admin.com / root
3. Query:
```sql
SELECT * FROM public.api_key WHERE type = 'publishable';
```

### Bước 6: Link API Key với Sales Channel

⚠️ **QUAN TRỌNG!** API Key phải được link với Sales Channel, nếu không sẽ không trả về products.

1. Admin UI → Settings → Publishable API Keys
2. Click vào key → Edit
3. Trong "Sales Channels" → Add "Default Sales Channel"
4. Save

### Bước 7: Cấu hình Frontend (.env.local)

Tạo file `vercel-commerce/.env.local`:

```env
# Medusa Backend URL
NEXT_PUBLIC_MEDUSA_BACKEND_URL=http://localhost:9000

# Publishable API Key (lấy từ Bước 5)
NEXT_PUBLIC_MEDUSA_PUBLISHABLE_KEY=pk_your_key_here

# Site URL
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

### Bước 8: Khởi động Frontend

```bash
cd vercel-commerce
pnpm install
pnpm dev
```

---

## ✅ Verification Checklist

### Test APIs

```powershell
# Test Products API
$headers = @{"x-publishable-api-key"="pk_your_key_here"}

# 1. Products (phải có ít nhất 1 product)
Invoke-RestMethod -Uri "http://localhost:9000/store/products" -Headers $headers

# 2. Regions (phải có ít nhất 1 region)
Invoke-RestMethod -Uri "http://localhost:9000/store/regions" -Headers $headers

# 3. Test tạo Cart
$body = @{region_id="reg_xxx"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:9000/store/carts" -Method POST -Headers $headers -Body $body -ContentType "application/json"
```

### Checklist

| Component | Check | Command/URL |
|-----------|-------|-------------|
| Medusa Backend | ✅ Running | http://localhost:9000/health |
| Admin UI | ✅ Accessible | http://localhost:9000/app |
| Products API | ✅ Returns data | GET /store/products |
| Regions API | ✅ Returns data | GET /store/regions |
| API Key | ✅ Linked to Sales Channel | Admin UI check |
| Frontend | ✅ Shows products | http://localhost:3000 |

---

## 🔥 Troubleshooting

### Problem: "Failed to create cart"

**Nguyên nhân:**
1. Không có Region trong database
2. API Key không hợp lệ
3. API Key chưa link với Sales Channel

**Giải pháp:**
```bash
# Check regions
curl http://localhost:9000/store/regions -H "x-publishable-api-key: pk_xxx"

# Nếu empty, chạy seed
docker compose exec medusa npx medusa exec ./src/scripts/seed.ts
```

### Problem: Products API trả về empty

**Nguyên nhân:**
1. Chưa có products trong DB
2. API Key chưa link Sales Channel
3. Products chưa được publish

**Giải pháp:**
1. Chạy seed script
2. Vào Admin → Settings → Publishable API Keys → Link Sales Channel
3. Vào Admin → Products → Set status = "Published"

### Problem: "Cannot read properties of undefined (reading 'region')"

**Nguyên nhân:** Cart object là undefined/null

**Giải pháp:** Đã fix trong `lib/medusa/index.ts` - thêm null checks

---

## 📁 File Structure

```
my-medusa-store/
├── docker-compose.yml      # Docker services config
├── Dockerfile             # Medusa image build
├── medusa-config.ts       # Medusa configuration
├── src/
│   ├── scripts/
│   │   └── seed.ts        # Seed script (products, regions)
│   ├── api/               # Custom API routes
│   ├── admin/             # Admin UI customizations
│   └── modules/           # Custom modules
└── docs/
    └── MEDUSA-SETUP-GUIDE.md  # This file

vercel-commerce/
├── .env.local             # Environment variables
├── lib/medusa/            # Medusa API client
└── app/                   # Next.js pages
```

---

## 🚀 Quick Start Script

Tạo file `setup.sh` để tự động setup:

```bash
#!/bin/bash

echo "🚀 Starting Medusa Setup..."

# 1. Start Docker
echo "📦 Starting Docker containers..."
docker compose up -d

# 2. Wait for services
echo "⏳ Waiting for services to start..."
sleep 30

# 3. Run migrations
echo "🔄 Running migrations..."
docker compose exec medusa npx medusa db:migrate

# 4. Seed data
echo "🌱 Seeding data..."
docker compose exec medusa npx medusa exec ./src/scripts/seed.ts

# 5. Create admin user
echo "👤 Creating admin user..."
docker compose exec medusa npx medusa user -e admin@medusa-test.com -p supersecret

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Go to http://localhost:9000/app and login"
echo "2. Get Publishable API Key from Settings"
echo "3. Link API Key to Sales Channel"
echo "4. Update vercel-commerce/.env.local with the API Key"
echo "5. Run 'pnpm dev' in vercel-commerce folder"
```

---

## 📝 Notes

- **Mỗi lần reset DB** cần chạy lại seed script
- **API Key thay đổi** mỗi lần seed → cần update `.env.local`
- **Seed script** có thể customize trong `src/scripts/seed.ts`
- **Region mặc định** là Europe/EUR, có thể thêm VN/VND trong Admin UI

---

*Last updated: 2025-11-30*

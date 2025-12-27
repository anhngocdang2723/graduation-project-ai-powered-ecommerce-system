# 🚀 Medusa Setup Guide - Production vs Development

## 📋 Tóm tắt nhanh

| Môi trường | Cách setup | Thời gian | Phù hợp cho |
|------------|------------|-----------|-------------|
| **Development** | Chạy seed script | 1 phút | Local testing, demo |
| **Production** | Setup thủ công qua Admin UI | 10-15 phút | Store thật |

---

## 🔧 Option A: Development (Dùng Seed)

```bash
# 1. Start Docker
cd my-medusa-store
docker compose up -d

# 2. Chờ services khởi động
# Khoảng 30 giây

# 3. Chạy migration
docker compose exec medusa npx medusa db:migrate

# 4. Chạy seed script
docker compose exec medusa npx medusa exec ./src/scripts/seed.ts

# 5. Tạo admin user
docker compose exec medusa npx medusa user -e admin@test.com -p supersecret

# 6. Lấy API Key từ database
docker compose exec postgres psql -U postgres -d "medusa-store" -c "SELECT token FROM api_key WHERE type = 'publishable' AND title = 'Webshop';"
```

**Seed tạo sẵn:**
- ✅ Region: Europe (EUR)
- ✅ Sales Channel: Default Sales Channel
- ✅ Publishable API Key: "Webshop" (đã link Sales Channel)
- ✅ 4 Products mẫu (T-Shirt, Sweatshirt, Sweatpants, Shorts)
- ✅ Stock Location + Inventory

**Sau khi seed:** Chỉ cần copy API Key vào `.env.local` và chạy FE!

---

## 🏭 Option B: Production (Setup thủ công)

Khi deploy VPS/production, KHÔNG dùng seed. Tạo data thủ công:

### Bước 1: Khởi động Backend

```bash
cd my-medusa-store
docker compose up -d
docker compose exec medusa npx medusa db:migrate
docker compose exec medusa npx medusa user -e admin@yourstore.com -p your-secure-password
```

### Bước 2: Vào Admin UI

Truy cập: `http://your-vps-ip:9000/app`

Login với email/password vừa tạo.

### Bước 3: Tạo Data theo thứ tự

⚠️ **THỨ TỰ QUAN TRỌNG!** Phải tạo đúng thứ tự, không sẽ bị lỗi.

```
┌─────────────────────────────────────────────────────────────┐
│  BƯỚC 1: REGION (Bắt buộc đầu tiên!)                       │
│  └── Settings → Regions → Create                            │
│      • Name: "Vietnam"                                      │
│      • Currency: VND                                        │
│      • Countries: Chọn Vietnam                              │
│      • Payment Providers: (sau này thêm)                    │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  BƯỚC 2: SALES CHANNEL (Thường đã có sẵn)                  │
│  └── Settings → Sales Channels                              │
│      • Kiểm tra có "Default Sales Channel"                  │
│      • Nếu không có → Create: "Website"                     │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  BƯỚC 3: PUBLISHABLE API KEY                               │
│  └── Settings → Publishable API Keys → Create               │
│      • Title: "Webshop"                                     │
│      • Sales Channels: Add "Default Sales Channel"          │
│      → Copy key (pk_xxx...) cho FE!                         │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  BƯỚC 4: STOCK LOCATION                                    │
│  └── Settings → Locations → Create                          │
│      • Name: "Kho chính"                                    │
│      • Address: Địa chỉ kho                                 │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  BƯỚC 5: SHIPPING (Optional nhưng nên có)                  │
│  └── Settings → Shipping                                    │
│      • Create Shipping Profile                              │
│      • Create Shipping Options cho từng region              │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  BƯỚC 6: PRODUCTS                                          │
│  └── Products → Create                                      │
│      • Title, Description, Images                           │
│      • Variants (Size, Color...)                            │
│      • Pricing: Set giá cho từng region                     │
│      • Inventory: Set số lượng tại Stock Location           │
│      • Sales Channels: Add "Default Sales Channel"          │
│      • Status: Published ✅                                  │
└─────────────────────────────────────────────────────────────┘
```

### Bước 4: Cấu hình Frontend

```env
# vercel-commerce/.env.local

# Backend URL
NEXT_PUBLIC_MEDUSA_BACKEND_API=http://your-vps-ip:9000

# API Key từ bước 3
MEDUSA_API_KEY=pk_xxx...

# Các config khác
SITE_NAME="Your Store Name"
NEXT_PUBLIC_VERCEL_URL=http://your-vps-ip:3000
```

---

## ✅ Verification Checklist

Sau khi setup xong, kiểm tra:

```powershell
# Thay YOUR_API_KEY và YOUR_SERVER
$headers = @{"x-publishable-api-key"="YOUR_API_KEY"}
$server = "http://localhost:9000"  # hoặc http://your-vps-ip:9000

# 1. Test regions (phải có ít nhất 1)
Invoke-RestMethod -Uri "$server/store/regions" -Headers $headers

# 2. Test products (phải có ít nhất 1)
Invoke-RestMethod -Uri "$server/store/products" -Headers $headers

# 3. Test create cart (thay REGION_ID từ bước 1)
$body = '{"region_id":"reg_xxx"}'
Invoke-RestMethod -Uri "$server/store/carts" -Method POST -Headers $headers -Body $body -ContentType "application/json"
```

**Checklist:**

| # | Item | Dev (Seed) | Prod (Manual) |
|---|------|------------|---------------|
| 1 | Region tồn tại | ✅ Auto | ☐ Tự tạo |
| 2 | Sales Channel | ✅ Auto | ☐ Check/Tạo |
| 3 | API Key linked | ✅ Auto | ☐ Tự link |
| 4 | Stock Location | ✅ Auto | ☐ Tự tạo |
| 5 | Products | ✅ 4 mẫu | ☐ Tự thêm |
| 6 | Products published | ✅ Auto | ☐ Tự publish |
| 7 | Prices set | ✅ Auto | ☐ Tự set |
| 8 | Inventory set | ✅ Auto | ☐ Tự set |

---

## 🔥 Common Issues

### Issue 1: Products API trả về `[]` empty

**Nguyên nhân:**
- API Key chưa link Sales Channel
- Products chưa assign vào Sales Channel
- Products chưa Published

**Fix:**
1. Admin → Settings → API Keys → Edit → Add Sales Channel
2. Admin → Products → Edit → Sales Channels → Add channel
3. Admin → Products → Status → Published

### Issue 2: "Failed to create cart"

**Nguyên nhân:**
- Không có Region
- Region ID trong cookie cũ/không tồn tại

**Fix:**
1. Tạo Region trong Admin UI
2. Xóa cookie `_medusa_region_id` trong browser

### Issue 3: Prices = 0 hoặc không hiển thị

**Nguyên nhân:**
- Product variant chưa có price cho region đó

**Fix:**
- Admin → Products → Edit → Variants → Pricing → Add price

### Issue 4: "A valid publishable key is required"

**Nguyên nhân:**
- API Key sai hoặc không tồn tại
- API Key chưa link Sales Channel

**Fix:**
- Lấy lại key từ Admin UI
- Link với Sales Channel

---

## 📝 Notes quan trọng

1. **Mỗi lần reset DB** → Phải setup lại từ đầu
2. **API Key khác nhau** giữa dev và prod → Cập nhật `.env.local`
3. **Region ID** có thể cache trong cookie → Xóa cookie nếu đổi region
4. **Seed script** chỉ dùng cho dev, KHÔNG dùng cho production thật

---

## 🔗 Quick Links

- Admin UI: `http://localhost:9000/app`
- Store API: `http://localhost:9000/store/*`
- Admin API: `http://localhost:9000/admin/*`
- pgAdmin: `http://localhost:5050`

---

*Last updated: 2025-11-30*

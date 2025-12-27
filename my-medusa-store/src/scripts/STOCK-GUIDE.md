# Stock Management Scripts - Quick Guide

## 🚀 Quick Start

### Thêm stock cho TẤT CẢ sản phẩm (100 units mỗi sản phẩm):

```bash
cd my-medusa-store
npx medusa exec ./src/scripts/add-stock.ts
```

### Thêm stock với SỐ LƯỢNG TÙY CHỈNH:

1. Mở file `src/scripts/add-stock-custom.ts`
2. Sửa config:
```typescript
const STOCK_CONFIG = {
  defaultQuantity: 100,  // Số lượng mặc định
  
  // Số lượng riêng theo SKU
  customQuantities: {
    "BACKPACK-001": 500,
    "SHIRT-M": 250,
  }
}
```
3. Chạy:
```bash
npm run medusa exec ./src/scripts/add-stock-custom.ts
```

---

## 📋 Các Script Có Sẵn

### 1. `add-stock.ts` - Thêm Stock Cơ Bản
- Tự động thêm 100 units cho mỗi variant
- Tạo stock location nếu chưa có
- Không cần config gì cả, chỉ cần chạy

**Khi nào dùng:** Khi muốn add stock nhanh cho tất cả sản phẩm

### 2. `add-stock-custom.ts` - Thêm Stock Nâng Cao  
- Tùy chỉnh số lượng theo từng SKU
- Set số lượng theo khoảng giá
- Linh hoạt hơn

**Khi nào dùng:** Khi cần control số lượng chi tiết

---

## ✅ Kết Quả Sau Khi Chạy

```
==============================================================
Stock addition completed!
==============================================================
Total products processed: 50
Total variants processed: 150
Inventory items created: 75
Inventory levels updated: 75
==============================================================
```

---

## 🔧 Tùy Chỉnh

### Thay đổi số lượng mặc định:

Mở `add-stock.ts`, tìm dòng:
```typescript
const defaultStockQuantity = 100 // Đổi số này
```

### Thêm stock theo giá:

Trong `add-stock-custom.ts`:
```typescript
priceRanges: {
  enabled: true,  // Bật tính năng
  ranges: [
    { minPrice: 0, maxPrice: 50, quantity: 200 },    // Hàng rẻ: nhiều stock
    { minPrice: 50, maxPrice: 200, quantity: 100 },  // Trung bình
    { minPrice: 200, maxPrice: 999999, quantity: 50 }, // Đắt: ít stock
  ]
}
```

---

## 🐛 Troubleshooting

### Lỗi "No stock location found"
Script sẽ tự tạo location. Nếu vẫn lỗi, kiểm tra database.

### Stock không hiển thị trên web
1. Vào Medusa Admin → Products → Inventory
2. Verify số lượng đã được add
3. Refresh cache của Next.js

### Muốn xóa stock và thêm lại
Xóa inventory trong Admin hoặc database, rồi chạy lại script.

---

## 💡 Tips

- ✅ **Backup trước khi chạy:** Export database để phòng lỗi
- ✅ **Test với ít sản phẩm:** Comment code để test trước
- ✅ **Chạy lại an toàn:** Scripts có thể chạy nhiều lần
- ✅ **Xem logs:** Terminal sẽ show chi tiết từng bước

---

## 📖 Chi Tiết Kỹ Thuật

Xem [README.md](./README.md) trong thư mục scripts để biết thêm chi tiết.

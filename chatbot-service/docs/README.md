# 🤖 CHATBOT SERVICE - PROJECT DOCUMENTATION

## Tổng quan dự án

**Mục tiêu:** Xây dựng hệ thống Multi-Agent Chatbot tích hợp với Medusa E-commerce

**Tech Stack:**
- Backend: Python FastAPI
- AI Model: Qwen3-Max (Alibaba DashScope)
- Database: PostgreSQL (shared với Medusa)
- Frontend: Next.js (vercel-commerce)
- Admin: Medusa Admin UI

---

## 📁 Documentation Structure

| File | Nội dung |
|------|----------|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Kiến trúc Multi-Agent, sơ đồ hệ thống |
| [DECISION_TREE.md](./DECISION_TREE.md) | Kịch bản phân nhánh, intent definitions |
| [PROGRESS.md](./PROGRESS.md) | Tiến độ thực hiện, checklist |
| [API.md](./API.md) | API documentation (sẽ bổ sung) |

---

## 🎯 Yêu cầu chức năng (Thống nhất)

### 1. Ngôn ngữ hỗ trợ
- **Tiếng Việt (VN)** - Ngôn ngữ chính
- **English (EN)** - Hỗ trợ thêm
- Agent sẽ tự động detect ngôn ngữ và response phù hợp

### 2. Xác thực người dùng
- ✅ Cho phép **Guest chat** (chưa đăng nhập)
- ✅ **Customer chat** (đã đăng nhập)
- Agent sẽ xác định user type để:
  - Guest: Giới hạn một số chức năng (không xem order history, không lưu address)
  - Customer: Full access
- **Khi Guest cần chức năng của Customer:**
  - Hướng dẫn đăng ký/đăng nhập
  - **Quan trọng:** Giữ session chat sau khi đăng ký để không mất context

### 3. Mức độ tự động hóa
- ✅ Tự động tìm kiếm sản phẩm
- ✅ Tự động thêm vào giỏ hàng
- ✅ Tự động điền thông tin shipping
- ❌ **Thanh toán:** User phải tự thực hiện (redirect to checkout page)

### 4. Human Escalation (Chuyển cho nhân viên)
- ✅ Có chức năng chuyển cuộc trò chuyện cho nhân viên thật
- Nhân viên có thể can thiệp thay thế AI ngay trong đoạn chat
- **Đề xuất implementation:**
  - Thêm role `staff` trong messages
  - Thêm trạng thái session: `active` | `escalated` | `closed`
  - Admin UI có realtime notification khi có escalation
  - Staff có thể "take over" và chat trực tiếp

---

## 🔗 Quick Links

- **Chatbot API:** http://localhost:8000
- **Medusa Backend:** http://localhost:9000
- **Medusa Admin:** http://localhost:9000/app
- **Frontend:** http://localhost:3000
- **PgAdmin:** http://localhost:5050

---

## 📅 Timeline

| Phase | Thời gian | Trạng thái |
|-------|-----------|------------|
| Phase 1: Core Agents | Tuần 1 | 🔲 In Progress |
| Phase 2: Tools & Medusa Integration | Tuần 2 | 🔲 Not Started |
| Phase 3: Response & Templates | Tuần 3 | 🔲 Not Started |
| Phase 4: FE Widget & Admin UI | Tuần 4 | 🔲 Not Started |

---

*Last updated: 2025-11-30*

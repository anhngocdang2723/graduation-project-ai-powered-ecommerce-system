# 🐳 Docker Commands - Graduation Project

## 📍 Vị trí chạy lệnh
**LUÔN LUÔN** chạy từ folder gốc: `d:\Edu\graduation-project\`

---

## 🚀 Khởi động hệ thống

### Lần đầu tiên (hoặc khi thay đổi code)
```bash
docker compose up -d --build
```
- `up`: Khởi động containers
- `-d`: Chạy nền (detached)
- `--build`: Build lại images (dùng khi thay đổi Dockerfile hoặc code)

### Các lần sau (không thay đổi code)
```bash
docker compose up -d
```

### Chỉ khởi động 1 service cụ thể
```bash
docker compose up -d medusa          # Chỉ backend
docker compose up -d chatbot         # Chỉ chatbot
docker compose up -d postgres redis  # Chỉ databases
```

---

## 🛑 Dừng hệ thống

### Dừng tất cả (giữ data)
```bash
docker compose down
```

### Dừng và XÓA data (reset hoàn toàn)
```bash
docker compose down -v
```
⚠️ **Cẩn thận:** `-v` sẽ xóa database!

---

## 📊 Kiểm tra trạng thái

### Xem containers đang chạy
```bash
docker compose ps
```

### Xem logs của service
```bash
docker logs medusa_backend           # Logs Medusa
docker logs medusa_chatbot           # Logs Chatbot
docker logs medusa_postgres          # Logs Database

# Theo dõi logs realtime (tail -f)
docker logs -f medusa_backend
docker logs --tail 50 medusa_backend # 50 dòng cuối
```

---

## 🔄 Restart services

### Restart 1 service
```bash
docker restart medusa_backend
docker restart medusa_chatbot
```

### Rebuild và restart 1 service
```bash
docker compose up -d --build medusa
docker compose up -d --build chatbot
```

---

## 🛠️ Debug & Troubleshoot

### 🗄️ Database & Schema (Quan trọng)

#### Khôi phục Chatbot Schema
Nếu build lại image và bị mất bảng `chatbot` trong database, chạy lệnh này để tạo lại:
```bash
# Windows (PowerShell/CMD)
type chatbot-service\database\init.sql | docker exec -i medusa_postgres psql -U postgres -d medusa-store

# Linux/Mac
cat chatbot-service/database/init.sql | docker exec -i medusa_postgres psql -U postgres -d medusa-store
```

#### Kiểm tra Schema tồn tại chưa
```bash
docker exec -i medusa_postgres psql -U postgres -d medusa-store -c "SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'chatbot';"
```

### Vào bên trong container
```bash
docker exec -it medusa_backend sh     # Vào Medusa (Alpine Linux)
docker exec -it medusa_chatbot bash   # Vào Chatbot (Debian)
docker exec -it medusa_postgres psql -U postgres  # Vào PostgreSQL
```

### Xem resource usage
```bash
docker stats
```

### Xóa cache/images cũ
```bash
docker system prune -a
```

---

## 🌐 Ports & URLs

| Service | Port | URL |
|---------|------|-----|
| Medusa Backend | 9000 | http://localhost:9000 |
| Medusa Admin | 9000 / 41401 | http://localhost:9000/app hoặc http://localhost:41401/app |
| Chatbot API | 8000 | http://localhost:8000 |
| Chatbot Docs | 8000 | http://localhost:8000/docs |
| pgAdmin | 5050 | http://localhost:5050 |
| PostgreSQL | 5432 | localhost:5432 |
| Redis | 6379 | localhost:6379 |

---

## 📦 Cấu trúc Docker

```
graduation-project/
├── docker-compose.yml          # 👈 FILE CHÍNH
│
├── my-medusa-store/
│   ├── Dockerfile              # Build Node.js image
│   ├── start.sh                # Script chạy migrations + dev server
│   ├── .env                    # Biến môi trường Medusa
│   └── docker-compose.yml      # ❌ BỎ QUA (file cũ)
│
├── chatbot-service/
│   ├── Dockerfile              # Build Python image
│   ├── .env                    # Biến môi trường (API keys)
│   └── requirements.txt        # Python dependencies
│
└── vercel-commerce/            # FE - Deploy trên Vercel
    └── (không cần Docker)
```

---

## 🚢 Deploy lên VPS

### 1. Cài Docker trên VPS
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose-plugin -y
sudo systemctl enable docker
```

### 2. Clone code và chạy
```bash
git clone <your-repo> graduation-project
cd graduation-project
docker compose up -d --build
```

### 3. Cấu hình Production
- Sửa `.env` files với credentials thật
- Thêm SSL/HTTPS với reverse proxy (nginx)
- Đổi `NODE_ENV=production`

---

## ❓ FAQ

**Q: Tại sao có 2 file docker-compose.yml?**
A: File ở `my-medusa-store/docker-compose.yml` là file cũ, KHÔNG DÙNG. 
   Chỉ dùng file ở folder gốc `graduation-project/docker-compose.yml`.

**Q: Có cần cài Node.js/Python trên máy không?**
A: KHÔNG. Docker đã bao gồm tất cả. Chỉ cần Docker Desktop.

**Q: Làm sao biết service đã chạy thành công?**
A: Chạy `docker compose ps` - tất cả phải ở trạng thái "running".

**Q: Lỗi "port already in use"?**
A: Có app khác đang dùng port đó. Dừng app đó hoặc đổi port trong docker-compose.yml.

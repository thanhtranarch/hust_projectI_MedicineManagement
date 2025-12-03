# Hướng dẫn Migration từ MySQL sang Supabase

## Tổng quan

Dự án **MediManager** đã được migrate từ MySQL local (XAMPP) sang **Supabase** (PostgreSQL Cloud). Tài liệu này hướng dẫn cách thiết lập và sử dụng phiên bản mới.

---

## Các thay đổi chính

### 1. Database Engine
- **Trước**: MySQL/MariaDB (local via XAMPP)
- **Sau**: PostgreSQL (Supabase Cloud)

### 2. Database Driver
- **Trước**: `MySQLdb` / `mysqlclient`
- **Sau**: `psycopg2-binary`

### 3. Cấu hình kết nối
- **Trước**: Hard-coded trong DBManager.py
- **Sau**: Sử dụng environment variables (.env file)

### 4. Auto-increment syntax
- **Trước**: `AUTO_INCREMENT` (MySQL)
- **Sau**: `SERIAL` (PostgreSQL)

---

## Bước 1: Tạo Supabase Project

### 1.1. Đăng ký Supabase

1. Truy cập: https://supabase.com
2. Đăng nhập bằng GitHub hoặc email
3. Click **"New Project"**

### 1.2. Cấu hình Project

1. **Organization**: Chọn hoặc tạo organization
2. **Project Name**: Đặt tên (ví dụ: `medimanager`)
3. **Database Password**: Đặt mật khẩu mạnh (LƯU LẠI!)
4. **Region**: Chọn region gần nhất (ví dụ: `Southeast Asia (Singapore)`)
5. **Pricing Plan**: Chọn **Free** (đủ cho development)
6. Click **"Create new project"**

⏱️ **Chờ 2-3 phút** để Supabase khởi tạo project.

---

## Bước 2: Lấy Database Credentials

### 2.1. Database Settings

1. Vào **Settings** (icon bánh răng) → **Database**
2. Trong phần **Connection info**, copy các thông tin:
   - **Host**: `db.xxxxxxxxxxxxx.supabase.co`
   - **Database name**: `postgres`
   - **Port**: `5432`
   - **User**: `postgres`
   - **Password**: (password bạn đã đặt ở bước 1.2)

### 2.2. API Settings

1. Vào **Settings** → **API**
2. Copy các thông tin:
   - **Project URL**: `https://xxxxxxxxxxxxx.supabase.co`
   - **Project API keys** → **anon public**: `eyJhbGc...` (key dài)

---

## Bước 3: Cấu hình môi trường local

### 3.1. Clone/Pull code mới

```bash
git checkout claude/migrate-supabase-cloud-01DxBLZkbRazSd8eaMNBg5oC
git pull origin claude/migrate-supabase-cloud-01DxBLZkbRazSd8eaMNBg5oC
```

### 3.2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

Hoặc:

```bash
pip install PyQt6 psycopg2-binary bcrypt darkdetect python-dotenv supabase
```

### 3.3. Tạo file .env

1. Copy file template:

```bash
cp .env.example .env
```

2. Mở file `.env` và điền thông tin từ Supabase:

```env
# Supabase Configuration
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_DB_PASSWORD=your_strong_password_here

# Database Connection (PostgreSQL)
DB_HOST=db.xxxxxxxxxxxxx.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your_strong_password_here
```

> ⚠️ **Quan trọng**: Thay thế `xxxxxxxxxxxxx` và `your_strong_password_here` bằng giá trị thực tế!

---

## Bước 4: Khởi tạo Database Schema

### Cách 1: Tự động (Khuyến nghị)

Chạy ứng dụng, nó sẽ tự động tạo các bảng:

```bash
python MediManager.py
```

Khi ứng dụng khởi động lần đầu, bạn sẽ thấy:
```
✔ Database and tables created successfully.
✔ Admin account created (username: admin / password: admin)
```

### Cách 2: Thủ công (qua Supabase Dashboard)

1. Vào Supabase Dashboard → **SQL Editor**
2. Mở file `supabase_schema.sql` trên máy local
3. Copy toàn bộ nội dung
4. Paste vào SQL Editor
5. Click **"Run"**

---

## Bước 5: Test kết nối

### 5.1. Chạy ứng dụng

```bash
python MediManager.py
```

### 5.2. Đăng nhập

- **Username**: `admin`
- **Password**: `admin`

### 5.3. Kiểm tra data trên Supabase

1. Vào Supabase Dashboard → **Table Editor**
2. Chọn bảng `staff`
3. Bạn sẽ thấy tài khoản admin đã được tạo

---

## Troubleshooting

### Lỗi: "Database connection failed"

**Nguyên nhân**: File `.env` chưa được cấu hình đúng

**Giải pháp**:
1. Kiểm tra file `.env` có tồn tại không
2. Xác nhận tất cả các giá trị đã được điền
3. Đảm bảo không có khoảng trắng thừa trong `.env`

### Lỗi: "psycopg2 not found"

**Nguyên nhân**: Chưa cài đặt psycopg2

**Giải pháp**:
```bash
pip install psycopg2-binary
```

### Lỗi: "Authentication failed"

**Nguyên nhân**: Password sai

**Giải pháp**:
1. Vào Supabase Dashboard → Settings → Database
2. Click **"Reset database password"**
3. Copy password mới
4. Cập nhật file `.env` với password mới

### Lỗi: "SSL connection required"

**Nguyên nhân**: Supabase yêu cầu SSL

**Giải pháp**: Code đã được update để tự động sử dụng SSL. Nếu vẫn lỗi, update psycopg2:
```bash
pip install --upgrade psycopg2-binary
```

---

## Migration Data từ MySQL cũ (Nếu có)

Nếu bạn có data cũ trong MySQL và muốn migrate sang Supabase:

### 1. Export data từ MySQL

```bash
mysqldump -u root -p medimanager > medimanager_backup.sql
```

### 2. Convert MySQL dump sang PostgreSQL

Sử dụng tool online: https://www.convert-in.com/mysql-to-postgres-convert.htm

Hoặc thủ công:
- Đổi `AUTO_INCREMENT` → `SERIAL`
- Đổi backticks `` ` `` → double quotes `"`
- Đổi `TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP` → trigger functions

### 3. Import vào Supabase

1. Vào SQL Editor trên Supabase
2. Paste converted SQL
3. Run

---

## So sánh MySQL vs Supabase

| Feature | MySQL (Local) | Supabase (Cloud) |
|---------|--------------|------------------|
| Cài đặt | Cần XAMPP/MySQL | Không cần |
| Truy cập | Chỉ local | Anywhere với internet |
| Backup | Thủ công | Tự động |
| Bảo mật | Cơ bản | SSL/TLS + RLS |
| Chi phí | Free | Free (500MB) / Paid |
| Dashboard | phpMyAdmin | Supabase Dashboard |
| Performance | Phụ thuộc máy | Ổn định |

---

## Lợi ích của việc Migration

✅ **Không cần XAMPP**: Không phải cài đặt và quản lý MySQL local

✅ **Cloud-based**: Truy cập database từ bất kỳ đâu

✅ **Tự động backup**: Supabase tự động backup dữ liệu hàng ngày

✅ **Bảo mật**: SSL/TLS encryption, Row Level Security

✅ **Dễ deploy**: Dễ dàng deploy ứng dụng lên production

✅ **Dashboard trực quan**: Quản lý data qua web interface

✅ **Miễn phí**: Free tier đủ cho hầu hết use cases

---

## Câu hỏi thường gặp (FAQ)

### Q: Chi phí sử dụng Supabase?
**A**: Free tier bao gồm:
- 500MB database storage
- 2GB bandwidth/tháng
- 50MB file storage
- Unlimited API requests

### Q: Data có bị mất không nếu dùng Free tier?
**A**: Không. Supabase cam kết dữ liệu luôn được lưu trữ và backup.

### Q: Có thể quay lại MySQL được không?
**A**: Có. Bạn có thể checkout về commit trước đó:
```bash
git checkout 5b119c9
```

### Q: Tốc độ có bị ảnh hưởng không?
**A**: Với Free tier và region xa, latency có thể cao hơn MySQL local một chút (50-200ms). Tuy nhiên, với region gần (Singapore cho VN), tốc độ rất ổn.

### Q: Có thể sử dụng cho production không?
**A**: Có. Nhiều công ty sử dụng Supabase cho production. Nếu cần, có thể nâng cấp lên Pro plan.

---

## Support

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra lại [Troubleshooting](#troubleshooting)
2. Xem Supabase docs: https://supabase.com/docs
3. Tạo issue trên GitHub repo

---

**Tác giả**: Trần Tiến Thạnh
**Version**: 2.0 (Supabase Migration)
**Ngày**: December 2025

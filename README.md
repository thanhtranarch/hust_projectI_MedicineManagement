# HUST_PROJECT-I

# MediManager – Quản lý thuốc và bán hàng

## Tổng quan

**MediManager** là ứng dụng desktop quản lý nhà thuốc được phát triển bằng Python (PyQt6) kết nối với cơ sở dữ liệu Supabase (PostgreSQL Cloud). Hệ thống cho phép:
- Quản lý thông tin thuốc, nhà cung cấp, khách hàng, nhân viên.
- Lập hóa đơn, theo dõi tồn kho.
- Báo cáo thuốc sắp hết hạn, nhật ký hoạt động.
- Phân quyền người dùng, đăng nhập và đăng ký tài khoản.

## Công nghệ sử dụng

| Thành phần        | Công nghệ             |
|-------------------|------------------------|
| Giao diện người dùng | PyQt6 (UI dạng `.ui`) |
| Cơ sở dữ liệu     | Supabase (PostgreSQL Cloud) |
| Database Driver   | psycopg2              |
| Bảo mật mật khẩu  | bcrypt (hash)         |
| Báo cáo & UI nâng cao | PyQt + QTableWidget + QLabel + QTimer |

## Cơ sở dữ liệu

CSDL `medimanager` bao gồm các bảng chính:
- `medicine`, `category`, `supplier`, `stock`, `stock_transaction`
- `invoice`, `invoice_detail`, `customer`
- `staff` (có phân quyền admin, manager, staff), `activity_log`

SQL schema được lưu trong `supabase_schema.sql`.

## Sơ đồ quan hệ các thực thể
https://dbdiagram.io/d/PROJECT-I-MEDICINE-MANAGEMENT-67ef9cc94f7afba184576060?utm_source=dbdiagram_embed&utm_medium=bottom_open

## Cấu trúc thư mục

```
MediManager/
│
├── MediManager.py          # Điểm bắt đầu chương trình
├── app_context.py          # Kết nối CSDL
├── constants.py            # Đường dẫn icon, query mẫu, v.v.
├── utils/
│   └── helpers.py          # Các hàm dùng chung (load_ui, logging)
├── services/
│   ├── db_service.py       # Đóng gói thao tác DB
│   └── report_service.py   # Xuất báo cáo
├── screens/
│   ├── main_window.py
│   ├── auth.py
│   ├── supplier.py
│   ├── customer.py
│   ├── staff.py
│   ├── medicine.py
│   ├── invoice.py
│   └── stock.py
├── ui/                     # Các file .ui
└── icons/                  # Các file icon


```
## 🧾 Các chức năng chính

- **Đăng nhập / Đăng ký** (Phân quyền: admin, manager, staff)
- **Quản lý thuốc**: thêm, sửa, xóa, chi tiết, lọc theo danh mục
- **Quản lý nhà cung cấp**
- **Quản lý khách hàng**
- **Quản lý nhân viên**
- **Hóa đơn**: tạo và theo dõi hóa đơn trong ngày
- **Tồn kho**: theo dõi tồn kho, thuốc sắp hết hạn
- **Lịch sử hoạt động**: log hành động người dùng
- **Báo cáo xuất file (đang phát triển)**: tổng tồn kho, hóa đơn, thuốc sắp hết hạn

---

## 🛠 Cài đặt và chạy

### 1. Cài đặt thư viện cần thiết

```bash
pip install -r requirements.txt
```

Hoặc cài đặt thủ công:

```bash
pip install PyQt6 psycopg2-binary bcrypt darkdetect python-dotenv supabase
```

### 2. Thiết lập Supabase Database

#### Bước 2.1: Tạo Supabase Project

1. Truy cập https://supabase.com và đăng ký/đăng nhập
2. Tạo một project mới
3. Chờ project được khởi tạo (khoảng 2 phút)

#### Bước 2.2: Lấy Database Credentials

1. Vào **Settings** → **Database**
2. Copy các thông tin sau:
   - **Host** (ví dụ: `db.xxxxx.supabase.co`)
   - **Database name** (thường là `postgres`)
   - **Port** (thường là `5432`)
   - **User** (thường là `postgres`)
   - **Password** (password bạn đã đặt khi tạo project)

3. Vào **Settings** → **API** để lấy:
   - **Project URL** (ví dụ: `https://xxxxx.supabase.co`)
   - **Anon/Public Key**

#### Bước 2.3: Cấu hình file .env

1. Copy file `.env.example` thành `.env`:

```bash
cp .env.example .env
```

2. Mở file `.env` và điền thông tin từ Supabase:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
SUPABASE_DB_PASSWORD=your-database-password

DB_HOST=db.your-project-id.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your-database-password
```

#### Bước 2.4: Tạo Database Schema (Tùy chọn)

Ứng dụng sẽ tự động tạo các bảng khi chạy lần đầu. Nếu muốn tạo thủ công:

1. Vào **SQL Editor** trong Supabase Dashboard
2. Copy nội dung từ file `supabase_schema.sql`
3. Paste và chạy SQL script

### 3. Khởi chạy ứng dụng

```bash
python MediManager.py
```

> **Lưu ý:** Đảm bảo file `.env` đã được cấu hình đúng trước khi chạy ứng dụng.

---

## Tài khoản mặc định

- `Username: admin`  
- `Password: admin`  
> Hệ thống sẽ tự động tạo tài khoản admin nếu chưa có.

---

## Đóng gói thành file .exe

Bạn có thể đóng gói ứng dụng thành `.exe` bằng `PyInstaller`.

### Bước 1: Cài đặt PyInstaller

```bash
pip install pyinstaller
```

### Bước 2: Đóng gói ứng dụng

```bash
pyinstaller --noconfirm --windowed --icon=icon/app_icon_dark.ico --add-data "ui;ui" --add-data "icon;icon" main.py
```

### Bước 3: Chạy ứng dụng

File `main.exe` nằm trong thư mục `dist/`. Chạy file này để sử dụng mà không cần Python.

> ⚠️ Đảm bảo đường dẫn `ui/` và `icon/` chính xác. Nếu dùng PySide6 có thể cần bổ sung `--hidden-import`.

---

## Cơ sở dữ liệu - Supabase

Ứng dụng sử dụng **Supabase** (PostgreSQL Cloud) với các bảng chính:
- `medicine`, `supplier`, `stock`
- `invoice`, `invoice_detail`, `customer`
- `staff`, `activity_log`

**SQL schema**: `supabase_schema.sql`

### Lợi ích của Supabase

- ✅ **Cloud-based**: Không cần cài đặt MySQL/XAMPP local
- ✅ **Miễn phí tier**: 500MB database, 2GB bandwidth/tháng
- ✅ **Tự động backup**: Supabase tự động backup dữ liệu
- ✅ **Bảo mật cao**: SSL/TLS encryption, Row Level Security (RLS)
- ✅ **Dễ mở rộng**: Có thể nâng cấp lên Pro khi cần
- ✅ **Dashboard trực quan**: Quản lý database qua web interface

---

## Hướng phát triển tương lai

- Xuất báo cáo định dạng PDF
- Lọc báo cáo theo ngày/tháng/năm
- Tích hợp API / phiên bản mobile
- Giao diện hiện đại hơn

---

## Tác giả

**Trần Tiến Thạnh**  
MSSV: 20239253  
Đại học Bách khoa Hà Nội – Môn: PROJECT I
  



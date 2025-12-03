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
├── run.py                      # Entry point - Điểm bắt đầu chương trình
├── requirements.txt            # Python dependencies
├── .env.example                # Template cấu hình môi trường
├── .gitignore                  # Git ignore rules
│
├── src/                        # Source code
│   ├── config/                 # Configuration management
│   │   ├── settings.py         # Application settings
│   │   └── database.py         # Database configuration
│   │
│   ├── core/                   # Core business logic
│   │   ├── db_manager.py       # Database manager
│   │   └── app_context.py      # Application context
│   │
│   ├── services/               # Business services
│   │   └── report_service.py   # PDF report generation
│   │
│   ├── ui/                     # User interface
│   │   ├── windows/            # Main windows
│   │   ├── dialogs/            # Dialog windows
│   │   └── forms/              # Qt Designer .ui files
│   │
│   └── utils/                  # Utilities
│       ├── helpers.py          # Helper functions
│       └── constants.py        # Application constants
│
├── assets/                     # Static resources
│   ├── icons/                  # Application icons
│   └── fonts/                  # Fonts for PDF
│
├── exports/                    # Generated reports
│
├── docs/                       # Documentation
│   └── ARCHITECTURE.md         # Architecture documentation
│
└── Legacy files (đang refactor):
    ├── MediManager.py          # Main UI code (sẽ được tách)
    ├── DBManager.py            # Database code (đã migrate to src/core/)
    └── export_reports.py       # Report code (đã migrate to src/services/)
```

> **Lưu ý**: Dự án đang trong quá trình refactor từ cấu trúc monolithic sang clean architecture.
> Xem chi tiết tại [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
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
python run.py
```

Hoặc (cách cũ, vẫn hoạt động):

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

## Kiến trúc dự án

Dự án được tổ chức theo **Clean Architecture** với các lớp rõ ràng:

- **Config Layer**: Quản lý cấu hình (settings, database config)
- **Core Layer**: Logic nghiệp vụ cốt lõi (database, app context)
- **Service Layer**: Các dịch vụ nghiệp vụ (reports, auth, ...)
- **UI Layer**: Giao diện người dùng (windows, dialogs)
- **Utils Layer**: Các hàm tiện ích dùng chung

Xem chi tiết tại: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

## Hướng phát triển tương lai

### Version 2.x (In Progress)
- ✅ Migrate sang Supabase PostgreSQL Cloud
- ✅ Tổ chức lại cấu trúc theo Clean Architecture
- ⏳ Refactor UI code thành các module riêng biệt
- ⏳ Tách service layer cho từng nghiệp vụ
- 📝 Thêm unit tests

### Version 3.x (Planned)
- REST API cho mobile app
- Advanced reporting với charts
- Role-based access control (RBAC)
- Real-time notifications
- Barcode scanning
- Multi-language support
- Dark mode UI

---

## Tác giả

**Trần Tiến Thạnh**  
MSSV: 20239253  
Đại học Bách khoa Hà Nội – Môn: PROJECT I
  



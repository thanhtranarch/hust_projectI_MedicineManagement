# MediManager - Hệ Thống Quản Lý Nhà Thuốc

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.4.0+-green.svg)
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

**Ứng dụng desktop quản lý nhà thuốc hiện đại với kiến trúc Clean Architecture**

[Tính năng](#tính-năng-chính) • [Cài đặt](#cài-đặt) • [Sử dụng](#sử-dụng) • [Kiến trúc](#kiến-trúc-hệ-thống) • [Đóng góp](#đóng-góp)

</div>

---

## Mục lục

- [Giới thiệu](#giới-thiệu)
- [Tính năng chính](#tính-năng-chính)
- [Công nghệ sử dụng](#công-nghệ-sử-dụng)
- [Kiến trúc hệ thống](#kiến-trúc-hệ-thống)
- [Cài đặt](#cài-đặt)
- [Sử dụng](#sử-dụng)
- [Cấu trúc thư mục](#cấu-trúc-thư-mục)
- [Cơ sở dữ liệu](#cơ-sở-dữ-liệu)
- [Đóng gói ứng dụng](#đóng-gói-ứng-dụng)
- [Roadmap](#roadmap)
- [Đóng góp](#đóng-góp)
- [Tác giả](#tác-giả)

---

## Giới thiệu

**MediManager** là ứng dụng desktop quản lý nhà thuốc toàn diện, được phát triển với **Python** và **PyQt6**, kết nối với **Supabase PostgreSQL Cloud**. Dự án được xây dựng theo kiến trúc **Clean Architecture**, đảm bảo tính bảo trì, mở rộng và kiểm thử cao.

### Thông tin dự án
- **Môn học**: PROJECT I
- **Trường**: Đại học Bách khoa Hà Nội
- **Phiên bản**: 2.0.0
- **Trạng thái**: Đang phát triển tích cực

---

## Tính năng chính

### Quản lý người dùng
- Đăng nhập / Đăng ký tài khoản
- Phân quyền 3 cấp: **Admin**, **Manager**, **Staff**
- Quản lý thông tin nhân viên
- Theo dõi lịch sử hoạt động người dùng

### Quản lý thuốc
- Thêm, sửa, xóa thông tin thuốc
- Tìm kiếm và lọc thuốc theo danh mục
- Quản lý chi tiết thuốc (thành phần, công dụng, liều lượng)
- Theo dõi ngày sản xuất và hạn sử dụng

### Quản lý tồn kho
- Theo dõi số lượng tồn kho theo thời gian thực
- Cảnh báo thuốc sắp hết hạn
- Cảnh báo thuốc tồn kho thấp
- Quản lý giao dịch nhập/xuất kho
- Lịch sử biến động tồn kho

### Quản lý nhà cung cấp & khách hàng
- Quản lý thông tin nhà cung cấp
- Quản lý thông tin khách hàng
- Theo dõi lịch sử giao dịch

### Quản lý hóa đơn
- Tạo hóa đơn bán hàng
- Quản lý chi tiết hóa đơn
- Theo dõi doanh thu theo ngày
- Tìm kiếm và xem lại hóa đơn cũ

### Báo cáo & Thống kê
- Báo cáo tồn kho
- Báo cáo doanh thu
- Báo cáo thuốc sắp hết hạn
- Xuất báo cáo PDF
- Nhật ký hoạt động hệ thống

---

## Công nghệ sử dụng

### Backend & Database
| Công nghệ | Mô tả | Phiên bản |
|-----------|-------|-----------|
| ![Python](https://img.shields.io/badge/-Python-3776AB?style=flat&logo=python&logoColor=white) | Ngôn ngữ lập trình chính | 3.8+ |
| ![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-336791?style=flat&logo=postgresql&logoColor=white) | Cơ sở dữ liệu quan hệ | 14+ |
| ![Supabase](https://img.shields.io/badge/-Supabase-3ECF8E?style=flat&logo=supabase&logoColor=white) | PostgreSQL Cloud Platform | 2.0+ |
| **psycopg2** | PostgreSQL adapter cho Python | 2.9.9+ |
| **bcrypt** | Mã hóa mật khẩu | 4.0.1+ |

### Frontend & UI
| Công nghệ | Mô tả | Phiên bản |
|-----------|-------|-----------|
| ![PyQt6](https://img.shields.io/badge/-PyQt6-41CD52?style=flat&logo=qt&logoColor=white) | Framework giao diện người dùng | 6.4.0+ |
| **darkdetect** | Tự động phát hiện theme hệ thống | 0.8.0+ |

### Utilities
| Công nghệ | Mô tả |
|-----------|-------|
| **python-dotenv** | Quản lý biến môi trường |
| **Qt Designer** | Thiết kế giao diện .ui |

---

## Kiến trúc hệ thống

MediManager được xây dựng theo **Clean Architecture** với các lớp phân tách rõ ràng:

```
┌─────────────────────────────────────────┐
│      Presentation Layer (UI)            │
│   ┌─────────────┬─────────────┐        │
│   │   Windows   │   Dialogs   │        │
│   └─────────────┴─────────────┘        │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Application Layer (Services)       │
│   ┌───────────────────────────────┐    │
│   │  Business Logic & Services    │    │
│   └───────────────────────────────┘    │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│        Core Layer (Domain)              │
│   ┌─────────────┬─────────────┐        │
│   │  DBManager  │ AppContext  │        │
│   └─────────────┴─────────────┘        │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│       Infrastructure Layer              │
│      (Supabase PostgreSQL Cloud)        │
└─────────────────────────────────────────┘
```

### Lợi ích của Clean Architecture:
- **Tách biệt trách nhiệm**: Mỗi layer có trách nhiệm riêng biệt
- **Dễ bảo trì**: Thay đổi một layer không ảnh hưởng layer khác
- **Dễ kiểm thử**: Có thể test từng layer độc lập
- **Mở rộng**: Dễ dàng thêm tính năng mới
- **Tái sử dụng**: Code có thể tái sử dụng ở nhiều nơi

**Chi tiết kiến trúc**: Xem [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## Cài đặt

### Yêu cầu hệ thống
- **Python**: 3.8 trở lên
- **Hệ điều hành**: Windows 10+, macOS 10.14+, Ubuntu 20.04+
- **RAM**: Tối thiểu 2GB
- **Dung lượng**: ~200MB

### Bước 1: Clone repository

```bash
git clone https://github.com/thanhtranarch/hust_projectI_MedicineManagement.git
cd hust_projectI_MedicineManagement
```

### Bước 2: Cài đặt dependencies

#### Cách 1: Sử dụng requirements.txt (Khuyến nghị)
```bash
pip install -r requirements.txt
```

#### Cách 2: Cài đặt thủ công
```bash
pip install PyQt6>=6.4.0 psycopg2-binary>=2.9.9 bcrypt>=4.0.1 \
            darkdetect>=0.8.0 python-dotenv>=1.0.0 supabase>=2.0.0
```

### Bước 3: Thiết lập Supabase Database

#### 3.1. Tạo Supabase Project

1. Truy cập [https://supabase.com](https://supabase.com)
2. Đăng ký/đăng nhập tài khoản
3. Click **"New Project"**
4. Điền thông tin:
   - **Project Name**: `medimanager`
   - **Database Password**: Tạo password mạnh (lưu lại để dùng sau)
   - **Region**: Chọn gần nhất (ví dụ: Singapore)
5. Click **"Create new project"** và chờ ~2 phút

#### 3.2. Lấy Database Credentials

**Lấy Database Connection String:**
1. Vào **Settings** → **Database**
2. Cuộn xuống **Connection Info**
3. Copy các thông tin sau:
   - **Host**: `db.xxxxxxxxxxxxx.supabase.co`
   - **Database name**: `postgres`
   - **Port**: `5432`
   - **User**: `postgres`
   - **Password**: Password bạn đã tạo ở bước 3.1

**Lấy API Keys:**
1. Vào **Settings** → **API**
2. Copy:
   - **Project URL**: `https://xxxxxxxxxxxxx.supabase.co`
   - **anon/public key**: `eyJhbGc...`

#### 3.3. Cấu hình Environment Variables

1. Copy file template:
```bash
cp .env.example .env
```

2. Mở file `.env` và điền thông tin:
```env
# Supabase API Configuration
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGc...your-anon-key...

# Database Configuration
DB_HOST=db.xxxxxxxxxxxxx.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your-database-password
```

#### 3.4. Khởi tạo Database Schema

**Tự động** (Khuyến nghị):
- Ứng dụng sẽ tự động tạo bảng khi chạy lần đầu

**Thủ công**:
1. Vào **SQL Editor** trong Supabase Dashboard
2. Copy nội dung file `supabase_schema.sql`
3. Paste vào SQL Editor và click **"Run"**

---

## Sử dụng

### Khởi chạy ứng dụng

#### Cách 1: Sử dụng entry point mới (Khuyến nghị)
```bash
python run.py
```

#### Cách 2: Sử dụng file legacy
```bash
python MediManager.py
```

### Đăng nhập lần đầu

Hệ thống tự động tạo tài khoản admin nếu chưa có:

```
Username: admin
Password: admin
```

> **Lưu ý bảo mật**: Đổi mật khẩu admin ngay sau lần đăng nhập đầu tiên!

### Giao diện chính

Sau khi đăng nhập, bạn sẽ thấy Dashboard với các module:

```
┌─────────────────────────────────────────┐
│          MediManager Dashboard           │
├─────────────────────────────────────────┤
│  Dashboard  │  Thuốc      │  Kho        │
│  Khách hàng │  Hóa đơn    │  Nhân viên  │
│  Báo cáo    │  Nhật ký    │  Cài đặt   │
└─────────────────────────────────────────┘
```

---

## Cấu trúc thư mục

```
MediManager/
│
├── run.py                       # Entry point chính
├── requirements.txt             # Python dependencies
├── .env.example                 # Template cấu hình
├── .gitignore                   # Git ignore rules
├── supabase_schema.sql          # Database schema
│
├── src/                         # Source code
│   ├── config/                  # Quản lý cấu hình
│   │   ├── settings.py          # Cài đặt ứng dụng
│   │   └── database.py          # Cấu hình database
│   │
│   ├── core/                    # Core business logic
│   │   ├── db_manager.py        # Database manager (DAO)
│   │   └── app_context.py       # Application context
│   │
│   ├── services/                # Business services
│   │   └── report_service.py    # Tạo báo cáo PDF
│   │
│   ├── ui/                      # Giao diện người dùng
│   │   ├── windows/             # Main windows
│   │   │   ├── main_window.py
│   │   │   ├── medicine_window.py
│   │   │   ├── invoice_window.py
│   │   │   ├── stock_window.py
│   │   │   ├── customer_window.py
│   │   │   ├── supplier_window.py
│   │   │   ├── staff_window.py
│   │   │   └── logs_window.py
│   │   │
│   │   ├── dialogs/             # Dialog windows
│   │   │   ├── login_dialog.py
│   │   │   ├── register_dialog.py
│   │   │   ├── medicine_information_dialog.py
│   │   │   ├── medicine_add_dialog.py
│   │   │   ├── create_invoice_dialog.py
│   │   │   ├── create_stock_dialog.py
│   │   │   ├── customer_information_dialog.py
│   │   │   ├── supplier_information_dialog.py
│   │   │   ├── staff_information_dialog.py
│   │   │   └── report_dialog.py
│   │   │
│   │   ├── forms/               # Qt Designer .ui files
│   │   └── base/                # Base classes
│   │       ├── base_window.py
│   │       └── base_dialog.py
│   │
│   └── utils/                   # Utilities
│       ├── helpers.py           # Helper functions
│       └── constants.py         # Application constants
│
├── assets/                      # Static resources
│   ├── icons/                   # Application icons
│   └── fonts/                   # Fonts for PDF
│
├── exports/                     # Generated reports
├── docs/                        # Documentation
│   └── ARCHITECTURE.md
│
└── Legacy files/                # (Đang refactor)
    ├── MediManager.py          # Main UI cũ
    ├── DBManager.py            # Database code cũ
    └── export_reports.py       # Report code cũ
```

---

## Cơ sở dữ liệu

### Database: Supabase PostgreSQL Cloud

**Sơ đồ quan hệ**: [Xem trên dbdiagram.io](https://dbdiagram.io/d/PROJECT-I-MEDICINE-MANAGEMENT-67ef9cc94f7afba184576060)

### Bảng chính

| Bảng | Mô tả | Số cột |
|------|-------|--------|
| `staff` | Thông tin nhân viên & tài khoản | 8 |
| `medicine` | Thông tin thuốc | 12 |
| `category` | Danh mục thuốc | 3 |
| `supplier` | Nhà cung cấp | 6 |
| `customer` | Khách hàng | 6 |
| `invoice` | Hóa đơn | 7 |
| `invoice_detail` | Chi tiết hóa đơn | 6 |
| `stock` | Tồn kho | 7 |
| `stock_transaction` | Biến động kho | 6 |
| `activity_log` | Nhật ký hoạt động | 6 |

### Mối quan hệ chính

```sql
staff (1) ──< (N) invoice
customer (1) ──< (N) invoice
invoice (1) ──< (N) invoice_detail
medicine (1) ──< (N) invoice_detail
medicine (1) ──< (N) stock
supplier (1) ──< (N) stock
medicine (1) ──< (N) stock_transaction
staff (1) ──< (N) activity_log
```

### Lợi ích Supabase

| Tính năng | Mô tả |
|-----------|-------|
| **Cloud-based** | Không cần cài MySQL/PostgreSQL local |
| **Free tier** | 500MB database, 2GB bandwidth/tháng |
| **Auto backup** | Tự động backup dữ liệu định kỳ |
| **Bảo mật cao** | SSL/TLS encryption, Row Level Security |
| **Scalable** | Dễ dàng nâng cấp khi cần |
| **Dashboard** | Quản lý database qua web interface |
| **Realtime** | Hỗ trợ realtime subscriptions |

---

## Đóng gói ứng dụng

### Tạo file executable (.exe) với PyInstaller

#### Bước 1: Cài đặt PyInstaller

```bash
pip install pyinstaller
```

#### Bước 2: Build ứng dụng

**Windows:**
```bash
pyinstaller --noconfirm --windowed \
    --icon=MediManager.ico \
    --add-data "ui;ui" \
    --add-data "assets;assets" \
    --add-data ".env;." \
    run.py
```

**macOS/Linux:**
```bash
pyinstaller --noconfirm --windowed \
    --icon=MediManager.ico \
    --add-data "ui:ui" \
    --add-data "assets:assets" \
    --add-data ".env:." \
    run.py
```

#### Bước 3: Tìm file thực thi

File executable sẽ nằm trong:
```
dist/run/run.exe      (Windows)
dist/run/run          (macOS/Linux)
```

#### Bước 4: Phân phối

1. Copy thư mục `dist/run/` sang máy khác
2. Đảm bảo file `.env` đã được cấu hình đúng
3. Chạy file `run.exe` (Windows) hoặc `run` (macOS/Linux)

> **Lưu ý**: Đảm bảo file `.env` không chứa thông tin nhạy cảm khi phân phối

---

## Roadmap

### Version 1.0 (Completed)
- [x] Giao diện cơ bản với PyQt6
- [x] Quản lý thuốc, khách hàng, nhà cung cấp
- [x] Hóa đơn và tồn kho cơ bản
- [x] Database MySQL local

### Version 2.0 (Current)
- [x] Migrate sang Supabase PostgreSQL Cloud
- [x] Refactor theo Clean Architecture
- [x] Tách UI thành các module riêng
- [x] Service layer cho business logic
- [ ] Hoàn thiện tất cả UI windows/dialogs (In Progress)
- [ ] Thêm unit tests (Planned)

### Version 3.0 (Future)
- **Mobile App**: Flutter app kết nối API
- **Advanced RBAC**: Phân quyền chi tiết hơn
- **Analytics Dashboard**: Biểu đồ và thống kê nâng cao
- **Notifications**: Thông báo realtime
- **Barcode Scanner**: Quét mã vạch thuốc
- **Multi-language**: Tiếng Việt & English
- **Dark Mode**: Giao diện tối
- **Export Excel**: Xuất báo cáo Excel
- **Sync**: Đồng bộ offline-online
- **AI**: Gợi ý thuốc dựa trên triệu chứng

### Version 4.0 (Vision)
- **Web App**: Progressive Web App (PWA)
- **Microservices**: Tách backend thành microservices
- **Docker**: Containerization
- **Redis Cache**: Caching layer
- **GraphQL API**: Alternative to REST
- **Elasticsearch**: Advanced search
- **Big Data**: Analytics với Apache Spark
- **Integration**: Kết nối hệ thống kế toán, ERP

---

## Đóng góp

Mọi đóng góp đều được chào đón! Dự án này đang trong giai đoạn phát triển tích cực.

### Cách đóng góp

1. **Fork** repository
2. Tạo **feature branch**:
   ```bash
   git checkout -b feature/TinhNangMoi
   ```
3. **Commit** thay đổi:
   ```bash
   git commit -m "Add: Thêm tính năng mới"
   ```
4. **Push** lên branch:
   ```bash
   git push origin feature/TinhNangMoi
   ```
5. Tạo **Pull Request**

### Coding Guidelines

- Tuân thủ **PEP 8** style guide
- Thêm **docstrings** cho functions/classes
- Viết **type hints** cho parameters
- Thêm **unit tests** cho code mới
- Cập nhật **documentation** khi cần

### Issues & Bugs

Nếu bạn tìm thấy bug hoặc có đề xuất tính năng:
1. Kiểm tra [Issues](https://github.com/thanhtranarch/hust_projectI_MedicineManagement/issues) hiện tại
2. Tạo issue mới với template phù hợp
3. Mô tả chi tiết vấn đề/tính năng

---

## License

Dự án này được phát hành dưới **MIT License**.

```
MIT License

Copyright (c) 2024 Trần Tiến Thạnh

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## Tác giả

<div align="center">

### **Trần Tiến Thạnh**

MSSV: **20239253**
Trường: **Đại học Bách khoa Hà Nội**
Môn học: **PROJECT I**

[![GitHub](https://img.shields.io/badge/GitHub-thanhtranarch-181717?style=for-the-badge&logo=github)](https://github.com/thanhtranarch)
[![Email](https://img.shields.io/badge/Email-Contact-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:thanh.tt239253@sis.hust.edu.vn)

</div>

---

## Cảm ơn

Xin cảm ơn:
- **Supabase Team** - Cloud PostgreSQL platform tuyệt vời
- **Riverbank Computing** - PyQt6 framework
- **Giảng viên môn PROJECT I** - Hướng dẫn và hỗ trợ
- **Cộng đồng Python Việt Nam** - Nguồn cảm hứng và kiến thức

---

<div align="center">

**Nếu bạn thấy dự án hữu ích, hãy cho một Star nhé!**

Made with by [Trần Tiến Thạnh](https://github.com/thanhtranarch)

</div>

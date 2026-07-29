# MediManager - Hệ Thống Quản Lý Nhà Thuốc

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.4.0+-green.svg)
![SQLite](https://img.shields.io/badge/SQLite-built--in-003B57.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supabase-orange.svg)
![Tests](https://img.shields.io/badge/Tests-167%20passing-brightgreen.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**Ứng dụng desktop quản lý nhà thuốc: quản lý thuốc, kiểm soát tồn kho, bán hàng và báo cáo doanh thu**

[Bắt đầu nhanh](#bắt-đầu-nhanh) • [Tính năng](#tính-năng) • [Cài đặt](#cài-đặt) • [Kiến trúc](#kiến-trúc-hệ-thống) • [Kiểm thử](#kiểm-thử)

</div>

---

## Mục lục

- [Giới thiệu](#giới-thiệu)
- [Bắt đầu nhanh](#bắt-đầu-nhanh)
- [Tính năng](#tính-năng)
- [Công nghệ sử dụng](#công-nghệ-sử-dụng)
- [Cài đặt](#cài-đặt)
  - [Chế độ SQLite (mặc định)](#chế-độ-sqlite-mặc-định)
  - [Chế độ PostgreSQL / Supabase](#chế-độ-postgresql--supabase)
- [Sử dụng](#sử-dụng)
- [Dữ liệu mẫu](#dữ-liệu-mẫu)
- [Kiến trúc hệ thống](#kiến-trúc-hệ-thống)
- [Cấu trúc thư mục](#cấu-trúc-thư-mục)
- [Cơ sở dữ liệu](#cơ-sở-dữ-liệu)
- [Báo cáo](#báo-cáo)
- [Kiểm thử](#kiểm-thử)
- [Đóng gói ứng dụng](#đóng-gói-ứng-dụng)
- [Xử lý sự cố](#xử-lý-sự-cố)
- [Roadmap](#roadmap)
- [Đóng góp](#đóng-góp)
- [License](#license)
- [Tác giả](#tác-giả)

---

## Giới thiệu

**MediManager** là ứng dụng desktop quản lý nhà thuốc được phát triển bằng **Python** và **PyQt6**,
sử dụng **cơ sở dữ liệu quan hệ** để quản lý thông tin thuốc, kiểm soát tồn kho,
hỗ trợ bán hàng và xuất báo cáo doanh thu.

Hệ thống giúp nhà thuốc theo dõi số lượng thuốc, hạn sử dụng, lịch sử bán hàng và doanh thu,
đồng thời hỗ trợ các thao tác tìm kiếm thuốc, nhập - xuất kho, quản lý thông tin khách hàng
và nhà cung cấp.

### Thông tin dự án

| | |
|---|---|
| **Môn học** | PROJECT I |
| **Trường** | Đại học Bách khoa Hà Nội |
| **Phiên bản** | 2.0.0 |
| **Kiến trúc** | Clean Architecture (phân tách UI / Service / Core) |
| **Cơ sở dữ liệu** | SQLite (mặc định) hoặc PostgreSQL / Supabase |

---

## Bắt đầu nhanh

Chạy được ngay với 3 lệnh, **không cần cấu hình gì thêm**:

```bash
pip install -r requirements.txt
python seed_demo_data.py      # tùy chọn: nạp dữ liệu mẫu để xem thử
python run.py
```

Đăng nhập bằng `admin` / `admin`.

Mặc định ứng dụng dùng SQLite, tự tạo file `data/medimanager.db` và toàn bộ bảng
ở lần chạy đầu tiên. Muốn dùng PostgreSQL/Supabase thì xem
[phần cấu hình bên dưới](#chế-độ-postgresql--supabase).

---

## Tính năng

### Quản lý người dùng
- Đăng nhập / đăng ký tài khoản nhân viên
- Mật khẩu được mã hóa bằng **bcrypt**; tài khoản cũ lưu mật khẩu dạng thô sẽ được
  tự động nâng cấp sang bcrypt ở lần đăng nhập kế tiếp
- Phân quyền 3 cấp: **admin**, **manager**, **staff**
- Nhật ký hoạt động (activity log) ghi lại thao tác của từng nhân viên

### Quản lý thuốc
- Thêm, sửa, xóa thông tin thuốc
- Tìm kiếm thuốc theo tên ngay trên bảng danh sách
- Phân loại theo danh mục (thuốc giảm đau, kháng sinh, vitamin, dụng cụ y tế...)
- Theo dõi hoạt chất, thương hiệu, đơn vị tính, số lô, giá nhập và giá bán

### Quản lý tồn kho
- Theo dõi số lượng tồn kho theo thời gian thực
- **Phiếu nhập kho** gồm phần đầu (nhà cung cấp, nhân viên, hình thức thanh toán)
  và các dòng chi tiết từng loại thuốc
- Nhập kho tự động cộng tồn và cập nhật giá; bán hàng tự động trừ tồn
- **Cảnh báo hạn sử dụng** trên màn hình chính, phân mức:
  - `!` còn ≤ 30 ngày
  - `⚠` còn ≤ 60 ngày

### Quản lý nhà cung cấp & khách hàng
- Quản lý thông tin nhà cung cấp và điều khoản thanh toán
- Quản lý khách hàng, tra cứu nhanh theo số điện thoại
- Tự động tạo khách hàng mới ngay trong lúc lập hóa đơn

### Bán hàng & hóa đơn
- Lập hóa đơn bán hàng với nhiều mặt hàng
- Chỉ cho phép bán thuốc còn tồn kho, kiểm tra số lượng trước khi thêm vào giỏ
- Hóa đơn, chi tiết hóa đơn và việc trừ tồn kho nằm trong **cùng một giao dịch**
- Xem lại hóa đơn cũ kèm chi tiết từng dòng

### Báo cáo & thống kê
- Báo cáo **tồn kho** (kèm tổng giá trị tồn)
- Báo cáo **doanh thu** theo khoảng thời gian, kèm doanh thu theo ngày và thuốc bán chạy
- Báo cáo **hóa đơn** theo ngày
- Báo cáo **thuốc sắp hết hạn** với ngưỡng cảnh báo tùy chỉnh
- Toàn bộ báo cáo xuất ra **PDF tiếng Việt có dấu**

---

## Công nghệ sử dụng

### Ứng dụng
| Công nghệ | Vai trò | Phiên bản |
|-----------|---------|-----------|
| **Python** | Ngôn ngữ lập trình chính | 3.8+ |
| **PyQt6** | Framework giao diện người dùng | 6.4.0+ |
| **Qt Designer** | Thiết kế giao diện dạng `.ui` | — |
| **bcrypt** | Mã hóa mật khẩu | 4.0.1+ |
| **reportlab** | Sinh báo cáo PDF | 4.0.0+ |
| **darkdetect** | Nhận diện theme sáng/tối của hệ thống | 0.8.0+ |
| **python-dotenv** | Đọc cấu hình từ file `.env` | 1.0.0+ |

### Cơ sở dữ liệu
| Công nghệ | Vai trò |
|-----------|---------|
| **SQLite** | Backend mặc định, có sẵn trong Python, không cần cài đặt |
| **PostgreSQL / Supabase** | Backend cho môi trường nhiều máy trạm |
| **psycopg2-binary** | Driver PostgreSQL (chỉ cần khi dùng PostgreSQL) |

### Kiểm thử
| Công nghệ | Vai trò |
|-----------|---------|
| **pytest** | Bộ khung kiểm thử |
| **Qt offscreen** | Chạy kiểm thử giao diện không cần màn hình |

---

## Cài đặt

### Yêu cầu hệ thống
- **Python**: 3.8 trở lên
- **Hệ điều hành**: Windows 10+, macOS 10.14+, Ubuntu 20.04+
- **RAM**: tối thiểu 2GB
- **Dung lượng**: ~200MB

### Bước 1: Tải mã nguồn

```bash
git clone https://github.com/thanhtranarch/hust_projectI_MedicineManagement.git
cd hust_projectI_MedicineManagement
```

### Bước 2: Cài đặt thư viện

```bash
pip install -r requirements.txt
```

> Trên Linux, PyQt6 cần thêm một vài thư viện hệ thống:
> ```bash
> sudo apt install libegl1 libgl1 libxkbcommon-x11-0 libdbus-1-3 libfontconfig1
> ```

### Bước 3: Chọn cơ sở dữ liệu

Ứng dụng **tự động chọn backend**:

| Điều kiện | Backend được dùng |
|-----------|-------------------|
| Không có `.env`, hoặc thiếu `DB_HOST` / `DB_PASSWORD` | **SQLite** |
| Có đủ `DB_HOST` và `DB_PASSWORD` | **PostgreSQL** |
| Đặt `DB_BACKEND=sqlite` hoặc `DB_BACKEND=postgres` | Theo giá trị chỉ định |

#### Chế độ SQLite (mặc định)

Không cần làm gì cả. Chạy `python run.py` là xong — ứng dụng tự tạo
`data/medimanager.db` cùng toàn bộ bảng và tài khoản `admin`.

Muốn đổi vị trí file database:

```env
SQLITE_PATH=duong/dan/toi/medimanager.db
```

#### Chế độ PostgreSQL / Supabase

**1. Tạo project Supabase**

1. Truy cập [supabase.com](https://supabase.com) và đăng nhập
2. Chọn **New Project**, đặt tên `medimanager`, tạo **Database Password** và chọn
   region gần nhất (ví dụ Singapore)
3. Chờ khoảng 2 phút để project khởi tạo

**2. Lấy thông tin kết nối**

Vào **Settings → Database → Connection Info** và ghi lại `Host`, `Port`,
`Database name`, `User`. Mật khẩu là mật khẩu bạn tạo ở bước 1.

**3. Tạo file `.env`**

```bash
cp .env.example .env
```

Điền vào `.env`:

```env
DB_BACKEND=postgres
DB_HOST=db.xxxxxxxxxxxxx.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=mat-khau-cua-ban
```

**4. Tạo bảng**

- **Tự động** (khuyến nghị): ứng dụng tự tạo toàn bộ bảng ở lần chạy đầu tiên.
- **Thủ công**: mở **SQL Editor** trên Supabase, dán nội dung `supabase_schema.sql` rồi **Run**.

> Nếu bạn đã có database tạo từ phiên bản cũ, ứng dụng sẽ **tự động bổ sung** các
> cột mới (`stock.staff_id`, `stock.payment_method_id`, `invoice.payment_method_id`,
> `payment_method.method_type`, `medicine.unit`) mà không làm mất dữ liệu hiện có.

---

## Sử dụng

### Khởi chạy

```bash
python run.py
```

Khi khởi động, ứng dụng in ra backend đang dùng:

```
============================================================
  MediManager v2.0.0
  Trần Tiến Thạnh
============================================================
Database: SQLite /home/user/hust_projectI_MedicineManagement/data/medimanager.db
Connected to database.
```

### Đăng nhập lần đầu

```
Username: admin
Password: admin
```

> **Lưu ý bảo mật**: đổi mật khẩu admin ngay sau lần đăng nhập đầu tiên.

### Luồng nghiệp vụ chính

```
Nhà cung cấp  ──►  Nhập kho  ──►  Tồn kho  ──►  Bán hàng  ──►  Hóa đơn
                  (stock +          (medicine.      (trừ tồn)      │
                   stock_detail)   stock_quantity)                 ▼
                                          │                    Báo cáo
                                          ▼                   doanh thu
                                  Cảnh báo hạn dùng
```

1. **Nhà cung cấp** — thêm nhà cung cấp trước khi nhập hàng
2. **Nhập kho** — tạo phiếu nhập, chọn nhà cung cấp và thêm từng dòng thuốc.
   Thuốc chưa có trong hệ thống sẽ được tạo mới; thuốc đã có (trùng tên và số lô)
   sẽ được cộng dồn tồn kho và cập nhật giá
3. **Bán hàng** — từ màn hình chính chọn **Tạo hóa đơn**, nhập số điện thoại
   khách hàng, thêm thuốc và lưu. Tồn kho tự động giảm
4. **Báo cáo** — nhấn **In báo cáo ngày** để chọn loại báo cáo và xuất PDF

---

## Dữ liệu mẫu

Để xem thử ứng dụng với dữ liệu thật, dùng script nạp dữ liệu mẫu:

```bash
python seed_demo_data.py                # nạp dữ liệu mẫu
python seed_demo_data.py --reset        # xóa dữ liệu cũ rồi nạp lại
python seed_demo_data.py --days 90      # sinh 90 ngày lịch sử bán hàng
```

Script tạo ra:

- 3 tài khoản nhân viên (mật khẩu `matkhau123`)
- 4 nhà cung cấp, 5 khách hàng
- 14 loại thuốc thuộc nhiều danh mục, trong đó có vài loại sắp hết hạn
  để thấy được cảnh báo
- Các phiếu nhập kho và khoảng 30 ngày lịch sử bán hàng

Dữ liệu tham chiếu (danh mục, hình thức thanh toán) và tài khoản `admin`
luôn được giữ nguyên.

---

## Kiến trúc hệ thống

Dự án tổ chức theo **Clean Architecture**, tách bạch giao diện, nghiệp vụ và truy cập dữ liệu:

```
┌──────────────────────────────────────────────────────┐
│  Presentation Layer — src/ui/                        │
│  windows/ · dialogs/ · forms/ (.ui) · base/          │
└───────────────────────┬──────────────────────────────┘
                        │
┌───────────────────────▼──────────────────────────────┐
│  Service Layer — src/services/                       │
│  AuthService · ReportService                         │
└───────────────────────┬──────────────────────────────┘
                        │
┌───────────────────────▼──────────────────────────────┐
│  Core Layer — src/core/                              │
│  AppContext · DBManager · SqlDialect · schema        │
└───────────────────────┬──────────────────────────────┘
                        │
┌───────────────────────▼──────────────────────────────┐
│  Infrastructure                                      │
│  SQLite  ·  PostgreSQL / Supabase                    │
└──────────────────────────────────────────────────────┘
```

### Các thành phần chính

| Thành phần | Trách nhiệm |
|------------|-------------|
| `AppContext` | Giữ kết nối database và phiên đăng nhập, truyền xuống mọi màn hình |
| `DBManager` | Mở kết nối, thực thi truy vấn, quản lý giao dịch, tạo bảng và migration |
| `SqlDialect` | Che giấu khác biệt SQL giữa SQLite và PostgreSQL |
| `schema.py` | **Nguồn định nghĩa duy nhất** của lược đồ dữ liệu |
| `AuthService` | Xác thực, băm mật khẩu, đăng ký tài khoản |
| `ReportService` | Sinh báo cáo PDF |
| `BaseWindow` / `BaseDialog` | Nạp file `.ui`, đặt icon, hộp thoại thông báo dùng chung |

### Hỗ trợ hai backend

Mã nghiệp vụ chỉ viết SQL một lần. `DBManager` xử lý phần khác biệt:

| Khác biệt | PostgreSQL | SQLite |
|-----------|-----------|--------|
| Tham số truy vấn | `%s` | `?` (tự động chuyển đổi) |
| Khóa chính tự tăng | `SERIAL PRIMARY KEY` | `INTEGER PRIMARY KEY AUTOINCREMENT` |
| ID vừa thêm | `SELECT lastval()` | `cursor.lastrowid` |
| Ngày hôm nay | `CURRENT_DATE` | `date('now','localtime')` |
| Số ngày còn lại | `col::date - CURRENT_DATE` | `julianday(...) - julianday(...)` |

Nhờ đó việc chuyển giữa máy cá nhân (SQLite) và môi trường nhiều máy trạm
(PostgreSQL) không cần sửa một dòng mã nghiệp vụ nào.

Chi tiết đầy đủ: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

---

## Cấu trúc thư mục

```
hust_projectI_MedicineManagement/
│
├── run.py                        # Entry point của ứng dụng
├── seed_demo_data.py             # Script nạp dữ liệu mẫu
├── supabase_schema.sql           # Lược đồ PostgreSQL (sinh từ src/core/schema.py)
├── requirements.txt              # Thư viện cho ứng dụng
├── requirements-dev.txt          # Thư viện cho phát triển & kiểm thử
├── pytest.ini                    # Cấu hình pytest
├── .env.example                  # Mẫu cấu hình
│
├── src/
│   ├── config/
│   │   ├── database.py           # Chọn backend, tham số kết nối
│   │   └── settings.py           # Đường dẫn, hằng số ứng dụng
│   │
│   ├── core/
│   │   ├── app_context.py        # Kết nối database + phiên đăng nhập
│   │   ├── db_manager.py         # Thực thi truy vấn, giao dịch, migration
│   │   └── schema.py             # Định nghĩa lược đồ (nguồn duy nhất)
│   │
│   ├── services/
│   │   ├── auth_service.py       # Đăng nhập, đăng ký, mã hóa mật khẩu
│   │   └── report_service.py     # Sinh báo cáo PDF
│   │
│   ├── ui/
│   │   ├── base/                 # BaseWindow, BaseDialog
│   │   ├── windows/              # 8 màn hình chính
│   │   ├── dialogs/              # 12 hộp thoại
│   │   └── forms/                # File giao diện .ui của Qt Designer
│   │
│   └── utils/
│       ├── constants.py          # Hằng số dùng chung, thông báo
│       └── helpers.py            # Định dạng tiền tệ, ngày tháng, kiểm tra dữ liệu
│
├── tests/                        # Bộ kiểm thử (167 test case)
│   ├── conftest.py               # Fixture dùng chung
│   ├── factories.py              # Hàm tạo dữ liệu kiểm thử
│   ├── test_database.py          # Lược đồ, migration, giao dịch
│   ├── test_auth.py              # Đăng nhập, đăng ký, nâng cấp mật khẩu
│   ├── test_workflows.py         # Nhập kho, bán hàng, cảnh báo hạn, doanh thu
│   ├── test_reports.py           # Sinh báo cáo PDF
│   ├── test_ui.py                # Kiểm thử giao diện headless
│   ├── test_postgres.py          # Kiểm thử riêng cho PostgreSQL
│   └── test_helpers.py           # Hàm tiện ích và cấu hình
│
├── assets/
│   ├── fonts/arial.ttf           # Font Unicode cho báo cáo tiếng Việt
│   └── icons/                    # Icon ứng dụng
│
├── docs/ARCHITECTURE.md          # Tài liệu kiến trúc chi tiết
│
├── data/                         # Database SQLite (tự tạo, không commit)
└── exports/                      # Báo cáo PDF xuất ra (tự tạo, không commit)
```

---

## Cơ sở dữ liệu

### Sơ đồ quan hệ

```
   supplier ──┬──────────────► medicine ◄────────── category
              │                 │    ▲
              │                 │    │
              ▼                 │    │
   staff ──► stock ──► stock_detail  │
     │         ▲                     │
     │         │                     │
     │    payment_method             │
     │         │                     │
     ▼         ▼                     │
   invoice ────┴──► invoice_detail ──┘
     ▲
     │
  customer

   staff ──► activity_log
```

### Danh sách bảng

| Bảng | Mô tả |
|------|-------|
| `staff` | Tài khoản nhân viên, chức vụ, lương, mật khẩu đã băm |
| `category` | Danh mục thuốc *(có sẵn 9 danh mục)* |
| `payment_method` | Hình thức thanh toán, phân loại `purchase` / `sale` |
| `supplier` | Nhà cung cấp và điều khoản thanh toán |
| `customer` | Khách hàng |
| `medicine` | Thông tin thuốc, giá, tồn kho, hạn dùng, số lô |
| `stock` | Phần đầu phiếu nhập kho (nhà cung cấp, nhân viên, thanh toán) |
| `stock_detail` | Chi tiết từng dòng thuốc trong phiếu nhập |
| `invoice` | Hóa đơn bán hàng |
| `invoice_detail` | Chi tiết từng dòng thuốc trong hóa đơn |
| `activity_log` | Nhật ký thao tác của nhân viên |

### Dữ liệu tham chiếu có sẵn

**Hình thức thanh toán** — cột `method_type` phân biệt rõ hai nghiệp vụ:

| Tên | Loại | Dùng khi |
|-----|------|----------|
| COD | `purchase` | Nhập kho |
| prepayment | `purchase` | Nhập kho |
| Tiền mặt | `sale` | Bán hàng |
| Chuyển khoản | `sale` | Bán hàng |

**Danh mục thuốc**: Thuốc giảm đau · Thuốc kháng sinh · Thuốc kháng viêm ·
Vitamin & Khoáng chất · Thuốc tiêu hóa · Thuốc hô hấp · Thuốc tim mạch ·
Dụng cụ y tế · Khác

### Thay đổi lược đồ

`src/core/schema.py` là **nguồn định nghĩa duy nhất**. Khi cần thêm bảng hoặc cột:

1. Sửa `TABLES` (bảng mới) hoặc thêm mục vào `MIGRATIONS` (cột mới trên bảng cũ)
2. Cập nhật `supabase_schema.sql` cho khớp
3. Chạy `pytest tests/test_database.py` để kiểm tra

Cách làm này giữ cho SQLite và PostgreSQL luôn đồng bộ, và các database đã triển khai
trước đó vẫn được cập nhật cột mới mà không mất dữ liệu.

---

## Báo cáo

Từ màn hình chính, nhấn **In báo cáo ngày** để mở hộp thoại xuất báo cáo.

| Báo cáo | Nội dung | Tham số |
|---------|----------|---------|
| **Tồn kho** | Danh sách thuốc, số lượng, giá bán, tổng giá trị tồn | — |
| **Doanh thu** | Tổng doanh thu, số hóa đơn, giá trị trung bình, doanh thu theo ngày, thuốc bán chạy | Từ ngày → đến ngày |
| **Hóa đơn** | Toàn bộ hóa đơn trong một ngày kèm tổng doanh thu | Ngày |
| **Thuốc sắp hết hạn** | Thuốc còn hạn dưới ngưỡng cảnh báo, sắp xếp theo hạn gần nhất | Số ngày cảnh báo |

Báo cáo được lưu vào thư mục `exports/` dưới dạng PDF và ghi nhận vào nhật ký hoạt động.
Font `assets/fonts/arial.ttf` đảm bảo tiếng Việt hiển thị đúng dấu; nếu thiếu font,
hệ thống tự chuyển sang Helvetica thay vì báo lỗi.

---

## Kiểm thử

Bộ kiểm thử gồm **167 test case**, chạy hoàn toàn offline trên SQLite tạm thời
nên không ảnh hưởng tới dữ liệu thật.

```bash
pip install -r requirements-dev.txt
pytest
```

Kết quả mong đợi:

```
167 passed
```

### Chạy theo nhóm

```bash
pytest tests/test_workflows.py     # nghiệp vụ nhập kho, bán hàng, doanh thu
pytest tests/test_auth.py          # đăng nhập, đăng ký
pytest tests/test_ui.py            # giao diện (headless)
pytest -k expiry                   # lọc theo tên test
pytest -v                          # xem chi tiết từng test
```

### Phạm vi kiểm thử

| Tệp | Nội dung kiểm thử |
|-----|-------------------|
| `test_database.py` | Tạo bảng, migration, giao dịch, dữ liệu tham chiếu, dialect SQL |
| `test_auth.py` | Đăng nhập đúng/sai, nâng cấp mật khẩu cũ sang bcrypt, ràng buộc đăng ký |
| `test_workflows.py` | Nhập kho cộng tồn, bán hàng trừ tồn, tổng tiền hóa đơn, cảnh báo hạn dùng, tổng hợp doanh thu |
| `test_reports.py` | Sinh đủ 4 loại PDF, hoạt động cả khi database rỗng, định dạng số liệu |
| `test_ui.py` | Mở toàn bộ 8 màn hình và 12 hộp thoại, kiểm tra cột bảng khớp tiêu đề |
| `test_helpers.py` | Định dạng tiền tệ/ngày tháng, kiểm tra email/điện thoại, chọn backend |
| `test_postgres.py` | Hành vi riêng của PostgreSQL *(bỏ qua nếu không có server)* |

### Kiểm thử trên PostgreSQL

Một số hành vi chỉ tồn tại trên PostgreSQL — điển hình là việc một câu lệnh lỗi
làm hỏng toàn bộ giao dịch. SQLite không tái hiện được điều này, nên các test đó
cần một server thật:

```bash
TEST_PG_HOST=127.0.0.1 TEST_PG_PORT=5432 TEST_PG_NAME=medimanager_test \
TEST_PG_USER=postgres TEST_PG_PASSWORD=postgres pytest tests/test_postgres.py
```

Nếu không đặt `TEST_PG_HOST`, nhóm test này được **bỏ qua** (skip) chứ không báo lỗi.

### Kiểm thử giao diện không cần màn hình

`test_ui.py` dùng nền tảng offscreen của Qt nên chạy được trên máy chủ không có
màn hình (CI, WSL, container):

```bash
QT_QPA_PLATFORM=offscreen pytest tests/test_ui.py
```

Các test này mở thật từng cửa sổ với database thật, nhờ đó phát hiện được những
lỗi mà unit test bỏ sót: thiếu file `.ui`, sai tên widget, hoặc truy vấn không
khớp lược đồ.

---

## Đóng gói ứng dụng

Đóng gói thành file thực thi bằng **PyInstaller**:

```bash
pip install pyinstaller

pyinstaller --onefile --windowed \
  --name MediManager \
  --icon=MediManager.ico \
  --add-data "src/ui/forms:src/ui/forms" \
  --add-data "assets:assets" \
  run.py
```

> Trên Windows, dấu phân cách của `--add-data` là `;` thay vì `:`:
> `--add-data "src/ui/forms;src/ui/forms"`

File thực thi nằm trong thư mục `dist/`. Bản đóng gói dùng SQLite sẽ chạy được
ngay mà không cần cài đặt gì thêm.

---

## Xử lý sự cố

| Hiện tượng | Nguyên nhân & cách xử lý |
|------------|--------------------------|
| `Missing required database configuration` | Đang ở chế độ PostgreSQL nhưng thiếu `DB_HOST`/`DB_PASSWORD`. Điền vào `.env`, hoặc đặt `DB_BACKEND=sqlite` để chạy offline |
| `Failed to connect to the database` | Sai thông tin kết nối, hoặc project Supabase đang tạm dừng. Kiểm tra lại `.env` và trạng thái project |
| `ModuleNotFoundError: No module named 'psycopg2'` | Chỉ cần khi dùng PostgreSQL: `pip install psycopg2-binary` |
| `ImportError: libEGL.so.1` (Linux) | Thiếu thư viện hệ thống của Qt: `sudo apt install libegl1 libgl1 libxkbcommon-x11-0` |
| Báo cáo PDF mất dấu tiếng Việt | Thiếu `assets/fonts/arial.ttf`. Khôi phục file font từ repository |
| Quên mật khẩu admin | Ở chế độ SQLite: xóa `data/medimanager.db` để tạo lại tài khoản `admin`/`admin` (mất toàn bộ dữ liệu) |
| Muốn bắt đầu lại từ đầu | `python seed_demo_data.py --reset` |

---

## Roadmap

- [x] Kiến trúc phân lớp (Clean Architecture)
- [x] Mã hóa mật khẩu bằng bcrypt
- [x] Hỗ trợ hai backend SQLite / PostgreSQL
- [x] Quản lý nhập kho theo phiếu (header + chi tiết)
- [x] Cảnh báo hạn sử dụng phân mức
- [x] Báo cáo doanh thu, tồn kho, hóa đơn, hạn dùng dạng PDF
- [x] Bộ kiểm thử tự động
- [x] Script nạp dữ liệu mẫu
- [ ] Phân quyền chi tiết theo chức vụ trên từng màn hình
- [ ] Biểu đồ thống kê trực quan trên dashboard
- [ ] Xuất báo cáo dạng Excel
- [ ] Sao lưu / phục hồi dữ liệu
- [ ] Hỗ trợ máy quét mã vạch

---

## Đóng góp

### Quy trình

1. Fork repository
2. Tạo nhánh tính năng: `git checkout -b feature/ten-tinh-nang`
3. Viết mã và **bổ sung test** cho phần thay đổi
4. Chạy `pytest` để đảm bảo toàn bộ test còn xanh
5. Commit với thông điệp rõ ràng
6. Mở Pull Request

### Quy ước mã nguồn

- Tuân thủ **PEP 8**
- Đặt tên bằng tiếng Anh, thông báo hiển thị cho người dùng bằng tiếng Việt
- Mỗi hàm public cần có docstring
- Không viết SQL riêng cho từng backend — dùng `db.sql` (`SqlDialect`) khi cú pháp khác nhau
- Thay đổi lược đồ phải sửa `src/core/schema.py`, không sửa trực tiếp trong mã màn hình

### Báo lỗi

Khi tạo issue, vui lòng nêu rõ: backend đang dùng (SQLite hay PostgreSQL),
phiên bản Python, các bước tái hiện và thông báo lỗi đầy đủ.

---

## License

Dự án được phát hành dưới **MIT License**.

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

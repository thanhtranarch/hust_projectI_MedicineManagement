# MediManager - Hệ Thống Quản Lý Nhà Thuốc

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.4.0+-green.svg)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57.svg)
![Tests](https://img.shields.io/badge/Tests-154%20passing-brightgreen.svg)
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
sử dụng **cơ sở dữ liệu quan hệ SQLite** để quản lý thông tin thuốc, kiểm soát tồn kho,
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
| **Cơ sở dữ liệu** | SQLite - một file duy nhất, không cần cài đặt máy chủ |

---

## Bắt đầu nhanh

Chạy được ngay với 3 lệnh, **không cần cấu hình gì thêm**:

```bash
pip install -r requirements.txt
python seed_demo_data.py      # tùy chọn: nạp dữ liệu mẫu để xem thử
python run.py
```

Đăng nhập bằng `admin` / `admin`.

Toàn bộ dữ liệu nằm trong một file SQLite duy nhất tại `data/medimanager.db`.
File này cùng tất cả các bảng được **tạo tự động** ở lần chạy đầu tiên — không
cần cài máy chủ, không cần tài khoản dịch vụ, không cần chạy script SQL nào.

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

| Công nghệ | Vai trò | Phiên bản |
|-----------|---------|-----------|
| **Python** | Ngôn ngữ lập trình chính | 3.8+ |
| **PyQt6** | Framework giao diện người dùng | 6.4.0+ |
| **SQLite** | Cơ sở dữ liệu quan hệ (có sẵn trong Python) | 3 |
| **Qt Designer** | Thiết kế giao diện dạng `.ui` | — |
| **bcrypt** | Mã hóa mật khẩu | 4.0.1+ |
| **reportlab** | Sinh báo cáo PDF | 4.0.0+ |
| **darkdetect** | Nhận diện theme sáng/tối của hệ thống | 0.8.0+ |
| **python-dotenv** | Đọc cấu hình từ file `.env` | 1.0.0+ |
| **pytest** | Bộ khung kiểm thử (chỉ khi phát triển) | 7.4.0+ |

### Vì sao chọn SQLite

- **Không cần máy chủ** — dữ liệu nằm gọn trong một file, sao lưu chỉ là copy file
- **Có sẵn trong Python** — không phải cài driver hay dịch vụ ngoài
- **Chạy được ngay** — giảng viên hoặc người chấm chỉ cần `python run.py`
- **Đúng quy mô** — một nhà thuốc chạy trên một máy, không cần cơ sở dữ liệu phân tán
- **Kiểm thử dễ** — mỗi test dùng một file tạm riêng, chạy hoàn toàn offline

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

### Bước 3: Chạy

```bash
python run.py
```

Không có bước cấu hình cơ sở dữ liệu. Ở lần chạy đầu tiên ứng dụng sẽ:

1. Tạo thư mục `data/` và file `data/medimanager.db`
2. Tạo toàn bộ 11 bảng cùng các index
3. Nạp dữ liệu tham chiếu (9 danh mục thuốc, 4 hình thức thanh toán)
4. Tạo tài khoản quản trị `admin` / `admin`

### Tùy chọn: đổi vị trí file database

Chỉ cần khi bạn muốn lưu database ở chỗ khác (ví dụ ổ đĩa chung, USB):

```bash
cp .env.example .env
```

```env
SQLITE_PATH=D:/duong-dan/medimanager.db
```

---

## Sử dụng

### Khởi chạy

```bash
python run.py
```

Khi khởi động, ứng dụng in ra vị trí file dữ liệu:

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

### Sao lưu dữ liệu

Toàn bộ dữ liệu nằm trong một file duy nhất, nên sao lưu chỉ là copy file:

```bash
cp data/medimanager.db backup/medimanager_$(date +%Y%m%d).db
```

Khôi phục: chép file sao lưu đè lại vào `data/medimanager.db` khi ứng dụng đã đóng.

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
│  AppContext · DBManager · schema · sql               │
└───────────────────────┬──────────────────────────────┘
                        │
┌───────────────────────▼──────────────────────────────┐
│  Infrastructure — SQLite (data/medimanager.db)       │
└──────────────────────────────────────────────────────┘
```

Phụ thuộc chỉ đi một chiều từ trên xuống: màn hình có thể gọi service và
database, nhưng service không bao giờ import màn hình.

### Các thành phần chính

| Thành phần | Trách nhiệm |
|------------|-------------|
| `AppContext` | Giữ kết nối database và phiên đăng nhập, truyền xuống mọi màn hình |
| `DBManager` | Mở kết nối, thực thi truy vấn, quản lý giao dịch, tạo bảng và migration |
| `schema.py` | **Nguồn định nghĩa duy nhất** của lược đồ dữ liệu |
| `sql.py` | Các đoạn SQL dùng lại nhiều nơi (ví dụ: tính số ngày còn đến hạn) |
| `AuthService` | Xác thực, băm mật khẩu, đăng ký tài khoản |
| `ReportService` | Sinh báo cáo PDF |
| `BaseWindow` / `BaseDialog` | Nạp file `.ui`, đặt icon, hộp thoại thông báo dùng chung |

### Quản lý giao dịch

`DBManager.execute()` **tự động rollback** khi truy vấn lỗi rồi mới ném ngoại lệ.
Nhờ vậy một câu lệnh sai không để lại giao dịch dở dang làm hỏng các thao tác
tiếp theo trong cùng phiên làm việc.

Các nghiệp vụ nhiều bước (lập hóa đơn: ghi hóa đơn → ghi chi tiết → trừ tồn kho)
được gói trong **một giao dịch duy nhất**, nên không thể xảy ra tình trạng tồn kho
bị trừ trong khi hóa đơn chưa được lưu.

Chi tiết đầy đủ: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

---

## Cấu trúc thư mục

```
hust_projectI_MedicineManagement/
│
├── run.py                        # Entry point của ứng dụng
├── seed_demo_data.py             # Script nạp dữ liệu mẫu
├── requirements.txt              # Thư viện cho ứng dụng
├── requirements-dev.txt          # Thư viện cho phát triển & kiểm thử
├── pytest.ini                    # Cấu hình pytest
├── .env.example                  # Mẫu cấu hình (tùy chọn)
│
├── src/
│   ├── config/
│   │   ├── database.py           # Đường dẫn file database
│   │   └── settings.py           # Đường dẫn, hằng số ứng dụng
│   │
│   ├── core/
│   │   ├── app_context.py        # Kết nối database + phiên đăng nhập
│   │   ├── db_manager.py         # Thực thi truy vấn, giao dịch, migration
│   │   ├── schema.py             # Định nghĩa lược đồ (nguồn duy nhất)
│   │   └── sql.py                # Các đoạn SQL dùng chung
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
├── tests/                        # Bộ kiểm thử (154 test case)
│   ├── conftest.py               # Fixture dùng chung
│   ├── factories.py              # Hàm tạo dữ liệu kiểm thử
│   ├── test_database.py          # Lược đồ, migration, giao dịch
│   ├── test_auth.py              # Đăng nhập, đăng ký, nâng cấp mật khẩu
│   ├── test_workflows.py         # Nhập kho, bán hàng, cảnh báo hạn, doanh thu
│   ├── test_reports.py           # Sinh báo cáo PDF
│   ├── test_ui.py                # Kiểm thử giao diện headless
│   └── test_helpers.py           # Hàm tiện ích và cấu hình
│
├── assets/
│   ├── fonts/arial.ttf           # Font Unicode cho báo cáo tiếng Việt
│   └── icons/                    # Icon ứng dụng
│
├── docs/ARCHITECTURE.md          # Tài liệu kiến trúc chi tiết
│
├── data/                         # File SQLite (tự tạo, không commit)
└── exports/                      # Báo cáo PDF xuất ra (tự tạo, không commit)
```

---

## Cơ sở dữ liệu

Toàn bộ dữ liệu nằm trong **một file SQLite duy nhất**: `data/medimanager.db`.

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

`src/core/schema.py` là **nguồn định nghĩa duy nhất** — không có file `.sql`
riêng nào cần giữ đồng bộ. Khi cần thêm bảng hoặc cột:

1. Thêm bảng mới vào `TABLES`, hoặc thêm cột mới vào `MIGRATIONS`
2. Chạy `pytest tests/test_database.py` để kiểm tra

Vì sao cần `MIGRATIONS`: bảng được tạo bằng `CREATE TABLE IF NOT EXISTS`, câu
lệnh này **không làm gì** khi bảng đã tồn tại — kể cả khi bảng đang thiếu một cột
mới thêm. Do đó mỗi lần khởi động, ứng dụng đối chiếu danh sách cột thực tế và
tự chạy `ALTER TABLE ... ADD COLUMN` cho những cột còn thiếu. File database tạo
từ phiên bản cũ vẫn dùng được và được bổ sung cột mới mà không mất dữ liệu.

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

Bộ kiểm thử gồm **154 test case**. Mỗi test chạy trên một file SQLite tạm riêng
nên hoàn toàn offline, không ảnh hưởng tới dữ liệu thật và không cần cấu hình gì.

```bash
pip install -r requirements-dev.txt
pytest
```

Kết quả mong đợi:

```
154 passed
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
| `test_database.py` | Tạo bảng, migration, giao dịch và rollback, dữ liệu tham chiếu, biểu thức ngày tháng |
| `test_auth.py` | Đăng nhập đúng/sai, nâng cấp mật khẩu cũ sang bcrypt, ràng buộc đăng ký |
| `test_workflows.py` | Nhập kho cộng tồn, bán hàng trừ tồn, tổng tiền hóa đơn, cảnh báo hạn dùng, tổng hợp doanh thu |
| `test_reports.py` | Sinh đủ 4 loại PDF, hoạt động cả khi database rỗng, định dạng số liệu |
| `test_ui.py` | Mở toàn bộ 8 màn hình và 12 hộp thoại, kiểm tra cột bảng khớp tiêu đề |
| `test_helpers.py` | Định dạng tiền tệ/ngày tháng, kiểm tra email/điện thoại, cấu hình |

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

File thực thi nằm trong thư mục `dist/`. Vì SQLite đã có sẵn trong Python, bản
đóng gói chạy được ngay trên máy chưa cài gì — chỉ cần copy file `.exe` sang là dùng được.

---

## Xử lý sự cố

| Hiện tượng | Nguyên nhân & cách xử lý |
|------------|--------------------------|
| `ImportError: libEGL.so.1` (Linux) | Thiếu thư viện hệ thống của Qt: `sudo apt install libegl1 libgl1 libxkbcommon-x11-0` |
| `Failed to establish database connection` | Không có quyền ghi vào thư mục `data/`. Kiểm tra quyền thư mục, hoặc đặt `SQLITE_PATH` trỏ tới nơi ghi được |
| `database is locked` | Đang mở file database bằng chương trình khác (DB Browser, một phiên MediManager khác). Đóng bớt rồi thử lại |
| Báo cáo PDF mất dấu tiếng Việt | Thiếu `assets/fonts/arial.ttf`. Khôi phục file font từ repository |
| Quên mật khẩu admin | Xóa `data/medimanager.db` để tạo lại tài khoản `admin`/`admin` (mất toàn bộ dữ liệu — nên sao lưu trước) |
| Muốn bắt đầu lại từ đầu | `python seed_demo_data.py --reset` |
| Muốn xem trực tiếp dữ liệu | Mở `data/medimanager.db` bằng [DB Browser for SQLite](https://sqlitebrowser.org/) |

---

## Roadmap

- [x] Kiến trúc phân lớp (Clean Architecture)
- [x] Mã hóa mật khẩu bằng bcrypt
- [x] Cơ sở dữ liệu SQLite tự khởi tạo, không cần cấu hình
- [x] Quản lý nhập kho theo phiếu (header + chi tiết)
- [x] Cảnh báo hạn sử dụng phân mức
- [x] Báo cáo doanh thu, tồn kho, hóa đơn, hạn dùng dạng PDF
- [x] Bộ kiểm thử tự động
- [x] Script nạp dữ liệu mẫu
- [ ] Phân quyền chi tiết theo chức vụ trên từng màn hình
- [ ] Biểu đồ thống kê trực quan trên dashboard
- [ ] Xuất báo cáo dạng Excel
- [ ] Sao lưu / phục hồi dữ liệu ngay trong ứng dụng
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
- Truy vấn dùng tham số `%s` (`DBManager` tự chuyển sang `?` của SQLite) —
  **không bao giờ** nối chuỗi dữ liệu người dùng vào câu SQL
- Thay đổi lược đồ phải sửa `src/core/schema.py`, không sửa trực tiếp trong mã màn hình

### Báo lỗi

Khi tạo issue, vui lòng nêu rõ: phiên bản Python, hệ điều hành,
các bước tái hiện và thông báo lỗi đầy đủ.

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

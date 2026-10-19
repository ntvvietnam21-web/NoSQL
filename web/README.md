# Cổng thông tin Tuyển dụng - Flask + MongoDB + Redis

Sản phẩm bám theo `plan.txt`: Flask làm backend, MongoDB (`QL_TuyenDung`) là cơ sở dữ liệu chính, Redis hỗ trợ String/Hash/List/Set.

## 1. Chức năng đã có

- Trang chủ và danh sách việc làm
- Tìm kiếm theo từ khóa, địa điểm, ngành nghề
- Xem chi tiết việc làm
- Đăng nhập và phân quyền `ung_vien` / `nha_tuyen_dung`
- Ứng viên: dashboard, hồ sơ, ứng tuyển, việc yêu thích, lịch sử tìm kiếm
- Nhà tuyển dụng: dashboard, danh sách việc làm, đăng tin, sửa tin, xem ứng viên, duyệt/từ chối hồ sơ
- MongoDB: `QL_NguoiDung`, `QL_ViecLam`, `QL_UngTuyen`
- Redis String: cache chi tiết việc làm + lượt xem
- Redis Hash: cache tóm tắt việc làm
- Redis List: 5 từ khóa tìm kiếm gần nhất
- Redis Set: việc làm yêu thích

## 2. Chuẩn bị

Yêu cầu:

- Python 3.11+ (Python 3.14 của bạn vẫn có thể dùng nếu các package cài được)
- MongoDB đang chạy tại `mongodb://localhost:27017/`
- Redis đang chạy tại `localhost:6379`
- Database MongoDB tên `QL_TuyenDung`

## 3. Cài đặt

Mở PowerShell trong thư mục `DoAnTuyenDung`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Kiểm tra MongoDB và Redis:

```powershell
python scripts\test_connections.py
```

Chạy web:

```powershell
python app.py
```

Mở trình duyệt:

```text
http://127.0.0.1:5000
```

## 4. Đăng nhập dữ liệu mẫu

Dữ liệu JSON hiện tại chứa giá trị `mat_khau` dạng chuỗi bcrypt bị lược bỏ, không đủ độ dài để xác thực bcrypt thực tế. Vì vậy project có chế độ demo:

```env
ALLOW_DEMO_LOGIN=1
DEMO_PASSWORD=123456
```

Tài khoản mẫu từ dữ liệu:

- Ứng viên: `user_ung_vien_3009` / `123456` (có kỹ năng và nhiều lượt ứng tuyển sẵn)
- Nhà tuyển dụng: `user_nha_tuyen_dung_770` / `123456` (có nhiều tin tuyển dụng sẵn)

Khi có mật khẩu bcrypt đầy đủ, hệ thống tự ưu tiên kiểm tra bcrypt.

## 5. Nếu chưa import dữ liệu MongoDB

Đặt ba file JSON ở vị trí bất kỳ và chạy:

```powershell
python scripts\import_data.py --nguoidung "C:\duongdan\QL_TuyenDung.QL_NguoiDung.json" --vieclam "C:\duongdan\QL_TuyenDung.QL_ViecLam.json" --ungtuyen "C:\duongdan\QL_TuyenDung.QL_UngTuyen.json" --drop
```

Script đọc MongoDB Extended JSON (`$oid`, `$date`) và import vào đúng 3 collection.

## 6. Redis được dùng ở đâu

| Kiểu | Key | Chức năng |
|---|---|---|
| String | `job:<id>` | Cache chi tiết việc làm, TTL 300 giây |
| String | `job:view:<id>` | Đếm lượt xem |
| Hash | `job:info:<id>` | Cache tóm tắt việc làm |
| List | `search:recent:<user_id>` | 5 tìm kiếm gần nhất |
| Set | `favorite:jobs:<user_id>` | Việc làm yêu thích |

Nếu Redis tạm thời mất kết nối, web vẫn ưu tiên cho MongoDB hoạt động; các thao tác Redis được bọc để không làm sập trang.

## 7. Cấu trúc

```text
DoAnTuyenDung/
├── app.py
├── config.py
├── database/
├── routes/
├── services/
├── utils/
├── templates/
├── static/
├── scripts/
├── .env.example
└── requirements.txt
```

## 8. Lưu ý khi nộp

Đây là đồ án chạy local. Nếu triển khai production, nên bổ sung CSRF, rate limit, HTTPS, secret key mạnh, validation chặt hơn và tài khoản thật có bcrypt đầy đủ.

import random
from datetime import datetime
from pymongo import MongoClient
from faker import Faker

fake = Faker('vi_VN')

client = MongoClient("mongodb://localhost:27017/")
db = client["QL_TuyenDung"]

print("--- ĐANG DỌN DẸP VÀ SINH LẠI DỮ LIỆU VỚI 3 COLLECTION ---")

for collection_name in ["QL_NguoiDung", "QL_ViecLam", "QL_UngTuyen"]:
    db[collection_name].drop()

db.QL_CongTy.drop()
db.QL_HoSo.drop()

TINH_THANH = [
    "TP. Hồ Chí Minh", "Hà Nội", "Đà Nẵng", "Cần Thơ", "Hải Phòng",
    "An Giang", "Bà Rịa - Vũng Tàu", "Bắc Giang", "Bắc Ninh", "Bình Định",
    "Bình Dương", "Bình Phước", "Bình Thuận", "Cà Mau", "Đắk Lắk",
    "Đồng Nai", "Đồng Tháp", "Gia Lai", "Hà Nam", "Hải Dương",
    "Hưng Yên", "Khánh Hòa", "Kiên Giang", "Lâm Đồng", "Long An",
    "Nam Định", "Nghệ An", "Ninh Bình", "Ninh Thuận", "Phú Thọ",
    "Quảng Bình", "Quảng Nam", "Quảng Ngãi", "Quảng Ninh", "Sóc Trăng",
    "Tây Ninh", "Thái Bình", "Thái Nguyên", "Thanh Hóa", "Thừa Thiên Huế",
    "Tiền Giang", "Trà Vinh", "Vĩnh Long", "Vĩnh Phúc"
]

QUAN_HUYEN = {
    "TP. Hồ Chí Minh": ["Quận 1", "Quận 3", "Quận 4", "Quận 5", "Quận 7", "Quận 10", "Quận 11", "Quận 12", "Bình Thạnh", "Gò Vấp", "Tân Bình", "Tân Phú", "Phú Nhuận", "TP. Thủ Đức", "Bình Chánh", "Hóc Môn"],
    "Hà Nội": ["Ba Đình", "Hoàn Kiếm", "Đống Đa", "Cầu Giấy", "Hai Bà Trưng", "Thanh Xuân", "Nam Từ Liêm", "Bắc Từ Liêm", "Long Biên", "Hà Đông", "Hoàng Mai", "Tây Hồ"],
    "Đà Nẵng": ["Hải Châu", "Thanh Khê", "Sơn Trà", "Ngũ Hành Sơn", "Liên Chiểu", "Cẩm Lệ"],
    "Cần Thơ": ["Ninh Kiều", "Bình Thủy", "Cái Răng", "Ô Môn", "Thốt Nốt"],
    "Hải Phòng": ["Hồng Bàng", "Ngô Quyền", "Lê Chân", "Hải An", "Kiến An", "Đồ Sơn"],
    "An Giang": ["Long Xuyên", "Châu Đốc", "Tân Châu", "Châu Phú", "Thoại Sơn"],
    "Bà Rịa - Vũng Tàu": ["Vũng Tàu", "Bà Rịa", "Phú Mỹ", "Long Điền", "Đất Đỏ"],
    "Bắc Giang": ["TP. Bắc Giang", "Việt Yên", "Lạng Giang", "Hiệp Hòa"],
    "Bắc Ninh": ["TP. Bắc Ninh", "Từ Sơn", "Yên Phong", "Quế Võ"],
    "Bình Định": ["Quy Nhơn", "An Nhơn", "Hoài Nhơn", "Tuy Phước"],
    "Bình Dương": ["Thủ Dầu Một", "Dĩ An", "Thuận An", "Tân Uyên", "Bến Cát"],
    "Bình Phước": ["Đồng Xoài", "Chơn Thành", "Phước Long", "Bình Long"],
    "Bình Thuận": ["Phan Thiết", "La Gi", "Hàm Thuận Bắc", "Tuy Phong"],
    "Cà Mau": ["TP. Cà Mau", "Năm Căn", "Cái Nước", "U Minh"],
    "Đắk Lắk": ["Buôn Ma Thuột", "Buôn Hồ", "Ea Kar", "Krông Pắc"],
    "Đồng Nai": ["Biên Hòa", "Long Khánh", "Nhơn Trạch", "Trảng Bom", "Long Thành"],
    "Đồng Tháp": ["Cao Lãnh", "Sa Đéc", "Hồng Ngự", "Lấp Vò"],
    "Gia Lai": ["Pleiku", "An Khê", "Ayun Pa", "Chư Sê"],
    "Hà Nam": ["Phủ Lý", "Duy Tiên", "Kim Bảng", "Thanh Liêm"],
    "Hải Dương": ["TP. Hải Dương", "Chí Linh", "Kinh Môn", "Cẩm Giàng"],
    "Hưng Yên": ["TP. Hưng Yên", "Mỹ Hào", "Văn Lâm", "Khoái Châu"],
    "Khánh Hòa": ["Nha Trang", "Cam Ranh", "Ninh Hòa", "Diên Khánh"],
    "Kiên Giang": ["Rạch Giá", "Hà Tiên", "Phú Quốc", "Châu Thành"],
    "Lâm Đồng": ["Đà Lạt", "Bảo Lộc", "Đức Trọng", "Di Linh"],
    "Long An": ["Tân An", "Bến Lức", "Đức Hòa", "Cần Giuộc"],
    "Nam Định": ["TP. Nam Định", "Mỹ Lộc", "Giao Thủy", "Hải Hậu"],
    "Nghệ An": ["Vinh", "Cửa Lò", "Thái Hòa", "Diễn Châu"],
    "Ninh Bình": ["TP. Ninh Bình", "Tam Điệp", "Gia Viễn", "Hoa Lư"],
    "Ninh Thuận": ["Phan Rang - Tháp Chàm", "Ninh Hải", "Ninh Phước"],
    "Phú Thọ": ["Việt Trì", "Phú Thọ", "Lâm Thao", "Thanh Ba"],
    "Quảng Bình": ["Đồng Hới", "Ba Đồn", "Bố Trạch", "Quảng Ninh"],
    "Quảng Nam": ["Tam Kỳ", "Hội An", "Điện Bàn", "Núi Thành"],
    "Quảng Ngãi": ["TP. Quảng Ngãi", "Đức Phổ", "Bình Sơn", "Sơn Tịnh"],
    "Quảng Ninh": ["Hạ Long", "Cẩm Phả", "Uông Bí", "Móng Cái"],
    "Sóc Trăng": ["TP. Sóc Trăng", "Ngã Năm", "Vĩnh Châu", "Mỹ Xuyên"],
    "Tây Ninh": ["TP. Tây Ninh", "Trảng Bàng", "Hòa Thành", "Gò Dầu"],
    "Thái Bình": ["TP. Thái Bình", "Tiền Hải", "Đông Hưng", "Quỳnh Phụ"],
    "Thái Nguyên": ["TP. Thái Nguyên", "Sông Công", "Phổ Yên", "Đại Từ"],
    "Thanh Hóa": ["TP. Thanh Hóa", "Sầm Sơn", "Bỉm Sơn", "Nghi Sơn"],
    "Thừa Thiên Huế": ["TP. Huế", "Hương Thủy", "Hương Trà", "Phú Vang"],
    "Tiền Giang": ["Mỹ Tho", "Gò Công", "Cai Lậy", "Châu Thành"],
    "Trà Vinh": ["TP. Trà Vinh", "Duyên Hải", "Cầu Kè", "Tiểu Cần"],
    "Vĩnh Long": ["TP. Vĩnh Long", "Bình Minh", "Long Hồ", "Mang Thít"],
    "Vĩnh Phúc": ["Vĩnh Yên", "Phúc Yên", "Bình Xuyên", "Tam Dương"]
}

THUONG_HIEU_LON = [
    ("FPT Software", "1000+ nhân viên", "FPT"),
    ("Viettel Solutions", "1000+ nhân viên", "Viettel"),
    ("VNG Corporation", "1000+ nhân viên", "VNG"),
    ("Tiki Việt Nam", "500-1000 nhân viên", "Tiki"),
    ("Shopee Việt Nam", "1000+ nhân viên", "Shopee"),
    ("Tập đoàn Vingroup", "1000+ nhân viên", "Vingroup"),
    ("Công ty MISA", "500-1000 nhân viên", "MISA"),
    ("CMC Global", "500-1000 nhân viên", "CMC"),
    ("KMS Technology", "500-1000 nhân viên", "KMS"),
    ("Ngân hàng Techcombank", "1000+ nhân viên", "Techcombank"),
    ("Ngân hàng MB Bank", "1000+ nhân viên", "MBBank"),
    ("Ví MoMo", "500-1000 nhân viên", "MoMo"),
    ("Tập đoàn Vinamilk", "1000+ nhân viên", "Vinamilk"),
    ("VNPT Technology", "1000+ nhân viên", "VNPT"),
    ("NashTech Vietnam", "1000+ nhân viên", "NashTech"),
    ("Bosch Global Software Technologies", "1000+ nhân viên", "Bosch"),
    ("Axon Active Vietnam", "500-1000 nhân viên", "Axon"),
    ("Rikkeisoft", "1000+ nhân viên", "Rikkeisoft"),
    ("TMA Solutions", "1000+ nhân viên", "TMA"),
    ("ELCA Vietnam", "500-1000 nhân viên", "ELCA"),
    ("Grab Việt Nam", "1000+ nhân viên", "Grab"),
    ("Lazada Việt Nam", "1000+ nhân viên", "Lazada"),
    ("Sendo", "500-1000 nhân viên", "Sendo"),
    ("Zalo", "500-1000 nhân viên", "Zalo"),
    ("NAB Innovation Centre Vietnam", "500-1000 nhân viên", "NAB"),
    ("Deloitte Vietnam", "500-1000 nhân viên", "Deloitte"),
    ("PwC Vietnam", "500-1000 nhân viên", "PwC"),
    ("KPMG Vietnam", "500-1000 nhân viên", "KPMG"),
    ("EY Vietnam", "500-1000 nhân viên", "EY"),
    ("Sacombank", "1000+ nhân viên", "Sacombank"),
    ("ACB", "1000+ nhân viên", "ACB"),
    ("VPBank", "1000+ nhân viên", "VPBank"),
    ("BIDV", "1000+ nhân viên", "BIDV"),
    ("Vietcombank", "1000+ nhân viên", "Vietcombank")
]

CONG_TY_NHO = [
    "Công ty TNHH Giải pháp Số Vina", "Công ty Cổ phần Công nghệ Nam Việt",
    "Công ty TNHH Truyền thông Sài Gòn", "Công ty Cổ phần Thương mại Đông Nam",
    "Công ty TNHH Phần mềm Á Châu", "Công ty Cổ phần Dịch vụ Số Việt",
    "Công ty TNHH Công nghệ Sao Việt", "Công ty Cổ phần Giải pháp Mây Việt",
    "Công ty TNHH Dữ liệu Thông Minh", "Công ty Cổ phần Phần mềm Mekong",
    "Công ty TNHH Công nghệ Đông Dương", "Công ty Cổ phần Truyền thông Đại Việt",
    "Công ty TNHH Thương mại Minh Phát", "Công ty Cổ phần Kỹ thuật Tân Tiến",
    "Công ty TNHH Giải pháp Doanh nghiệp Việt", "Công ty Cổ phần Công nghệ Hồng Hà",
    "Công ty TNHH Digital Future", "Công ty Cổ phần Innovation Hub Việt Nam",
    "Công ty TNHH TechNova Việt Nam", "Công ty Cổ phần SmartBiz"
]

LINH_VUC_LIST = [
    "IT", "Bán hàng", "Marketing", "Thiết kế", "Kế toán", "Tài chính - Ngân hàng",
    "Nhân sự", "Chăm sóc khách hàng", "Logistics", "Thương mại điện tử",
    "Giáo dục", "Y tế", "Sản xuất", "Xây dựng", "Bất động sản", "Du lịch - Nhà hàng - Khách sạn"
]

KY_NANG_IT = [
    "Python", "Java", "C#", "C++", "JavaScript", "TypeScript", "Node.js", "ReactJS",
    "VueJS", "Angular", "Next.js", "PHP", "Laravel", "Spring Boot", ".NET",
    "SQL", "MySQL", "PostgreSQL", "SQL Server", "MongoDB", "Redis", "Neo4j",
    "Docker", "Kubernetes", "Git", "GitHub", "GitLab", "Linux", "REST API",
    "GraphQL", "AWS", "Azure", "Google Cloud", "CI/CD", "Jenkins", "Kafka",
    "RabbitMQ", "Spark", "Hadoop", "Pandas", "NumPy", "Power BI", "Tableau",
    "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "NLP",
    "Computer Vision", "Data Engineering", "Data Analysis", "ETL", "Airflow",
    "Selenium", "Postman", "Figma", "HTML", "CSS", "Bootstrap", "Tailwind CSS"
]

def tao_cong_ty(i):
    tinh = random.choice(TINH_THANH)
    quan = random.choice(QUAN_HUYEN[tinh])

    if i < 300:
        brand_info = random.choice(THUONG_HIEU_LON)
        ten_cty = f"{brand_info[0]} - Chi nhánh {tinh}"
        quy_mo = brand_info[1]
        domain = brand_info[2].lower()
    else:
        ten_cty = f"{random.choice(CONG_TY_NHO)} ({tinh})"
        quy_mo = random.choice(["10-50 nhân viên", "50-200 nhân viên"])
        domain = f"company{i}"

    return {
        "ten_cong_ty": ten_cty,
        "quy_mo": quy_mo,
        "dia_chi": {
            "thanh_pho": tinh,
            "quan_huyen": quan,
            "chi_tiet": f"Số {random.randint(1, 250)} Đường Nguyễn Huệ, {quan}"
        },
        "lien_he": {
            "email": f"tuyendung@{domain}.com.vn",
            "so_dien_thoai": f"028{random.randint(1000000, 9999999)}"
        },
        "mo_ta": f"Doanh nghiệp hoạt động tại {tinh} trong lĩnh vực phát triển dịch vụ và công nghệ."
    }

# 1. QL_NguoiDung
print("1. Sinh 20,000 QL_NguoiDung...")
danh_sach_nguoi_dung = []

for i in range(20000):
    vai_tro = "nha_tuyen_dung" if i < 2000 else "ung_vien"

    nguoi_dung = {
        "ten_dang_nhap": f"user_{vai_tro}_{i + 1}",
        "mat_khau": "$2b$12$eImiTXuWVxfM37uY4JANjOL.81F8R.hNsdS4V",
        "email": fake.email(),
        "vai_tro": vai_tro,
        "trang_thai": "hoat_dong",
        "ngay_tao": fake.date_time_between(start_date="-1y", end_date="now")
    }

    if vai_tro == "ung_vien":
        linh_vuc = random.choice(LINH_VUC_LIST)
        chi_tiet_cv = {}

        if linh_vuc == "IT":
            chi_tiet_cv["ky_nang"] = random.sample(KY_NANG_IT, k=3)
            chi_tiet_cv["github"] = f"https://github.com/user_{i + 1}"
        else:
            chi_tiet_cv["ngoai_ngu"] = random.choice(
                ["TOEIC 750", "IELTS 6.5", "Tiếng Nhật N3"]
            )

        nguoi_dung["ho_so"] = {
            "ho_ten": fake.name(),
            "nganh_nghe": linh_vuc,
            "hoc_van": random.choice(
                ["Đại học Bách Khoa", "Đại học CNTT", "Đại học Kinh Tế"]
            ),
            "kinh_nghiem": f"{random.randint(1, 4)} năm kinh nghiệm",
            "chi_tiet_ho_so": chi_tiet_cv,
            "ngay_cap_nhat": datetime.now()
        }

    danh_sach_nguoi_dung.append(nguoi_dung)

res_user = db.QL_NguoiDung.insert_many(danh_sach_nguoi_dung)
recruiter_ids = res_user.inserted_ids[:2000]
candidate_ids = res_user.inserted_ids[2000:]

# 2. QL_ViecLam
print("2. Sinh 50,000 QL_ViecLam...")

danh_sach_cong_ty = []
for i in range(2000):
    cong_ty = tao_cong_ty(i)
    cong_ty["ma_nha_tuyen_dung"] = recruiter_ids[i]
    danh_sach_cong_ty.append(cong_ty)

danh_sach_viec_lam = []
for i in range(50000):
    linh_vuc = random.choice(LINH_VUC_LIST)
    tinh = random.choice(TINH_THANH)
    cong_ty = random.choice(danh_sach_cong_ty)

    chi_tiet = {"kinh_nghiem_nam": random.randint(1, 5)}

    if linh_vuc == "IT":
        chi_tiet["cong_nghe_chinh"] = random.sample(
            KY_NANG_IT, k=random.randint(2, 4)
        )
        chi_tiet["hinh_thuc_lam_viec"] = random.choice(
            ["Remote", "Hybrid", "Tại văn phòng"]
        )
    elif linh_vuc == "Bán hàng":
        chi_tiet["kpi_doanh_so_thang"] = f"{random.randint(100, 300)} triệu"
        chi_tiet["hoa_hong_phantram"] = random.randint(3, 8)
    elif linh_vuc == "Marketing":
        chi_tiet["kenh_phu_trach"] = random.sample(
            ["Facebook Ads", "SEO Website", "TikTok Ads"], k=2
        )

    if random.choice([True, False]):
        chi_tiet["phu_cap_an_trua"] = "1.000.000 VNĐ/tháng"

    viec_lam = {
        "cong_ty": cong_ty,
        "tieu_de": f"Tuyển dụng {linh_vuc} tại {tinh}",
        "nganh_nghe": linh_vuc,
        "muc_luong": {
            "toi_thieu": random.randint(12, 20) * 1000000,
            "toi_da": random.randint(25, 50) * 1000000,
            "don_vi": "VND"
        },
        "dia_diem": tinh,
        "chi_tiet_nganh": chi_tiet,
        "ngay_dang": fake.date_time_between(start_date="-30d", end_date="now"),
        "trang_thai": "dang_tuyen"
    }

    danh_sach_viec_lam.append(viec_lam)

res_job = db.QL_ViecLam.insert_many(danh_sach_viec_lam)
job_ids = res_job.inserted_ids

# 3. QL_UngTuyen
print("3. Sinh 100,000 QL_UngTuyen...")
danh_sach_ung_tuyen = []

for i in range(100000):
    ung_tuyen = {
        "ma_viec_lam": random.choice(job_ids),
        "ma_ung_vien": random.choice(candidate_ids),
        "ngay_ung_tuyen": fake.date_time_between(start_date="-15d", end_date="now"),
        "trang_thai": random.choice(["cho_duyet", "da_duyet", "tu_choi"]),
        "ghi_chu": random.choice(
            ["Hồ sơ phù hợp", "Đã gửi lịch phỏng vấn", "Chưa đạt yêu cầu"]
        )
    }
    danh_sach_ung_tuyen.append(ung_tuyen)

BATCH_SIZE = 5000
for start in range(0, len(danh_sach_ung_tuyen), BATCH_SIZE):
    db.QL_UngTuyen.insert_many(
        danh_sach_ung_tuyen[start:start + BATCH_SIZE]
    )

db.QL_NguoiDung.create_index("email")
db.QL_NguoiDung.create_index("vai_tro")
db.QL_ViecLam.create_index("nganh_nghe")
db.QL_ViecLam.create_index("dia_diem")
db.QL_UngTuyen.create_index("ma_viec_lam")
db.QL_UngTuyen.create_index("ma_ung_vien")

print("=== SINH MOCK DATA THÀNH CÔNG ===")
print("Các collection hiện có:", db.list_collection_names())
print("QL_NguoiDung:", db.QL_NguoiDung.count_documents({}))
print("QL_ViecLam:", db.QL_ViecLam.count_documents({}))
print("QL_UngTuyen:", db.QL_UngTuyen.count_documents({}))

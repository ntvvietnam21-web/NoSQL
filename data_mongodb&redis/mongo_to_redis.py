from pymongo import MongoClient
import redis
import json

# Kết nối MongoDB
mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["QL_TuyenDung"]
collection = db["QL_ViecLam"]

# Kết nối Redis
r = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

# Lấy 1 việc làm đầu tiên từ MongoDB
job = collection.find_one()

# Chuyển ObjectId và Date thành chuỗi để lưu được vào Redis
job["_id"] = str(job["_id"])

if "ngay_dang" in job:
    job["ngay_dang"] = str(job["ngay_dang"])

if "cong_ty" in job and "ma_nha_tuyen_dung" in job["cong_ty"]:
    job["cong_ty"]["ma_nha_tuyen_dung"] = str(
        job["cong_ty"]["ma_nha_tuyen_dung"]
    )

# Tạo key Redis
redis_key = f"job:{job['_id']}"

# Lưu dữ liệu vào Redis dưới dạng JSON
r.set(
    redis_key,
    json.dumps(job, ensure_ascii=False),
    ex=300
)

print("Da luu vao Redis")
print("Key:", redis_key)

# Đọc lại từ Redis
data = r.get(redis_key)

print("Du lieu lay tu Redis:")
print(data)
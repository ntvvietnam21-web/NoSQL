from pymongo import MongoClient
import redis
import json

JOB_ID = "6ac2864395b697299f21672e"

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

# Key cache và key lượt xem
cache_key = f"job:{JOB_ID}"
view_key = f"job:view:{JOB_ID}"

# Kiểm tra cache
data = r.get(cache_key)

if data:
    print("Lay du lieu tu Redis")
    job = json.loads(data)
else:
    print("Khong co cache, lay du lieu tu MongoDB")

    from bson import ObjectId

    job = collection.find_one({"_id": ObjectId(JOB_ID)})

    job["_id"] = str(job["_id"])
    job["ngay_dang"] = str(job["ngay_dang"])

    if "cong_ty" in job and "ma_nha_tuyen_dung" in job["cong_ty"]:
        job["cong_ty"]["ma_nha_tuyen_dung"] = str(
            job["cong_ty"]["ma_nha_tuyen_dung"]
        )

    r.set(
        cache_key,
        json.dumps(job, ensure_ascii=False),
        ex=300
    )

# Mỗi lần xem việc làm thì tăng 1 lượt xem
views = r.incr(view_key)

print("Tieu de:", job["tieu_de"])
print("Dia diem:", job["dia_diem"])
print("Luot xem:", views)
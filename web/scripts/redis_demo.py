import json
import os
from bson import ObjectId
from pymongo import MongoClient
import redis
from dotenv import load_dotenv

load_dotenv()

mongo = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
db = mongo[os.getenv("MONGO_DB", "QL_TuyenDung")]
r = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=int(os.getenv("REDIS_PORT", "6379")), decode_responses=True)

job = db.QL_ViecLam.find_one()
if not job:
    raise SystemExit("QL_ViecLam khong co du lieu")
job_id = str(job["_id"])

print("1) STRING - cache + view")
r.set(f"job:{job_id}", json.dumps({"tieu_de": job.get("tieu_de"), "dia_diem": job.get("dia_diem")}, ensure_ascii=False), ex=300)
print("GET:", r.get(f"job:{job_id}"))
print("TTL:", r.ttl(f"job:{job_id}"))
print("VIEW:", r.incr(f"job:view:{job_id}"))

print("\n2) HASH - tom tat viec lam")
r.hset(f"job:info:{job_id}", mapping={
    "tieu_de": job.get("tieu_de", ""),
    "nganh_nghe": job.get("nganh_nghe", ""),
    "dia_diem": job.get("dia_diem", ""),
    "trang_thai": job.get("trang_thai", ""),
})
print(r.hgetall(f"job:info:{job_id}"))

print("\n3) LIST - lich su tim kiem")
key = "search:recent:demo_user"
r.delete(key)
for kw in ["IT", "Python", "Marketing"]:
    r.lpush(key, kw)
r.ltrim(key, 0, 4)
print(r.lrange(key, 0, 4))

print("\n4) SET - viec lam yeu thich")
key = "favorite:jobs:demo_user"
r.delete(key)
r.sadd(key, job_id)
r.sadd(key, job_id)  # Set van chi luu 1 lan
print(r.smembers(key))
print("SCARD:", r.scard(key))

from pymongo import MongoClient
import redis
import os
from dotenv import load_dotenv

load_dotenv()

mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
mongo_db = os.getenv("MONGO_DB", "QL_TuyenDung")
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", "6379"))

print("=== KIEM TRA KET NOI ===")

try:
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=3000)
    client.admin.command("ping")
    db = client[mongo_db]
    print("MongoDB: OK")
    print("  QL_NguoiDung:", db.QL_NguoiDung.count_documents({}))
    print("  QL_ViecLam:", db.QL_ViecLam.count_documents({}))
    print("  QL_UngTuyen:", db.QL_UngTuyen.count_documents({}))
except Exception as e:
    print("MongoDB: LOI -", e)

try:
    r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True, socket_connect_timeout=3)
    print("Redis:", "OK" if r.ping() else "LOI")
except Exception as e:
    print("Redis: LOI -", e)

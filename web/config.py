import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "do-an-tuyen-dung-local-secret")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    MONGO_DB = os.getenv("MONGO_DB", "QL_TuyenDung")
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))
    CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))

    # Dữ liệu mẫu hiện tại chứa chuỗi mật khẩu giả/lược bỏ, không phải bcrypt đầy đủ.
    # Chế độ demo cho phép đăng nhập bằng DEMO_PASSWORD để chạy đồ án.
    ALLOW_DEMO_LOGIN = os.getenv("ALLOW_DEMO_LOGIN", "1") == "1"
    DEMO_PASSWORD = os.getenv("DEMO_PASSWORD", "123456")

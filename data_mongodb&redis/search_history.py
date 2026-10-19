import redis

r = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

user_id = "ungvien_1"

search_key = f"search:recent:{user_id}"

tu_khoa = input("Nhap tu khoa tim kiem: ")

# Thêm từ khóa mới vào đầu danh sách
r.lpush(search_key, tu_khoa)

# Chỉ giữ lại 5 từ khóa gần nhất
r.ltrim(search_key, 0, 4)

# Lấy danh sách lịch sử tìm kiếm
lich_su = r.lrange(search_key, 0, 4)

print("Lich su tim kiem gan day:")

for i, item in enumerate(lich_su, start=1):
    print(i, item)
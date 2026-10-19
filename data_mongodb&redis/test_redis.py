import redis

r = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

print("Ket noi Redis:", r.ping())

r.set("job:2", "Tuyen dung Python Developer")

print("Du lieu:", r.get("job:2"))
import redis

r = redis.Redis(
    host="172.22.219.82",
    port=6379,
    decode_responses=True
)

r.set("taskforge_test", "hello from Windows")

value = r.get("taskforge_test")

print(value)
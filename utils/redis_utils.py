import redis

redis_db = redis.Redis(
    host = "redis-13209.c292.ap-southeast-1-1.ec2.redns.redis-cloud.com",
    port = 13209,
    password = "irKVnFOjVdss02m0NV4mBv5bCHfbOoT3",
    ssl = False,
)

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True, db=0)
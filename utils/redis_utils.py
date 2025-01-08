import redis
from redis.commands.search.field import VectorField

redis_db = redis.Redis(
    host = "redis-17564.c102.us-east-1-mz.ec2.redns.redis-cloud.com",
    port = 17564,
    password = "GNd2XoAZtT5OTWdh92lDfjqlKP4TqYzq",
    ssl = False,
)

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True, db=0)

# redis_db.ft().create_index(
#     [
#         VectorField(
#             "embedding",
#             "HNSW",
#             {
#                 "TYPE": "FLOAT32",
#                 "DIM": 512,  
#                 "DISTANCE_METRIC": "L2",
#             },
#         )
#     ]
# )
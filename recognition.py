from flask import current_app
from deepface import DeepFace
import os
import numpy as np
from tqdm import tqdm
from redis.commands.search.field import VectorField, TagField
from redis.commands.search.query import Query
import redis

r = redis.Redis(
    host = "redis-13209.c292.ap-southeast-1-1.ec2.redns.redis-cloud.com",
    port = 13209,
    password = "irKVnFOjVdss02m0NV4mBv5bCHfbOoT3",
    ssl = False,
)

# embeddings = []
# for dirpath, dirnames, filenames in os.walk("./faces/database/class3/"):
#     for filename in filenames:
#         if filename.lower().endswith(('.jpg', '.png')):
#             img_path = f"{dirpath}{filename}"
#             embedding = DeepFace.represent(
#                 img_path=img_path,
#                 model_name="ArcFace",
#                 detector_backend="retinaface",
#             )[0]["embedding"]
#             embeddings.append((img_path, embedd.ing))

# print(f'embeddings length: {len(embeddings)}')
 

# pipeline = r.pipeline(transaction=False)
# for img_path, embedding in tqdm(embeddings):
#     key = img_path.split("/")[-1]
#     value = np.array(embedding).astype(np.float32).tobytes()
#     pipeline.hset(key, mapping={"embedding": value})

# pipeline_results = pipeline.execute()


# THIS SHOULD ONLY BE DONE ONCE

# r.ft().create_index(
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


target_embedding = DeepFace.represent(
    img_path="input3.jpg",
    model_name="ArcFace",
    detector_backend="retinaface"
)[0]["embedding"]

query_vector = np.array(target_embedding).astype(np.float32).tobytes()

k = 2

base_query = f"*=>[KNN {k} @embedding $query_vector AS distance]"
query = Query(base_query).return_fields("distance").sort_by("distance").dialect(2)
results = r.ft().search(query, query_params={"query_vector": query_vector})

print(results)

for idx, result in enumerate(results.docs):
    print(
        f"{idx + 1}th nearest neighbor is {result.id} with distance {result.distance}"
    )
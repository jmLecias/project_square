from utils.redis_utils import redis_client

def test_pubsub():
    pubsub = redis_client.pubsub()
    pubsub.subscribe("detection_events")
    print("Subscribed to detection_events")

    for message in pubsub.listen():
        print(f"Received message: {message}")

test_pubsub()
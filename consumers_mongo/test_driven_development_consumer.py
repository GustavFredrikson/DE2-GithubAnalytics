import pulsar
import json
from pymongo import MongoClient

client = pulsar.Client("pulsar://pulsar-proxy.pulsar.svc.cluster.local:6650")

consumer = client.subscribe("TDDTopic", "my-subscription")

# Mongodb
mongo_client = MongoClient("mongodb://mongodb_host:27017/")
db = mongo_client.your_database
collection = db.tdd

message_count = 0
save_interval = 100


TERMINATE_AFTER_N_MESSAGES = 10000

n_messages = 0
while True:
    try:
        msg = consumer.receive()
        repo = json.loads(msg.data())

        collection.update_one(
            {"name": repo["name"]},
            {"$set": {"has_tests": repo["has_tests"]}},
            upsert=True,
        )

        message_count += 1

        # Print all data every save_interval messages
        if message_count % save_interval == 0:
            all_data = collection.find()
            for data in all_data:
                print(f'Repo Name: {data["name"]}, Has Tests: {data["has_tests"]}')

        consumer.acknowledge(msg)
        n_messages += 1
        if n_messages >= TERMINATE_AFTER_N_MESSAGES:
            break
    except Exception as e:
        print("Error: ", e)

client.close()

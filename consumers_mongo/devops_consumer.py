import pulsar
import json
from pymongo import MongoClient

client = pulsar.Client("pulsar://pulsar-proxy.pulsar.svc.cluster.local:6650")
consumer = client.subscribe("WorkflowTopic", "my-subscription")

# Mongodb
mongo_client = MongoClient("mongodb://mongodb_host:mongoport/")
db = mongo_client.your_database
collection = db.devops

message_count = 0
save_interval = 100

while True:
    try:
        msg = consumer.receive()
        repo = json.loads(msg.data())

        collection.update_one(
            {"name": repo["name"]},
            {"$set": {"has_ci_cd": repo["has_ci_cd"]}},
            upsert=True,
        )

        message_count += 1

        # Print all data every save_interval messages
        if message_count % save_interval == 0:
            all_data = collection.find()
            for data in all_data:
                print(f'Repo Name: {data["name"]}, Has CI/CD: {data["has_ci_cd"]}')

        consumer.acknowledge(msg)
    except Exception as e:
        print("Error: ", e)

client.close()

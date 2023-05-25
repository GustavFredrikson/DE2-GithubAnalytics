import pulsar
import json
from pymongo import MongoClient

client = pulsar.Client("pulsar://pulsar-proxy.pulsar.svc.cluster.local:6650")
consumer = client.subscribe("LanguagesTopic", "my-subscription")

# Connect to MongoDB
mongo_client = MongoClient(
    "mongodb://gustavfredrikson:my-password@my-mongodb.default.svc.cluster.local:27017/my-database"
)
db = mongo_client.my_database
collection = db.languages

message_count = 0
save_interval = 10

while True:
    try:
        msg = consumer.receive()
        repo = json.loads(msg.data())

        repo_language = repo["language"] if repo["language"] else "No Language"

        # Update the collection with the language of the new repository
        language_doc = collection.find_one({"language": repo_language})

        if language_doc is None:
            collection.insert_one({"language": repo_language, "count": 1})
        else:
            collection.update_one({"language": repo_language}, {"$inc": {"count": 1}})

        message_count += 1

        # Calculate and print the top 10 languages
        if message_count % save_interval == 0:
            top_languages = list(collection.find().sort("count", -1).limit(10))
            print("Top 10 languages: ", top_languages)

        # Acknowledge processing of message so that it can be deleted
        consumer.acknowledge(msg)
    except Exception as e:
        print("Error: ", e)

client.close()

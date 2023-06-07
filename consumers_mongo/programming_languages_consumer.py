import pulsar
import json
from pymongo import MongoClient

client = pulsar.Client("pulsar://pulsar-proxy.pulsar.svc.cluster.local:6650")

consumer = client.subscribe("LanguagesTopic", "my-subscription")

# Mongodb:
mongo_client = MongoClient("mongodb://mongodb_host:mongodb_port/")
db = mongo_client.your_database
collection = db.languages

message_count = 0
save_interval = 1000

try:
    while True:
        msg = consumer.receive()
        repo = json.loads(msg.data())

        repo_language = repo["language"] if repo.get("language") else "No Language"

        lang_doc = collection.find_one({"language": repo_language})
        if lang_doc:
            collection.update_one({"language": repo_language}, {"$inc": {"count": 1}})
        else:
            collection.insert_one({"language": repo_language, "count": 1})

        message_count += 1

        # Print top 10 languages every save_interval messages
        if message_count % save_interval == 0:
            top_languages = collection.find().sort("count", -1).limit(10)
            for lang in top_languages:
                print(f'Language: {lang["language"]}, Count: {lang["count"]}')

        consumer.acknowledge(msg)

except Exception as e:
    print("Error: ", e)

finally:
    client.close()

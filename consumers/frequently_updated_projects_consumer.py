import pulsar
import json
from pymongo import MongoClient

# Configure the logging settings

client = pulsar.Client("pulsar://pulsar-proxy.pulsar.svc.cluster.local:6650")
consumer = client.subscribe("CommitsTopic", "my-subscription")

mongo_client = MongoClient(
    "mongodb://gustavfredrikson:my-password@my-mongodb.default.svc.cluster.local:27017/my-database"
)

db = mongo_client.my_database  # Use your database name here
collection = db.commits  # Use your collection name here

message_count = 0
save_interval = 10

while True:
    try:
        msg = consumer.receive()
        repo = json.loads(msg.data())

        repo_name = repo["name"]
        repo_record = collection.find_one({"name": repo_name})

        if repo_record:
            collection.update_one(
                {"name": repo_name},
                {
                    "$inc": {"commits": int(repo["commits"])},  # Ensure it's integer
                    "$set": {
                        "commit_frequency": (
                            repo_record["commit_frequency"] + repo["commit_frequency"]
                        )
                        / 2
                    },
                },  # Average frequency
            )
            if repo["start_date"] < repo_record["start_date"]:
                collection.update_one(
                    {"name": repo_name}, {"$set": {"start_date": repo["start_date"]}}
                )
            if repo["end_date"] > repo_record["end_date"]:
                collection.update_one(
                    {"name": repo_name}, {"$set": {"end_date": repo["end_date"]}}
                )
        else:
            collection.insert_one(
                {
                    "name": repo_name,
                    "commits": int(repo["commits"]),  # Ensure it's integer
                    "commit_frequency": repo["commit_frequency"],
                    "start_date": repo["start_date"],
                    "end_date": repo["end_date"],
                }
            )

        message_count += 1

        # Print top 10 projects every save_interval messages
        if message_count % save_interval == 0:
            most_commits = list(collection.find().sort("commits", -1).limit(10))
            print("Top 10 projects by total commits: ", most_commits)

            most_frequent_commits = list(
                collection.find().sort("commit_frequency", -1).limit(10)
            )
            print("Top 10 projects by commit frequency: ", most_frequent_commits)

        consumer.acknowledge(msg)
    except Exception as e:
        print("Error: ", e)

client.close()

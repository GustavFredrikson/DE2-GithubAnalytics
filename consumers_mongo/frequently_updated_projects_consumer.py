import pulsar
import json
from pymongo import MongoClient
from datetime import datetime

client = pulsar.Client("pulsar://pulsar-proxy.pulsar.svc.cluster.local:6650")
consumer = client.subscribe("CommitsTopic", "my-subscription")

# Setup MongoDB
mongo_client = MongoClient("mongodb://mongodb_host:mongoport/")
db = mongo_client.your_database
collection = db.commits

message_count = 0
save_interval = 100

while True:
    try:
        msg = consumer.receive()
        repo = json.loads(msg.data())

        repo["commits"] = int(repo["commits"])  # Ensure it's integer
        repo["commit_frequency"] = float(repo["commit_frequency"])  # Ensure it's float
        repo["start_date"] = datetime.strptime(
            repo["start_date"], "%Y-%m-%d"
        )  # Convert to datetime
        repo["end_date"] = datetime.strptime(
            repo["end_date"], "%Y-%m-%d"
        )  # Convert to datetime

        repo_doc = collection.find_one({"name": repo["name"]})
        if repo_doc:
            new_commits = repo_doc["commits"] + repo["commits"]
            new_commit_frequency = (
                repo_doc["commit_frequency"] + repo["commit_frequency"]
            ) / 2
            new_start_date = min(repo_doc["start_date"], repo["start_date"])
            new_end_date = max(repo_doc["end_date"], repo["end_date"])

            collection.update_one(
                {"name": repo["name"]},
                {
                    "$set": {
                        "commits": new_commits,
                        "commit_frequency": new_commit_frequency,
                        "start_date": new_start_date,
                        "end_date": new_end_date,
                    }
                },
            )
        else:
            collection.insert_one(repo)

        message_count += 1

        # Print top 10 projects every save_interval messages
        if message_count % save_interval == 0:
            most_commits = collection.find().sort("commits", -1).limit(10)
            most_frequent_commits = (
                collection.find().sort("commit_frequency", -1).limit(10)
            )

            print("Top 10 projects by total commits: ")
            for doc in most_commits:
                print(
                    f'Name: {doc["name"]}, Commits: {doc["commits"]}, Frequency: {doc["commit_frequency"]}, Start Date: {doc["start_date"]}, End Date: {doc["end_date"]}'
                )

            print("Top 10 projects by commit frequency: ")
            for doc in most_frequent_commits:
                print(
                    f'Name: {doc["name"]}, Commits: {doc["commits"]}, Frequency: {doc["commit_frequency"]}, Start Date: {doc["start_date"]}, End Date: {doc["end_date"]}'
                )

        consumer.acknowledge(msg)
    except Exception as e:
        print("Error: ", e)

client.close()

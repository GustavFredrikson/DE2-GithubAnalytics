import pulsar
import json
import pandas as pd

client = pulsar.Client("pulsar://pulsar-proxy.pulsar.svc.cluster.local:6650")
consumer = client.subscribe("DevOpsSubtopic", "my-subscription")

df = pd.DataFrame(columns=["language", "count"])
df.set_index("language", inplace=True)

df["count"] = df["count"].astype("int")

message_count = 0
save_interval = 10

# If file exists, load it
try:
    df = pd.read_csv("tdd_devops_counts.csv", index_col="language")
    df["count"] = df["count"].astype("int")
except FileNotFoundError:
    pass


# DevOps-related keywords
devops_keywords = ["continuous integration", "ci", "cd", "pipeline"]

while True:
    try:
        msg = consumer.receive()
        repo = json.loads(msg.data())

        uses_devops = any(
            any(keyword in workflow["name"].lower() for keyword in devops_keywords)
            for workflow in repo["workflows"]
        )

        if repo["uses_tdd"] and uses_devops:  # both TDD and DevOps
            for language in repo["languages"]:
                if language in df.index:
                    df.loc[language, "count"] += 1
                else:
                    df.at[language, "count"] = 1

        message_count += 1

        # Save all data to file every save_interval messages
        if message_count % save_interval == 0:
            top_languages = df.nlargest(10, "count")
            print(
                "Top 10 languages by number of projects using TDD and DevOps: ",
                top_languages,
            )

            df.sort_values(by="count", ascending=False, inplace=True)
            df.to_csv("tdd_devops_counts.csv")

        consumer.acknowledge(msg)
    except Exception as e:
        with open("devops_consumer.log", "a") as f:
            print(e, file=f)
        print(e)

client.close()

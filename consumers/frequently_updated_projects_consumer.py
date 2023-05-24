import pulsar
import json
import pandas as pd

client = pulsar.Client("pulsar://localhost:6650")
consumer = client.subscribe("CommitsTopic", "my-subscription")

df = pd.DataFrame(columns=["name", "commits"])
df.set_index("name", inplace=True)

df["commits"] = df["commits"].astype("int")

message_count = 0
save_interval = 1000

# If file exists, load it
try:
    df = pd.read_csv("most_commits.csv", index_col="name")
except:
    pass

while True:
    try:
        msg = consumer.receive()
        repo = json.loads(msg.data())

        if repo["name"] in df.index:
            df.loc[repo["name"], "commits"] += int(
                repo["commits"]
            )  # Ensure it's integer
        else:
            df.at[repo["name"], "commits"] = int(repo["commits"])  # Ensure it's integer

        message_count += 1

        most_commits = df.nlargest(10, "commits")
        print("Top 10 frequently updated projects: ", most_commits)

        # Save to file every save_interval messages
        if message_count % save_interval == 0:
            most_commits.to_csv("most_commits.csv")

        consumer.acknowledge(msg)
    except Exception as e:
        print("Error: ", e)

client.close()

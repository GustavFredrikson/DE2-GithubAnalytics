import pulsar
import json
import pandas as pd

client = pulsar.Client("pulsar://localhost:6650")
consumer = client.subscribe("CommitsTopic", "my-subscription")

df = pd.DataFrame(columns=["name", "commits", "commit_frequency"])
df.set_index("name", inplace=True)

df["commits"] = df["commits"].astype("int")
df["commit_frequency"] = df["commit_frequency"].astype("float")

message_count = 0
save_interval = 1000

# If file exists, load it
try:
    df = pd.read_csv("most_commits.csv", index_col="name")
except FileNotFoundError:
    pass

while True:
    try:
        msg = consumer.receive()
        repo = json.loads(msg.data())

        if repo["name"] in df.index:
            df.loc[repo["name"], "commits"] += int(
                repo["commits"]
            )  # Ensure it's integer
            df.loc[repo["name"], "commit_frequency"] = (
                df.loc[repo["name"], "commit_frequency"] + repo["commit_frequency"]
            ) / 2  # Average frequency
        else:
            df.at[repo["name"], "commits"] = int(repo["commits"])  # Ensure it's integer
            df.at[repo["name"], "commit_frequency"] = repo["commit_frequency"]

        message_count += 1

        most_commits = df.nlargest(10, "commits")
        print("Top 10 projects by total commits: ", most_commits)

        most_frequent_commits = df.nlargest(10, "commit_frequency")
        print("Top 10 projects by commit frequency: ", most_frequent_commits)

        # Save all data to file every save_interval messages
        if message_count % save_interval == 0:
            df.to_csv("most_commits.csv")

        consumer.acknowledge(msg)
    except Exception as e:
        print("Error: ", e)

client.close()

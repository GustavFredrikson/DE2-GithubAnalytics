import pulsar
import json
import pandas as pd

# Configure the logging settings

client = pulsar.Client("pulsar://pulsar-proxy.pulsar.svc.cluster.local:6650")
consumer = client.subscribe("CommitsTopic", "my-subscription")

df = pd.DataFrame(
    columns=["name", "commits", "commit_frequency", "start_date", "end_date"]
)
df.set_index("name", inplace=True)

df["commits"] = df["commits"].astype("int")
df["commit_frequency"] = df["commit_frequency"].astype("float")

message_count = 0
save_interval = 10

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
            df.loc[repo["name"], "start_date"] = min(
                df.loc[repo["name"], "start_date"], repo["start_date"]
            )
            df.loc[repo["name"], "end_date"] = max(
                df.loc[repo["name"], "end_date"], repo["end_date"]
            )
        else:
            df.at[repo["name"], "commits"] = int(repo["commits"])  # Ensure it's integer
            df.at[repo["name"], "commit_frequency"] = repo["commit_frequency"]
            df.at[repo["name"], "start_date"] = repo["start_date"]
            df.at[repo["name"], "end_date"] = repo["end_date"]

        message_count += 1

        most_commits = df.nlargest(10, "commits")
        print("Top 10 projects by total commits: ", most_commits)

        most_frequent_commits = df.nlargest(10, "commit_frequency")
        print("Top 10 projects by commit frequency: ", most_frequent_commits)

        # Save all data to file every save_interval messages
        if message_count % save_interval == 0:
            df.sort_values(by="commits", ascending=False, inplace=True)
            df.to_csv("most_commits.csv")

        consumer.acknowledge(msg)
    except Exception as e:
        print("Error: ", e)

client.close()

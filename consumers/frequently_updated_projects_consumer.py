import pulsar
import json
import pandas as pd

client = pulsar.Client("pulsar://localhost:6650")
consumer = client.subscribe("CommitsTopic", "my-subscription")

df = pd.DataFrame(columns=["name", "commits"])
df.set_index("name", inplace=True)

while True:
    msg = consumer.receive()
    repo = json.loads(msg.data())

    if repo["name"] in df.index:
        df.loc[repo["name"], "commits"] += repo["commits"]
    else:
        df.loc[repo["name"]] = {"commits": repo["commits"]}

    most_commits = df.nlargest(10, "commits")
    print("Top 10 frequently updated projects: ", most_commits)
    consumer.acknowledge(msg)

client.close()

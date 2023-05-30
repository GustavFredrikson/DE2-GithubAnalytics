import pulsar
import json
import pandas as pd

client = pulsar.Client("pulsar://pulsar-proxy.pulsar.svc.cluster.local:6650")
consumer = client.subscribe("WorkflowTopic", "my-subscription")

df = pd.DataFrame(columns=["name", "has_ci_cd"])
df.set_index("name", inplace=True)

message_count = 0
save_interval = 100

while True:
    try:
        msg = consumer.receive()
        repo = json.loads(msg.data())

        df.at[repo["name"], "has_ci_cd"] = repo["has_ci_cd"]

        message_count += 1

        if message_count % save_interval == 0:
            df.to_csv("devops.csv")

        consumer.acknowledge(msg)
    except Exception as e:
        print("Error: ", e)

client.close()

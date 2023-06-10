import pulsar
import os
import time
import json
import pandas as pd
from decouple import config

# Configuration
TOKEN = config("GITHUB_API_TOKEN")

client = pulsar.Client("pulsar://pulsar-proxy.pulsar.svc.cluster.local:6650")
consumer = client.subscribe("WorkflowTopic", "my-subscription")

df = pd.DataFrame(columns=["name", "has_ci_cd"])
df.set_index("name", inplace=True)

message_count = 0
save_interval = 100


TERMINATE_AFTER_N_MESSAGES = config("TERMINATE_AFTER_N_MESSAGES", cast=int, default=1000)
print(f"Will terminate after {TERMINATE_AFTER_N_MESSAGES} messages")

with open('dc_start', 'w') as f:
    f.write(str(time.time()))
n_messages = 0
while True:
    try:
        msg = consumer.receive()
        repo = json.loads(msg.data())

        df.at[repo["name"], "has_ci_cd"] = repo["has_ci_cd"]

        message_count += 1

        if message_count % save_interval == 0:
            df.to_csv("devops.csv")

        consumer.acknowledge(msg)
        n_messages += 1
        if n_messages >= TERMINATE_AFTER_N_MESSAGES:
            break
    except Exception as e:
        print("Error: ", e)

with open('dc_end', 'w') as f:
    f.write(str(time.time()))
client.close()

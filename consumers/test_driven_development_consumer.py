import pulsar
import os
import time
import json
import pandas as pd
from decouple import config

client = pulsar.Client("pulsar://pulsar-proxy.pulsar.svc.cluster.local:6650")
consumer = client.subscribe("TDDTopic", "my-subscription")

df = pd.DataFrame(columns=["name", "has_tests"])
df.set_index("name", inplace=True)

message_count = 0
save_interval = 100

TERMINATE_AFTER_N_MESSAGES = config("TERMINATE_AFTER_N_MESSAGES", cast=int, default=1000)
print(f"Will terminate after {TERMINATE_AFTER_N_MESSAGES} messages")

n_messages = 0

with open("tdd_start", "w") as f:
    f.write(str(time.time()))
while True:
    try:
        msg = consumer.receive()
        repo = json.loads(msg.data())

        df.at[repo["name"], "has_tests"] = repo["has_tests"]

        message_count += 1

        # Save all data to file every save_interval messages
        if message_count % save_interval == 0:
            df.to_csv("test_driven_development.csv")

        consumer.acknowledge(msg)
        n_messages += 1
        if n_messages >= TERMINATE_AFTER_N_MESSAGES:
            break
    except Exception as e:
        print("Error: ", e)

with open("tdd_end", "w") as f:
    f.write(str(time.time()))
client.close()

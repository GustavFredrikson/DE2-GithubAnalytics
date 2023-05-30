import pulsar
import json
import pandas as pd

client = pulsar.Client("pulsar://pulsar-proxy.pulsar.svc.cluster.local:6650")
consumer = client.subscribe("TDDTopic", "my-subscription")

df = pd.DataFrame(columns=["name", "has_tests"])
df.set_index("name", inplace=True)

message_count = 0
save_interval = 100

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
    except Exception as e:
        print("Error: ", e)

client.close()

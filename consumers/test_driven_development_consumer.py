import pulsar
import json
import pandas as pd

client = pulsar.Client("pulsar://pulsar-proxy.pulsar.svc.cluster.local:6650")
consumer = client.subscribe("TDDTopic", "my-subscription")

df = pd.DataFrame(columns=["language", "count"])
df.set_index("language", inplace=True)

df["count"] = df["count"].astype("int")

message_count = 0
save_interval = 10

while True:
    try:
        msg = consumer.receive()
        repo = json.loads(msg.data())

        if repo["uses_tdd"]:
            for language in repo["languages"]:
                if language in df.index:
                    df.loc[language, "count"] += 1
                else:
                    df.at[language, "count"] = 1

        message_count += 1

        # Save all data to file every save_interval messages
        if message_count % save_interval == 0:
            top_languages = df.nlargest(10, "count")
            print("Top 10 languages by number of projects using TDD: ", top_languages)

            df.sort_values(by="count", ascending=False, inplace=True)
            df.to_csv("tdd_counts.csv")

        consumer.acknowledge(msg)
    except Exception as e:
        with open("tdd_consumer.log", "a") as f:
            print(e, file=f)
        print("Error: ", e)

client.close()

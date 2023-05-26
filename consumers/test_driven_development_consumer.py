import pulsar
import json
import pandas as pd

client = pulsar.Client("pulsar://pulsar-proxy.pulsar.svc.cluster.local:6650")
consumer = client.subscribe("TDDTopic", "my-subscription")

df = pd.DataFrame(columns=["language", "count"])
df.set_index("language", inplace=True)

df["count"] = df["count"].astype("int")

with open("tdd_consumer.log", "w") as f:
    print("Starting TDD Consumer", file=f)

message_count = 0
save_interval = 10

count = 0
while True:
    print(f"TDD Consumer: {count}")
    count += 1
    try:
        msg = consumer.receive()
        repo = json.loads(msg.data())

        if repo["uses_tdd"]:
            for language in repo.get("languages", ["No Language"]):
                if language in df.index:
                    df.loc[language, "count"] += 1
                else:
                    df.at[language, "count"] = 1

            message_count += 1

            # Save all data to file every save_interval messages
            top_languages = df.nlargest(10, "count")
            print("Top 10 languages by number of projects using TDD: ", top_languages)
            with open("tdd_consumer.log", "a") as f:
                print(
                    "Top 10 languages by number of projects using TDD: ",
                    top_languages,
                    file=f,
                )

            df.sort_values(by="count", ascending=False, inplace=True)
            df.to_csv("tdd_counts.csv")

        consumer.acknowledge(msg)
    except Exception as e:
        with open("tdd_consumer.log", "a") as f:
            print("Error: ", e, file=f)
        print("Error: ", e)

client.close()

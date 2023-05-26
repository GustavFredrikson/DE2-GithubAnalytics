import pulsar
import json
import pandas as pd

client = pulsar.Client("pulsar://pulsar-proxy.pulsar.svc.cluster.local:6650")

consumer = client.subscribe("LanguagesTopic", "my-subscription")

# DataFrame to keep track of language counts
df = pd.DataFrame(columns=["language", "count"])
df.set_index("language", inplace=True)

df["count"] = df["count"].astype("int")

message_count = 0
save_interval = 10

# If file exists, load it
try:
    df = pd.read_csv("top_languages.csv", index_col="language")
    df["language"].fillna("No Language", inplace=True)
except FileNotFoundError:
    pass

try:
    while True:
        msg = consumer.receive()
        repo = json.loads(msg.data())

        repo_language = repo["language"] if repo.get("language") else "No Language"

        # Update the DataFrame with the language of the new repository
        if repo_language in df.index:
            df.loc[repo_language, "count"] += 1
        else:
            df.at[repo_language, "count"] = 1

        message_count += 1

        # Save to file every save_interval messages
        if message_count % save_interval == 0:
            top_languages = df.nlargest(10, "count")
            print("Top 10 languages: ", top_languages)
            df.sort_values(by="count", ascending=False, inplace=True)
            df.to_csv("top_languages.csv")

        # Acknowledge processing of message so that it can be deleted
        consumer.acknowledge(msg)

except Exception as e:
    print("Error: ", e)

finally:
    client.close()

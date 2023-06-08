import pulsar
import time
import json
import pandas as pd
from decouple import config

client = pulsar.Client("pulsar://pulsar-proxy.pulsar.svc.cluster.local:6650")

with open('plc_time_start', 'w') as f:
    f.write(str(time.time()))
consumer = client.subscribe("LanguagesTopic", "my-subscription")

df = pd.DataFrame(columns=["language", "count"])
df.set_index("language", inplace=True)

df["count"] = df["count"].astype("int")

message_count = 0
save_interval = 1000

TERMINATE_AFTER_N_MESSAGES = config("TERMINATE_AFTER_N_MESSAGES", cast=int, default=1000)

n_messages = 0

with open('plc_time_start', 'w') as f:
    f.write(str(time.time()))
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
            # print("Top 10 languages: ", top_languages)
            df.sort_values(by="count", ascending=False, inplace=True)
            df.to_csv("top_languages.csv")


        consumer.acknowledge(msg)
        n_messages += 1
        if n_messages >= TERMINATE_AFTER_N_MESSAGES:
            break

except Exception as e:
    print("Error: ", e)

finally:
    with open('plc_time_end', 'w') as f:
        f.write(str(time.time()))
    client.close()

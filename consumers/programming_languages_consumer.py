import pulsar
import json
import pandas as pd

client = pulsar.Client("pulsar://localhost:6650")

consumer = client.subscribe("ProgrammingLanguagesTopic", "my-subscription")

# DataFrame to keep track of language counts
df = pd.DataFrame(columns=["language", "count"])
df.set_index("language", inplace=True)

while True:
    try:
        msg = consumer.receive()
        repo = json.loads(msg.data())

        # Update the DataFrame with the language of the new repository
        if repo["language"] in df.index:
            df.loc[repo["language"], "count"] += 1
        else:
            df.loc[repo["language"]] = {"count": 1}

        # Calculate and print the top 10 languages
        top_languages = df.nlargest(10, "count")
        print("Top 10 languages: ", top_languages)

        # Acknowledge processing of message so that it can be deleted
        consumer.acknowledge(msg)
    except Exception as e:
        print("Error: ", e)

client.close()

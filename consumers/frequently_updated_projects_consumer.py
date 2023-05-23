import pulsar
import json
from collections import Counter

# Pulsar client
client = pulsar.Client("pulsar://localhost:6650")

# Pulsar consumer
consumer = client.subscribe("FrequentlyUpdatedProjectsTopic", "projects_subscriber")

# Counter for repository commits
commits_counts = Counter()

if __name__ == "__main__":
    try:
        while True:
            # Receive messages from the FrequentlyUpdatedProjectsTopic
            msg = consumer.receive()

            try:
                # Decode the message
                project_info = json.loads(msg.data())

                # Update the commits counts
                commits_counts[project_info["name"]] += project_info["commits"]

                # Acknowledge successful processing of the message
                consumer.acknowledge(msg)

            except:
                # Message failed to process
                consumer.negative_acknowledge(msg)

    finally:
        # Print the top 10 repositories with the most commits
        for repo, count in commits_counts.most_common(10):
            print(f"{repo}: {count}")

        # Close the client
        client.close()

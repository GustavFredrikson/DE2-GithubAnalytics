from pulsar import ConsumerType
import pulsar
import json
from collections import defaultdict

# Pulsar client
client = pulsar.Client("pulsar://localhost:6650")

# Pulsar consumer
consumer = client.subscribe(
    "LanguageTopic", "language_consumer_sub", consumer_type=ConsumerType.Shared
)

# Maintain a count of the number of repositories for each language
language_counts = defaultdict(int)

try:
    while True:
        # Receive messages from the LanguageTopic
        msg = consumer.receive()

        try:
            # Decode the message
            language_data = json.loads(msg.data())

            # Update the language counts
            if language_data["language"] is not None:
                language_counts[language_data["language"]] += 1

            # Acknowledge successful processing of the message
            consumer.acknowledge(msg)

        except:
            # Message failed to process
            consumer.negative_acknowledge(msg)

finally:
    # Close the client
    client.close()

# Print the counts
for language, count in language_counts.items():
    print(f"{language}: {count}")

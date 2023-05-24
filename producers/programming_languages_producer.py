from pulsar import ConsumerType
import pulsar
import json
from decouple import config

# Pulsar client
client = pulsar.Client("pulsar://localhost:6650")

# Pulsar consumers and producers
consumer = client.subscribe(
    "MainGithubRepoTopic", "language_producer_sub", consumer_type=ConsumerType.Shared
)
producer = client.create_producer("LanguageTopic")

try:
    while True:
        # Receive messages from the MainGitHubRepoTopic
        msg = consumer.receive()

        try:
            # Decode the message
            repo = json.loads(msg.data())

            # Send only the language data to the LanguageTopic
            language_data = {"id": repo["id"], "language": repo["language"]}
            producer.send(json.dumps(language_data).encode("utf-8"))

            # Acknowledge successful processing of the message
            consumer.acknowledge(msg)

        except:
            # Message failed to process
            consumer.negative_acknowledge(msg)

finally:
    # Close the client
    client.close()

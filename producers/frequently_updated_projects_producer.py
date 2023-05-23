import pulsar
import json

# Pulsar client
client = pulsar.Client("pulsar://localhost:6650")

# Pulsar consumers
main_consumer = client.subscribe("MainGithubRepoTopic", "main_subscriber")

# Pulsar producer
producer = client.create_producer("FrequentlyUpdatedProjectsTopic")


if __name__ == "__main__":
    try:
        while True:
            # Receive messages from the MainGitHubRepoTopic
            msg = main_consumer.receive()

            try:
                # Decode the message
                repo = json.loads(msg.data())

                # Extract and send the relevant information
                project_info = {
                    "name": repo["name"],
                    "commits": repo["commits"],
                }
                producer.send(json.dumps(project_info).encode("utf-8"))

                # Acknowledge successful processing of the message
                main_consumer.acknowledge(msg)

            except:
                # Message failed to process
                main_consumer.negative_acknowledge(msg)

    finally:
        # Close the client
        client.close()

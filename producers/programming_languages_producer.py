import pulsar
import json

client = pulsar.Client("pulsar://localhost:6650")

consumer = client.subscribe("MainGithubRepoTopic", "my-subscription")
producer = client.create_producer("ProgrammingLanguagesTopic")

while True:
    try:
        msg = consumer.receive()
        repo = json.loads(msg.data())
        print(f"Received message: '{repo}' id='{msg.message_id()}'")

        # Forward data to the ProgrammingLanguagesTopic
        producer.send(
            json.dumps({"name": repo["name"], "language": repo["language"]}).encode(
                "utf-8"
            )
        )

        # Acknowledge processing of message so that it can be deleted
        consumer.acknowledge(msg)
    except Exception as e:
        print("Error: ", e)

client.close()

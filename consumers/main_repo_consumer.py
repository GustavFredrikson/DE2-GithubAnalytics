import pulsar
import json

client = pulsar.Client("pulsar://localhost:6650")

consumer = client.subscribe("MainGithubRepoTopic", "my-subscription")

while True:
    try:
        msg = consumer.receive()
        repo = json.loads(msg.data())
        print(f"Received message: '{repo}' id='{msg.message_id()}'")

        # Acknowledge processing of message so that it can be deleted
        consumer.acknowledge(msg)
    except Exception as e:
        print("Error: ", e)

client.close()

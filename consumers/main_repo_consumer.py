import pulsar
import os
import time
import json
from decouple import config

client = pulsar.Client("pulsar://pulsar-proxy.pulsar.svc.cluster.local:6650")

consumer = client.subscribe("MainGithubRepoTopic", "my-subscription")

producer_languages = client.create_producer("ProgrammingLanguagesTopic")
producer_updates = client.create_producer("FrequentlyUpdatedProjectsTopic")
producer_tdd = client.create_producer("TestDrivenDevelopmentTopic")
producer_devops = client.create_producer("DevopsTopic")


TERMINATE_AFTER_N_MESSAGES = config("TERMINATE_AFTER_N_MESSAGES", cast=int, default=1000)*2
print(f"Will terminate after {TERMINATE_AFTER_N_MESSAGES} messages")

n_messages = 0
while True:
    try:
        msg = consumer.receive()
        repo = json.loads(msg.data())

        # Forward data to other topics, TODO: only send necessary data
        producer_languages.send(json.dumps(repo).encode("utf-8"))
        producer_updates.send(json.dumps(repo).encode("utf-8"))
        producer_tdd.send(json.dumps(repo).encode("utf-8"))
        producer_devops.send(json.dumps(repo).encode("utf-8"))

        # Acknowledge processing of message so that it can be deleted
        consumer.acknowledge(msg)
        n_messages += 1
        if n_messages >= TERMINATE_AFTER_N_MESSAGES:
            break
    except Exception as e:
        print("Error: ", e)

client.close()

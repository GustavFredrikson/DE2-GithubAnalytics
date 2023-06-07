import pulsar
import json

client = pulsar.Client("pulsar://pulsar-proxy.pulsar.svc.cluster.local:6650")

consumer = client.subscribe("MainGithubRepoTopic", "my-subscription")

producer_languages = client.create_producer("ProgrammingLanguagesTopic")
producer_updates = client.create_producer("FrequentlyUpdatedProjectsTopic")
producer_tdd = client.create_producer("TestDrivenDevelopmentTopic")
producer_devops = client.create_producer("DevopsTopic")

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
    except Exception as e:
        print("Error: ", e)

client.close()

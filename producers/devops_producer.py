import pulsar
import json
from decouple import config

client = pulsar.Client("pulsar://pulsar-proxy.pulsar.svc.cluster.local:6650")
consumer = client.subscribe("TddToDevOpsTopic", "my-subscription")
devops_producer = client.create_producer("DevOpsSubtopic")

while True:
    try:
        msg = consumer.receive()
        repo = json.loads(msg.data())

        # The repo data is already complete as it's coming from the TDD Producer,
        # So, we just forward it to the DevOps Consumer.
        devops_producer.send(msg.data())
        consumer.acknowledge(msg)

    except Exception as e:
        print("Error: ", e)

client.close()

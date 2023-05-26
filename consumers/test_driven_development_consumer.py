import pulsar
import json
from collections import defaultdict

client = pulsar.Client("pulsar://pulsar-proxy.pulsar.svc.cluster.local:6650")
consumer = client.subscribe("TestDrivenDevelopmentTopic", "my-subscription")

language_tdd_counts = defaultdict(int)

while True:
    msg = consumer.receive()
    repo = json.loads(msg.data())

    if repo["uses_tdd"]:
        for language in repo["languages"]:
            language_tdd_counts[language] += 1

    consumer.acknowledge(msg)

# At this point, `language_tdd_counts` contains the counts of projects using TDD for each language.
# You can sort this dictionary to get the top 10 languages, for example.

client.close()

import pulsar
import requests
import json
from decouple import config
import time
from datetime import datetime


TOKEN = config("GITHUB_API_TOKEN")
HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28",
}
WORKFLOWS_BASE_URL = "https://api.github.com/repos/{owner}/{repo}/actions/workflows"
RATE_LIMIT_URL = "https://api.github.com/rate_limit"

client = pulsar.Client("pulsar://pulsar-proxy.pulsar.svc.cluster.local:6650")
consumer = client.subscribe("MainGitHubRepositoryInfoTopic", "my-subscription")
producer = client.create_producer("TestDrivenDevelopmentTopic")


def check_rate_limit():
    response = requests.get(RATE_LIMIT_URL, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    core_remaining = data["resources"]["core"]["remaining"]
    core_reset = data["resources"]["core"]["reset"]
    return core_remaining, core_reset


while True:
    msg = consumer.receive()
    repo = json.loads(msg.data())

    url = WORKFLOWS_BASE_URL.format(owner=repo["owner"]["login"], repo=repo["name"])

    try:
        core_remaining, core_reset = check_rate_limit()
        if core_remaining < 100:  # Or any threshold you like
            reset_time = datetime.fromtimestamp(core_reset)
            sleep_seconds = (reset_time - datetime.now()).total_seconds()
            print(f"Rate limit low. Sleeping for {sleep_seconds} seconds.")
            time.sleep(sleep_seconds + 1)
        else:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()

            data = response.json()
            workflows = data["workflows"]
            repo["uses_tdd"] = any(
                workflow["name"].lower() == "test" for workflow in workflows
            )

            producer.send(json.dumps(repo).encode("utf-8"))
            consumer.acknowledge(msg)

    except requests.exceptions.HTTPError as e:
        print(e)
        consumer.acknowledge(msg)

client.close()

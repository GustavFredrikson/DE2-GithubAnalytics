import pulsar
import requests
import json
from decouple import config

TOKEN = config("GITHUB_API_TOKEN")
HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28",
}
RATE_LIMIT_URL = "https://api.github.com/rate_limit"

client = pulsar.Client("pulsar://pulsar-proxy.pulsar.svc.cluster.local:6650")
consumer = client.subscribe("TestDrivenDevelopmentTopic", "my-subscription")
producer = client.create_producer("TDDTopic")


def check_rate_limit():
    response = requests.get(RATE_LIMIT_URL, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    core_remaining = data["resources"]["core"]["remaining"]
    core_reset = data["resources"]["core"]["reset"]
    return core_remaining, core_reset


def has_tests(repo_name):
    contents_url = f'https://api.github.com/repos/{repo_name}/contents'
    contents_response = requests.get(contents_url, headers=HEADERS)
    contents_data = contents_response.json()
    return isinstance(contents_data, list) and any(
        content["name"].lower() in {"tests", "test"} for content in contents_data
    )


while True:
    msg = consumer.receive()
    repo = json.loads(msg.data())

    try:
        repo_with_tests = repo
        repo_with_tests["has_tests"] = has_tests(repo["full_name"])

        producer.send(json.dumps(repo_with_tests).encode("utf-8"))
        consumer.acknowledge(msg)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code in {403, 404, 409}:
            # The repository is empty, was deleted, or only contains git submodules, skip it
            continue
        else:
            print(f"Error: {e.response.status_code} - {e.response.reason}")
            consumer.acknowledge(msg)
    except Exception as e:
        print("Error: ", e)
        consumer.acknowledge(msg)

client.close()

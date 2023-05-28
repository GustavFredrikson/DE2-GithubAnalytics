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
consumer = client.subscribe("DevopsTopic", "my-subscription")
producer = client.create_producer("WorkflowTopic")


def check_rate_limit():
    response = requests.get(RATE_LIMIT_URL, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    core_remaining = data["resources"]["core"]["remaining"]
    core_reset = data["resources"]["core"]["reset"]
    return core_remaining, core_reset


def has_ci_cd(repo_name):
    workflows_url = f'https://api.github.com/repos/{repo_name}/actions/workflows'
    workflows_response = requests.get(workflows_url, headers=HEADERS)
    workflows_data = workflows_response.json()
    return any('ci' in workflow['name'].lower() or 'cd' in workflow['name'].lower() for workflow in workflows_data.get('workflows', []))


while True:
    msg = consumer.receive()
    repo = json.loads(msg.data())

    try:
        repo_with_ci_cd = repo
        repo_with_ci_cd["has_ci_cd"] = has_ci_cd(repo["full_name"])

        producer.send(json.dumps(repo_with_ci_cd).encode("utf-8"))
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

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
consumer = client.subscribe("TestDrivenDevelopmentTopic", "my-subscription")
producer = client.create_producer("TDDTopic")
devops_producer = client.create_producer("TddToDevOpsTopic")


def check_rate_limit():
    response = requests.get(RATE_LIMIT_URL, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    core_remaining = data["resources"]["core"]["remaining"]
    core_reset = data["resources"]["core"]["reset"]
    return core_remaining, core_reset


count = 0
while True:
    print(f"TDD Producer count: {count}")
    count += 1
    try:
        msg = consumer.receive()
        repo = json.loads(msg.data())

        url = WORKFLOWS_BASE_URL.format(owner=repo["owner"]["login"], repo=repo["name"])

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
                "test" in workflow["name"].lower() for workflow in workflows
            )
            for workflow in workflows:
                print(f"Repo: {repo['name']}, Workflow: {workflow['name']}")

            if repo["uses_tdd"]:
                print(f"{repo['name']} uses TDD with the workflows:")
                for workflow in workflows:
                    if "test" in workflow["name"].lower():
                        print(f"\t{workflow['name']}")

            producer.send(json.dumps(repo).encode("utf-8"))

            repo_with_workflows = repo.copy()  # create a copy of repo
            repo_with_workflows["workflows"] = workflows  # add workflows to repo data
            devops_producer.send(json.dumps(repo_with_workflows).encode("utf-8"))

            consumer.acknowledge(msg)

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:  # Too Many Requests
            core_remaining, core_reset = check_rate_limit()
            reset_time = datetime.fromtimestamp(core_reset)
            sleep_seconds = (reset_time - datetime.now()).total_seconds()
            print(f"Rate limit exceeded. Sleeping for {sleep_seconds} seconds.")
            time.sleep(sleep_seconds + 1)
        else:
            print(e)
            consumer.acknowledge(msg)
    except Exception as e:
        print(e)
        consumer.acknowledge(msg)

client.close()

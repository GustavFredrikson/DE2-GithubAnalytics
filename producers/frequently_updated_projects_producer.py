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
COMMITS_BASE_URL = "https://api.github.com/repos/{owner}/{repo}/commits"
PER_PAGE = 100

client = pulsar.Client("pulsar://localhost:6650")
consumer = client.subscribe("FrequentlyUpdatedProjectsTopic", "my-subscription")
producer = client.create_producer("CommitsTopic")

while True:
    msg = consumer.receive()
    repo = json.loads(msg.data())

    url = COMMITS_BASE_URL.format(owner=repo["owner"]["login"], repo=repo["name"])
    params = {"per_page": PER_PAGE, "page": 1}

    try:
        commits = 0
        while True:
            response = requests.get(url, headers=HEADERS, params=params)
            response.raise_for_status()
            commits += len(response.json())
            if "next" not in response.links:
                break
            params["page"] += 1

        repo_with_commits = repo
        repo_with_commits["commits"] = commits
        producer.send(json.dumps(repo_with_commits).encode("utf-8"))
        consumer.acknowledge(msg)

    except requests.exceptions.HTTPError as e:
        consumer.acknowledge(msg)

client.close()

import pulsar
import requests
import json
from decouple import config
from datetime import datetime

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
        first_commit_date = None
        last_commit_date = None
        while True:
            response = requests.get(url, headers=HEADERS, params=params)
            response.raise_for_status()

            data = response.json()
            commits += len(data)
            if len(data) > 0:
                current_first_commit_date = datetime.strptime(
                    data[-1]["commit"]["committer"]["date"], "%Y-%m-%dT%H:%M:%SZ"
                )
                current_last_commit_date = datetime.strptime(
                    data[0]["commit"]["committer"]["date"], "%Y-%m-%dT%H:%M:%SZ"
                )

                if (
                    first_commit_date is None
                    or current_first_commit_date < first_commit_date
                ):
                    first_commit_date = current_first_commit_date
                if (
                    last_commit_date is None
                    or current_last_commit_date > last_commit_date
                ):
                    last_commit_date = current_last_commit_date

            if "next" not in response.links:
                break
            params["page"] += 1

        repo_with_commits = repo
        repo_with_commits["commits"] = commits
        if first_commit_date and last_commit_date:
            days_difference = (
                last_commit_date - first_commit_date
            ).days or 1  # avoid division by zero
            repo_with_commits["commit_frequency"] = (
                commits / days_difference
            )  # average commits per day

        producer.send(json.dumps(repo_with_commits).encode("utf-8"))
        consumer.acknowledge(msg)

    except requests.exceptions.HTTPError as e:
        consumer.acknowledge(msg)

client.close()

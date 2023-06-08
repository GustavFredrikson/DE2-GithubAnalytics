import pulsar
from decouple import config
import requests
import json
import datetime
import time

# Configuration
TOKEN = config("GITHUB_API_TOKEN")
BASE_URL = "https://api.github.com/search/repositories"
HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28",
}
PER_PAGE = 100


# If we want to benchmark the script, we can set this to 
#the number of times we want to duplicate the results
PULSAR_BENCHMARK=100000

# Pulsar client
client = pulsar.Client("pulsar://pulsar-proxy.pulsar.svc.cluster.local:6650")

# Pulsar producer
producer = client.create_producer("MainGithubRepoTopic")

RATE_LIMIT_URL = "https://api.github.com/rate_limit"


def check_rate_limit():
    response = requests.get(RATE_LIMIT_URL, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    core_remaining = data["resources"]["core"]["remaining"]
    core_reset = data["resources"]["core"]["reset"]
    return core_remaining, core_reset


def fetch_repos(date):
    # Query parameters for the API request
    params = {
        "q": f"created:{date}..{date} pushed:{date}..{date}",
        "sort": "updated",
        "order": "desc",
        "per_page": PER_PAGE,
        "page": 1,
    }

    repos = []

    for _ in range(10):
        while True:
            core_remaining, core_reset = check_rate_limit()
            if core_remaining < 100:  # or whatever threshold you want
                reset_time = datetime.datetime.fromtimestamp(core_reset)
                sleep_seconds = (reset_time - datetime.datetime.now()).total_seconds()
                print(f"Rate limit low. Sleeping for {sleep_seconds} seconds.")
                time.sleep(sleep_seconds + 1)  # add a bit of extra time to be safe
            else:
                break
        try:
            # Make the API request
            response = requests.get(BASE_URL, headers=HEADERS, params=params)
            response.raise_for_status()

            # Add the repos from this page to our list
            repos.extend(response.json()["items"])

            # If this is the last page, break out of the loop
            if "next" not in response.links:
                break

            # Otherwise, increment the page number and continue
            params["page"] += 1

        except requests.exceptions.HTTPError as e:
            if e.response.status_code in {403, 404, 409, 502}:
                # The repository is empty, was deleted or only contains git submodules, skip it
                # print(
                #     f"Skipping repository: {repo['full_name']} - {e.response.status_code} (mrp)"
                # )
                continue
            else:
                print(f"Error: {e} (mrp)")
    return repos


if __name__ == "__main__":
    with open("mrp_time_start", "w") as f:
        f.write(str(time.time()))   
    min_date = datetime.date(2021, 1, 1)  # set to oldest date we want to use

    date = datetime.date.today()

    while date >= min_date:
        repos = fetch_repos(date)
        for _ in range(PULSAR_BENCHMARK) if PULSAR_BENCHMARK >= 1 else range(1):
            for repo in repos:
                producer.send(json.dumps(repo).encode("utf-8"))
        if PULSAR_BENCHMARK >= 1:
            print(f"Sent {len(repos)*PULSAR_BENCHMARK} messages for {date}")
            break

        date -= datetime.timedelta(days=1)

    client.close()
    with open("mrp_time_end", "w") as f:
        f.write(str(time.time()))

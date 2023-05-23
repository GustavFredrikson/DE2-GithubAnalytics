import requests
from decouple import config

RATE_LIMIT_URL = "https://api.github.com/rate_limit"
TOKEN = config("../GITHUB_API_TOKEN")
HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28",
}


def check_rate_limit():
    response = requests.get(RATE_LIMIT_URL, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    core_remaining = data["resources"]["core"]["remaining"]
    core_reset = data["resources"]["core"]["reset"]
    return core_remaining, core_reset

import requests
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import concurrent.futures

N_DAYS = 1

# Your GitHub personal access token
TOKEN = ""

# The base URL for the GitHub Search Repositories API
BASE_URL = "https://api.github.com/search/repositories"

# Headers for the API request
HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28",
}

# The maximum number of results per page
PER_PAGE = 100


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
    # use tqdm to make a while loop with a progress bar
    for _ in tqdm(range(10), desc=f"Fetching repos for {date}"):
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
            if e.response.status_code in {403, 404, 409}:
                # The repository is empty, was deleted or only contains git submodules, skip it
                tqdm.write(f"Skipping repo due to HTTP error: {e}")
                continue
            else:
                raise e

    return repos


COMMITS_BASE_URL = "https://api.github.com/repos/{owner}/{repo}/commits"


def fetch_commits(owner, repo):
    # URL for the API request
    url = COMMITS_BASE_URL.format(owner=owner, repo=repo)

    try:
        # Make the API request
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()

        # Return the number of commits
        return len(response.json())

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 409 or e.response.status_code == 404:
            # The repository is empty, was deleted or only contains git submodules, skip it
            return 0
        else:
            raise e


def fetch_commits_for_row(row):
    # Fetch the number of commits for this repository
    return fetch_commits(row["owner"]["login"], row["name"])


def analyze_repos(repos):
    # Convert the list of repos to a DataFrame
    df = pd.DataFrame(repos)

    # Fetch the number of commits for each repository
    with concurrent.futures.ThreadPoolExecutor() as executor:
        df["commits"] = list(
            tqdm(executor.map(fetch_commits_for_row, df.to_dict("records"))),
            total=len(df),
        )

    # Q1: Top 10 programming languages based on the number of projects developed
    language_counts = df["language"].value_counts()
    top_languages = language_counts.nlargest(10)

    # Q2: Top 10 repositories with the most commits
    most_commits = df.nlargest(10, "commits")

    return top_languages, most_commits


def plot_data(top_languages, most_commits):
    # Q1: Plot the top 10 programming languages
    plt.figure(figsize=(10, 6))
    top_languages.plot(kind="bar")
    plt.title("Top 10 Programming Languages")
    plt.xlabel("Language")
    plt.ylabel("Number of Projects")
    plt.show()

    # Q2: Plot the top 10 repositories with the most commits
    plt.figure(figsize=(10, 6))
    most_commits.set_index("name")["commits"].plot(kind="bar")
    plt.title("Top 10 Repositories with the Most Commits")
    plt.xlabel("Repository")
    plt.ylabel("Number of Commits")
    plt.show()


def main():
    # make a list of dates from today to n_days ago
    dates = [datetime.date.today() - datetime.timedelta(days=i) for i in range(N_DAYS)]

    # Fetch the repos created or updated on each date
    repos = [fetch_repos(date) for date in dates]

    # Flatten the list of lists
    repos = [repo for sublist in repos for repo in sublist]

    # Analyze the repos
    top_languages, most_frequently_updated = analyze_repos(repos)

    # Plot the data
    plot_data(top_languages, most_frequently_updated)


if __name__ == "__main__":
    main()

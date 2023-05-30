import requests
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import concurrent.futures
from decouple import config
import swifter
import time


N_DAYS = 5

# Your GitHub personal access token, from .env
TOKEN = config("GITHUB_API_TOKEN")

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
RATE_LIMIT_URL = "https://api.github.com/rate_limit"


def check_rate_limit():
    """
    Check the rate limit of the API.
    If the rate limit has been exceeded, sleeps until it resets.
    """
    response = requests.get(RATE_LIMIT_URL, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    core_remaining = data["resources"]["core"]["remaining"]
    core_reset = data["resources"]["core"]["reset"]
    if core_remaining < 1000:
        sleep_time = core_reset - time.time()
        if sleep_time > 0:
            print(
                f"Rate limit close to being exceeded. Sleeping for {sleep_time} seconds."
            )
            time.sleep(sleep_time)
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
                # The repository is empty, was deleted, or only contains git submodules, skip it
                tqdm.write(f"Skipping repo due to HTTP error: {e}")
                continue
            else:
                raise e

    return repos


COMMITS_BASE_URL = "https://api.github.com/repos/{owner}/{repo}/commits"


def fetch_commits(owner, repo):
    # URL for the API request
    url = COMMITS_BASE_URL.format(owner=owner, repo=repo)
    params = {"per_page": PER_PAGE, "page": 1}

    commits = 0
    while True:
        try:
            # Make the API request
            response = requests.get(url, headers=HEADERS, params=params)
            response.raise_for_status()

            # Add the number of commits from this page
            commits += len(response.json())

            # If this is the last page, break out of the loop
            if "next" not in response.links:
                break

            # Otherwise, increment the page number and continue
            params["page"] += 1

        except requests.exceptions.HTTPError as e:
            if e.response.status_code in {403, 404, 409}:
                # The repository is empty, was deleted, or only contains git submodules, skip it
                return commits
            else:
                raise e

    return commits


def fetch_commits_for_row(row):
    # Fetch the number of commits for this repository
    return fetch_commits(row["owner"]["login"], row["name"])


def analyze_repos(repos):
    # Check if the repository has a 'tests' or 'test' directory
    def has_tests(repo_name):
        contents_url = f"https://api.github.com/repos/{repo_name}/contents"
        contents_response = requests.get(contents_url, headers=HEADERS)
        contents_data = contents_response.json()
        return isinstance(contents_data, list) and any(
            content["name"].lower() in {"tests", "test"} for content in contents_data
        )

    # Check if the repository has a CI/CD workflow
    def has_ci_cd(repo_name):
        workflows_url = f"https://api.github.com/repos/{repo_name}/actions/workflows"
        workflows_response = requests.get(workflows_url, headers=HEADERS)
        workflows_data = workflows_response.json()
        return any(
            "ci" in workflow["name"].lower() or "cd" in workflow["name"].lower()
            for workflow in workflows_data.get("workflows", [])
        )

    # Convert the list of repos to a DataFrame
    df = pd.DataFrame(repos)

    # Q1: Top 10 programming languages based on the number of projects developed
    language_counts = df["language"].value_counts()
    top_languages = language_counts.nlargest(10)


    # Check the rate limit before fetching the number of commits for each repository
    check_rate_limit()
    df["commits"] = df["full_name"].swifter.apply(fetch_commits_for_row)

    # Check the rate limit before checking if the repository has a 'tests' or 'test' directory
    check_rate_limit()
    df["has_tests"] = df["full_name"].swifter.apply(has_tests)

    # Check the rate limit before checking if the repository has a CI/CD workflow
    check_rate_limit()
    df["has_ci_cd"] = df["full_name"].swifter.apply(has_ci_cd)

    # Q2: Top 10 repositories with the most commits
    most_commits = df.nlargest(10, "commits")
    # Filter repositories with tests
    df_with_tests = df[df["has_tests"] == True]

    # Q3: Top 10 programming languages that follow the test-driven development approach
    top_languages_tests = df_with_tests["language"].value_counts().nlargest(10)

    # Filter repositories with CI/CD workflow
    df_with_tests_and_ci_cd = df_with_tests[df_with_tests["has_ci_cd"] == True]

    # Q4: Top 10 programming languages that follow test-driven development and DevOps approach
    top_languages_tests_ci_cd = (
        df_with_tests_and_ci_cd["language"].value_counts().nlargest(10)
    )

    return top_languages, most_commits, top_languages_tests, top_languages_tests_ci_cd


def plot_data(
    top_languages, most_commits, num_repos_with_tests, num_repos_with_ci_cd, repos
):
    # Q1: Plot the top 10 programming languages
    plt.figure()
    plt.bar(top_languages.index, top_languages.values)
    plt.title("Top 10 Programming Languages")
    plt.xlabel("Language")
    plt.ylabel("Number of Projects")
    plt.xticks(rotation=45)
    plt.savefig("top_10_programming_languages.png")

    # Q2: Plot the top 10 repositories with the most commits
    plt.figure()
    plt.bar(most_commits["name"], most_commits["commits"])
    plt.title("Top 10 Repositories with the Most Commits")
    plt.xlabel("Repository")
    plt.xticks(rotation=45)
    plt.ylabel("Number of Commits")
    plt.savefig("top_10_repositories_with_most_commits.png")

    # Q3: Plot the percentage of repositories with 'tests' or 'test' directory
    plt.figure()
    perc_repos_with_tests = (num_repos_with_tests / len(repos)) * 100
    perc_repos_without_tests = 100 - perc_repos_with_tests
    bars = plt.bar(["Yes", "No"], [perc_repos_with_tests, perc_repos_without_tests])
    plt.title("Percentage of Repositories with 'tests' or 'test' Directory")
    plt.xlabel("Has 'tests' or 'test' Directory")
    plt.ylabel("Percentage of Repositories (%)")
    for bar in bars:
        yval = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2.0,
            yval,
            f"{yval:.2f}%",
            ha="center",
            va="bottom",
        )
    plt.savefig("percentage_of_repositories_with_tests_or_test_directory.png")

    # Q4: Plot the percentage of repositories with CI/CD workflow
    plt.figure()
    perc_repos_with_ci_cd = (num_repos_with_ci_cd / len(repos)) * 100
    perc_repos_without_ci_cd = 100 - perc_repos_with_ci_cd
    bars = plt.bar(["Yes", "No"], [perc_repos_with_ci_cd, perc_repos_without_ci_cd])
    plt.title("Percentage of Repositories with CI/CD Workflow")
    plt.xlabel("Has CI/CD Workflow")
    plt.ylabel("Percentage of Repositories (%)")
    for bar in bars:
        yval = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2.0,
            yval,
            f"{yval:.2f}%",
            ha="center",
            va="bottom",
        )
    plt.savefig("percentage_of_repositories_with_ci_cd_workflow.png")


def main():
    # make a list of dates from today to n_days ago
    dates = [datetime.date.today() - datetime.timedelta(days=i) for i in range(N_DAYS)]

    # create an empty dataframe to store the results
    result_df = pd.DataFrame()

    for date in dates:
        # Fetch the repos created or updated on this date
        repos = fetch_repos(date)

        # Analyze the repos
        (
            top_languages,
            most_frequently_updated,
            num_repos_with_tests,
            num_repos_with_ci_cd,
        ) = analyze_repos(repos)

        # Append the data to result_df
        result_df = result_df.append(
            {
                "date": date,
                "top_languages": top_languages,
                "most_frequently_updated": most_frequently_updated,
                "num_repos_with_tests": num_repos_with_tests,
                "num_repos_with_ci_cd": num_repos_with_ci_cd,
            },
            ignore_index=True,
        )

        # Save result_df to a CSV file
        result_df.to_csv("results.csv", index=False)

    # Plot the data
    plot_data(result_df)


if __name__ == "__main__":
    main()

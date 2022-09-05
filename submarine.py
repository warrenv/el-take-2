#!/usr/bin/env python

""" submarine """
import os
import subprocess

# pyGithub
from github import Github

CONFIG = "config/list.txt"


def main():
    repo_cache = {}
    token = os.getenv("GITHUB_TOKEN", "...")
    gh = Github(token)

    with open(CONFIG, encoding="utf8") as f:
        for line in f:
            if not line.strip() or line[0] == "#":
                continue
            print(line.strip())

            fields = line.strip().split(" ")
            if len(fields) < 2:
                print(f"Skipping. Must have at least 2 fields: {line}")
                continue

            repo_name = fields[0]
            # cache repo info to save api requests.
            short_repo = (
                repo_name.replace("https://github.com/", "")
                .replace("git@github.com:", "")
                .replace(".git", "")
            )
            if not repo_cache.get(short_repo):
                repo_cache[short_repo] = gh.get_repo(short_repo)
            repo = repo_cache[short_repo]

            submodule_names = fields[1]
            submodules = list(set(submodule_names.split(",")))

            reviewers = []
            if len(fields) == 3:
                reviewer_emails = fields[2]
                reviewers = list(
                    set(reviewer_emails.split(",")).difference([repo.owner.login])
                )

            print("############################################################")
            print(f"Processing repo {repo_name}...")
            print("############################################################")

            for repo_contents in repo.get_contents(""):
                # Checks if the instance is a submodule and is one we want to check,
                # then fetches it's details.
                if (
                    repo_contents.raw_data.get("type") == "submodule"
                    and repo_contents.name in submodules
                ):
                    submodule_repo = (
                        repo_contents.raw_data.get("submodule_git_url")
                        .replace("git@github.com:", "")
                        .replace("https://github.com/", "")
                        .replace(".git", "")
                    )

                    content_sha = (
                        gh.get_repo(submodule_repo)
                        .get_commits(sha="main")
                        .get_page(0)[0]
                        .sha
                    )
                    print(f"submodule '{repo_contents.name}' sha: {content_sha}")

                    if content_sha != repo_contents.raw_data.get("sha"):
                        print(f"{repo_contents.name} submodule is OUT OF DATE.")

                        # check for existing PR
                        existing_pr = ""
                        pulls = repo.get_pulls(
                            state="open", sort="created", base="main"
                        )
                        for pull_request in pulls:
                            if (
                                pull_request.title
                                == f"Update submodule content {content_sha}"
                            ):
                                existing_pr = pull_request.number
                                break

                        if existing_pr:
                            print(f"PR #{existing_pr} already exists.")
                            continue

                        try:
                            commit = subprocess.run(
                                [
                                    f"./update-submodule.sh {repo_name} {repo_contents.name}"
                                ],
                                capture_output=True,
                                shell=True,
                                check=True,
                            )

                            if commit.returncode == 0:
                                # open PR
                                pr_branch = commit.stdout.decode("utf-8").strip()
                                print(f"Opening PR for branch: {pr_branch}")

                                new_pr = repo.create_pull(
                                    title=f"Update submodule {repo_contents.name} {content_sha}",
                                    body=f"Update submodule {repo_contents.name} to {content_sha}",
                                    head=pr_branch,
                                    base="main",
                                )

                                print(f"Opened PR #{new_pr.number} - {new_pr.title}")

                                # add reviewers
                                try:
                                    if len(reviewers) != 0:
                                        print(f"Update PR with reviewers: {reviewers}")
                                        new_pr.create_review_request(
                                            reviewers=reviewers
                                        )
                                except:
                                    print(
                                        "Could not assign reviewers. Possible unknown collaborators in the list?"
                                    )
                        except subprocess.CalledProcessError as error:
                            print(error)
                    else:
                        print(f"{repo_contents.name} submodule is up-to-date.")

                    print("")


if __name__ == "__main__":
    main()

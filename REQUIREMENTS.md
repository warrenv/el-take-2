Our code is organized such that some of the repositories are included as submodules in others.
Since we update these dependencies regularly, it’s important to keep them updated in the
repositories that use them.

Given a submodule named 'content', please implement a solution to create a GitHub pull
request which updates the version of that submodule to the latest commit on its 'main' branch.
Your solution should run on a regular schedule and also automatically add a set of GitHub users
as reviewers on the pull request.

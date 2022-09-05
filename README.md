# Submarine

This program iterates over a list of 'consumer' github url's looking for
submodules. When it finds a match, it checks the current commit sha of the
submodule repo against the commit of the submodule in the consumer repo.
If they differ, and there is no matching open PR, the repo is cloned
and a commit is created on a new branch and pushed to the remote. A PR
is then created.

### Pre-reqs

If you are comfortable setting up python virtenv and
willing to export env vars by hand, you can skip
installing direnv. But it really makes things easier...

- install [direnv](https://docs.github.com/en/enterprise-server@3.4/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
    direnv is used to setup the python environment and
    export required environment variables.

- [Create an access token in github](https://docs.github.com/en/enterprise-server@3.4/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token()

### Setup

Create `config/list.txt` as shown below and update it
with one or more repos containing submodules.
You can choose which submodules are checked.

```bash
  $ cp envrc.example .envrc
  $ direnv allow
  $ direnv edit .envrc
  # update this line with your github access token.
  # export GITHUB_TOKEN="_YOUR_GITHUB_ACCESS_TOKEN_"

  $ mkdir config
  $ cp list.txt.example config/list.txt

  $ pip install pygithub
```

### Run

```bash
  $ ./submarine.py
```

### Production

Add a crontab entry to run the script at the desired interval.  Given the
[requierments](REQUIREMENTS.txt), this is a bit tricky. Googling will
reveal some ways to run tasks every N weeks using a wrapper script.

If you have ssh access to production servers/containers, this above
command can be manually run as needed.

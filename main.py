import requests, sys, os, subprocess
from git import Repo, remote, exc
from requests.auth import HTTPBasicAuth
from github import Github, GithubException


assert len(sys.argv) == 4, 'A from username, to username and token for the to account must be specified!';

fromUsername = sys.argv[1];
toUsername = sys.argv[2];
token = sys.argv[3];

# Authentication
remote = f'https://{toUsername}:{token}@github.com/';
user = Github(toUsername, token).get_user();

repositories = requests.get(f'https://api.github.com/users/{fromUsername}/repos').json();

if (not os.path.isdir('./repos')): os.mkdir('./repos');

for repository in repositories:
    fullRepoName = repository['full_name'];
    repoName = repository['name'];
    localRepoPath = f'./repos/{repoName}';
    repoUrl = f'{remote}{fullRepoName}.git';

    # Clone the repository to the local system
    try:
        Repo.clone_from(repoUrl, localRepoPath);
    except (exc.GitCommandError):
        print(f'warning: {repoName} already exists in the local repository directory. Continuing without cloning');


    # Create a repository on the new account
    try:
        user.create_repo(repoName);
    except (GithubException):
        print(f'warning: {repoName} is already a remote repository on the account. Continuing without creating a new repository');

    repo = Repo(localRepoPath);

    # Push the cloned files to the new account
    repo.index.commit('init');
    
    # Create the remote to push to
    try:
        remote = repo.create_remote('clone', f'{remote}{toUsername}/{repoName}');
    except (exc.GitCommandError):
        print(f'warning: A "clone" remote already exists. Continuing without making a new remote');

    try:
        repo.git.push('clone', 'main');
    except (exc.GitCommandError):
        print(f'error: The provided personal access token is incorrect for the account: {toUsername}. If you used your password, check the README for information on getting your token');

print(f'Finished transfering repositories from {fromUsername} to {toUsername}!');
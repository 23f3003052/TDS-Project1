import subprocess
import os
import requests
import time

def create_github_repo(task_id, github_token):
    """
    Creates a new public GitHub repository using GitHub API
    """
    
    repo_name = task_id  # Use task ID as repo name
    
    # GitHub API endpoint for creating repos
    url = "https://api.github.com/user/repos"
    
    # Request headers
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github+json"
    }
    
    # Repository configuration
    data = {
        "name": repo_name,
        "description": f"Auto-generated project for {task_id}",
        "private": False,  # Must be public for GitHub Pages
        "auto_init": False  # We'll push our own files
    }
    
    # Make the API request
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        repo_data = response.json()
        return repo_data['html_url'], repo_data['clone_url']
    else:
        raise Exception(f"Failed to create repo: {response.text}")

def enable_github_pages(username, repo_name, github_token):
    """
    Enables GitHub Pages for the repository
    """
    
    url = f"https://api.github.com/repos/{username}/{repo_name}/pages"
    
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github+json"
    }
    
    data = {
        "source": {
            "branch": "main",
            "path": "/"
        }
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    # 201 = created, 409 = already exists (both OK)
    if response.status_code in [201, 409]:
        return f"https://{username}.github.io/{repo_name}/"
    else:
        raise Exception(f"Failed to enable Pages: {response.text}")

def push_to_github(local_path, clone_url, github_token):
    """
    Pushes local files to GitHub repository
    """
    
    os.chdir(local_path)
    
    # Initialize git
    subprocess.run(["git", "init"], check=True)
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)
    subprocess.run(["git", "branch", "-M", "main"], check=True)
    
    # Add remote with token authentication
    authenticated_url = clone_url.replace(
        "https://", 
        f"https://{github_token}@"
    )
    subprocess.run(["git", "remote", "add", "origin", authenticated_url], check=True)
    
    # Push to GitHub
    subprocess.run(["git", "push", "-u", "origin", "main"], check=True)
    
    # Get the commit SHA
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], 
        capture_output=True, 
        text=True, 
        check=True
    )
    commit_sha = result.stdout.strip()
    
    return commit_sha
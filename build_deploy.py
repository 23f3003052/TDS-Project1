import os
import tempfile
import shutil
import subprocess
import openai
import time
from llm_generator import generate_app_code, generate_readme
from github_deploy import create_github_repo, enable_github_pages, push_to_github
from notification import send_evaluation_notification

def build_and_deploy(email, task_id, round_num, nonce, brief, checks, evaluation_url, attachments):
    """
    Complete build and deploy pipeline
    """
    
    # Get GitHub token from environment
    github_token = os.environ.get('GITHUB_TOKEN')
    github_username = os.environ.get('GITHUB_USERNAME')
    
    # Step 1: Generate the application code
    print(f"Generating code for {task_id}...")
    html_code = generate_app_code(brief, checks, attachments)
    readme_content = generate_readme(brief, task_id)
    
    # Step 2: Create a temporary directory for files
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Step 3: Write files to disk
        # Write index.html
        with open(os.path.join(temp_dir, 'index.html'), 'w') as f:
            f.write(html_code)
        
        # Write README.md
        with open(os.path.join(temp_dir, 'README.md'), 'w') as f:
            f.write(readme_content)
        
        # Write LICENSE (MIT License)
        mit_license = """MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""
        
        with open(os.path.join(temp_dir, 'LICENSE'), 'w') as f:
            f.write(mit_license)
        
        # Save attachments if any
        for attachment in attachments:
            filename = attachment['name']
            data_url = attachment['url']
            # Parse data URL and save file
            # (You'll need to implement data URL parsing)
            save_attachment(temp_dir, filename, data_url)
        
        # Step 4: Create GitHub repository
        print(f"Creating GitHub repository...")
        repo_url, clone_url = create_github_repo(task_id, github_token)
        
        # Step 5: Push code to GitHub
        print(f"Pushing code to GitHub...")
        commit_sha = push_to_github(temp_dir, clone_url, github_token)
        
        # Step 6: Enable GitHub Pages
        print(f"Enabling GitHub Pages...")
        pages_url = enable_github_pages(github_username, task_id, github_token)
        
        # Step 7: Wait for Pages to deploy (usually takes 1-2 minutes)
        print("Waiting for GitHub Pages to deploy...")
        time.sleep(120)  # Wait 2 minutes
        
        # Step 8: Send notification to evaluation URL
        print(f"Sending notification...")
        send_evaluation_notification(
            evaluation_url,
            email,
            task_id,
            round_num,
            nonce,
            repo_url,
            commit_sha,
            pages_url
        )
        
        print(f"✓ Successfully deployed {task_id} to {pages_url}")
        return True
        
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir)

def save_attachment(directory, filename, data_url):
    """
    Parses data URL and saves file
    """
    import base64
    
    # data URLs look like: data:image/png;base64,iVBORw0KG...
    if data_url.startswith('data:'):
        # Extract the base64 data
        header, encoded = data_url.split(',', 1)
        data = base64.b64decode(encoded)
        
        # Write to file
        filepath = os.path.join(directory, filename)
        with open(filepath, 'wb') as f:
            f.write(data)




def revise_and_deploy(email, task_id, round_num, nonce, brief, checks, evaluation_url, attachments):
    """
    Handles revision requests (round 2)
    """
    
    github_token = os.environ.get('GITHUB_TOKEN')
    github_username = os.environ.get('GITHUB_USERNAME')
    
    # Step 1: Clone the existing repository
    print(f"Cloning existing repository...")
    temp_dir = tempfile.mkdtemp()
    repo_url = f"https://github.com/{github_username}/{task_id}.git"
    
    authenticated_url = repo_url.replace(
        "https://",
        f"https://{github_token}@"
    )
    
    subprocess.run(
        ["git", "clone", authenticated_url, temp_dir],
        check=True
    )
    
    os.chdir(temp_dir)
    
    # Step 2: Read existing code
    with open('index.html', 'r') as f:
        existing_code = f.read()
    
    # Step 3: Generate modification using LLM
    print(f"Generating code modifications...")
    modified_code = generate_code_modification(existing_code, brief, checks)
    
    # Step 4: Write updated code
    with open('index.html', 'w') as f:
        f.write(modified_code)
    
    # Step 5: Update README
    updated_readme = generate_readme(brief, task_id)
    with open('README.md', 'w') as f:
        f.write(updated_readme)
    
    # Step 6: Commit and push changes
    print(f"Pushing updates...")
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", f"Round {round_num} updates"], check=True)
    subprocess.run(["git", "push"], check=True)
    
    # Step 7: Get new commit SHA
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True
    )
    commit_sha = result.stdout.strip()
    
    # Step 8: Wait for Pages to redeploy
    time.sleep(120)
    
    # Step 9: Send notification
    pages_url = f"https://{github_username}.github.io/{task_id}/"
    repo_url = f"https://github.com/{github_username}/{task_id}"
    
    send_evaluation_notification(
        evaluation_url,
        email,
        task_id,
        round_num,
        nonce,
        repo_url,
        commit_sha,
        pages_url
    )
    
    # Cleanup
    shutil.rmtree(temp_dir)
    
    return True

def generate_code_modification(existing_code, brief, checks):
    """
    Uses LLM to modify existing code based on new requirements
    """
    
    prompt = f"""
    You are modifying an existing web application.
    
    Current code:
    ```
    {existing_code}
    ```
    
    New requirements:
    {brief}
    
    Additional checks:
    {chr(10).join(f"- {check}" for check in checks)}
    
    Modify the code to meet the new requirements while keeping existing functionality.
    Return ONLY the complete modified HTML code, no explanations.
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a web development expert."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=3000
    )
    
    return response.choices[0].message.content.strip()

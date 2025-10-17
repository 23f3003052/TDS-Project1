import requests
import time

def send_evaluation_notification(evaluation_url, email, task_id, round_num, nonce, repo_url, commit_sha, pages_url):
    """
    Sends completion notification to evaluation API with retry logic
    """
    
    # Prepare the payload
    payload = {
        "email": email,
        "task": task_id,
        "round": round_num,
        "nonce": nonce,
        "repo_url": repo_url,
        "commit_sha": commit_sha,
        "pages_url": pages_url
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # Retry logic: 1, 2, 4, 8 second delays
    retry_delays = [1, 2, 4, 8]
    
    for attempt, delay in enumerate(retry_delays + [0]):
        try:
            response = requests.post(
                evaluation_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"✓ Notification sent successfully")
                return True
            else:
                print(f"⚠ Notification failed with status {response.status_code}")
                
                if attempt < len(retry_delays):
                    print(f"  Retrying in {retry_delays[attempt]} seconds...")
                    time.sleep(retry_delays[attempt])
                    
        except requests.exceptions.RequestException as e:
            print(f"⚠ Network error: {str(e)}")
            
            if attempt < len(retry_delays):
                print(f"  Retrying in {retry_delays[attempt]} seconds...")
                time.sleep(retry_delays[attempt])
    
    print("✗ Failed to send notification after all retries")
    return False
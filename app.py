from flask import Flask, request, jsonify
import json
import os
from build_deploy import build_and_deploy, revise_and_deploy

app = Flask(__name__)

# Store your secret (in production, use environment variables)
MY_SECRET = os.environ.get('MY_SECRET', 'itsme')



@app.route('/api-endpoint', methods=['POST'])
def handle_request():
    """
    This endpoint receives POST requests from instructors
    """
    try:
        # Get the JSON data from the request
        data = request.get_json()
        
        # Step 1: Verify the secret matches
        if data.get('secret') != MY_SECRET:
            return jsonify({"error": "Invalid secret"}), 403
        
        # Step 2: Extract important information
        email = data.get('email')
        task_id = data.get('task')
        round_num = data.get('round')
        nonce = data.get('nonce')
        brief = data.get('brief')
        checks = data.get('checks')
        evaluation_url = data.get('evaluation_url')
        attachments = data.get('attachments', [])
        
        # Step 3: Process the request
        if round_num == 1:
            # Build phase
            result = build_and_deploy(
                email, task_id, round_num, nonce, 
                brief, checks, evaluation_url, attachments
            )
        else:
            # Revision phase (round 2)
            result = revise_and_deploy(
                email, task_id, round_num, nonce,
                brief, checks, evaluation_url, attachments
            )
        
        return jsonify({"status": "success", "message": "Processing"}), 200
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run the server
    app.run(host='0.0.0.0', port=5000, debug=True)
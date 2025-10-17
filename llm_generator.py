import openai
import os

# Set your OpenAI API key
openai.api_key = os.environ.get('OPENAI_API_KEY')

def generate_app_code(brief, checks, attachments):
    """
    Uses an LLM to generate the HTML/CSS/JS code for the app
    """
    
    # Create a detailed prompt for the LLM
    prompt = f"""
    You are an expert web developer. Create a complete, single-page HTML application.
    
    Requirements:
    {brief}
    
    The app must pass these checks:
    {chr(10).join(f"- {check}" for check in checks)}
    
    {"Attachments are available as: " + ", ".join(att['name'] for att in attachments) if attachments else ""}
    
    Generate a complete index.html file with embedded CSS and JavaScript.
    Include all necessary CDN links for libraries.
    Make it professional and functional.
    
    Return ONLY the HTML code, no explanations.
    """
    
    try:
        # Call OpenAI API (using GPT-4 or GPT-3.5-turbo)
        response = openai.ChatCompletion.create(
            model="gpt-4",  # or "gpt-3.5-turbo" for lower cost
            messages=[
                {"role": "system", "content": "You are a web development expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=3000
        )
        
        # Extract the generated code
        html_code = response.choices[0].message.content
        
        # Clean up the code (remove markdown code blocks if present)
        html_code = html_code.replace("``````", "").strip()
        
        return html_code
        
    except Exception as e:
        print(f"LLM Error: {str(e)}")
        raise

def generate_readme(brief, task_id):
    """
    Generates a professional README.md file
    """
    
    prompt = f"""
    Create a professional README.md for a GitHub repository.
    
    Project: {task_id}
    Description: {brief}
    
    Include these sections:
    - Project title and description
    - Setup instructions
    - Usage guide
    - Code explanation (brief technical overview)
    - License (MIT)
    
    Make it clear, professional, and well-formatted in Markdown.
    Return ONLY the markdown, no explanations.
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a technical writer."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1500
    )
    
    readme = response.choices[0].message.content.strip()
    return readme
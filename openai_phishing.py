import os
import logging
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Gemini AI client
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def detect_phishing(email_body):
    """Send the email body to Gemini AI for phishing detection."""
    if not email_body:
        return False, ""

    prompt = f"Please carefully analyze the following email body for any phishing links, malicious content, or suspicious activity. If you find any, explain why and identify the specific elements that make the email malicious. Respond with 'Yes' if the email is phishing, followed by a detailed explanation. If it is not phishing, respond with 'No' and provide a very brief note explaining why it is safe:\n\n{email_body}\n\nIs this email phishing?"

    try:
        # Use Gemini's generative model
        model = genai.GenerativeModel('gemini-pro')  # Use the 'gemini-pro' model
        response = model.generate_content(prompt)

        result = response.text.strip().lower()
        if "yes" in result:
            return True, result  # Return True and the detailed explanation if phishing detected
        else:
            return False, "This email appears safe."  # Return False with a brief note if no phishing detected

    except Exception as e:
        logger.error(f"Error with Gemini AI: {e}")
        return False, str(e)  # Return the error message if the API call fails
"""
Test script to verify LLM connection is working.
Run this script to check if your local LLM server is properly configured.
"""
import os
import sys

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
sys.path.insert(0, src_dir)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Set OpenAI API key to prevent errors
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "NA")

# Import LLM configuration
from meeting_minutes.utils.llm_config import get_llm

def test_llm_connection():
    """Test connection to the LLM."""
    try:
        print("Testing LLM connection...")
        llm = get_llm()
        response = llm.invoke([{"role": "user", "content": "Hello, test connection. Respond with a short message."}])
        print("LLM response:", response)
        print("✅ Connection successful!")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\nPossible issues:")
        print("1. Is your local LLM server running at http://localhost:1337/v1?")
        print("2. Check if the LLM server requires a different configuration.")
        print("3. Verify that no environment variables are overriding your settings.")
        return False

if __name__ == "__main__":
    test_llm_connection()

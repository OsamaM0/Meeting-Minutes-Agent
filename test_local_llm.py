"""
Test if the local LLM is working properly.
This script will try to call the local LLM directly, bypassing CrewAI.
"""
import json
import os
import sys

import requests

# Add src to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
sys.path.insert(0, src_dir)

# Import configuration after src is in path
from meeting_minutes.config.app_config import LLM_SERVER


def test_local_llm_direct():
    """Test direct connection to local LLM without using any library."""
    print("Testing direct connection to local LLM...")

    # Define endpoint using config
    endpoint = f"{LLM_SERVER['base_url']}/chat/completions"

    # Define headers
    headers = {"Content-Type": "application/json"}

    # Define data
    data = {
        "model": "gpt-4o",
        "messages": [
            {"role": "user", "content": "Say hello in a simple short sentence"}
        ],
        "temperature": 0.7,
    }

    try:
        # Send request
        response = requests.post(endpoint, headers=headers, json=data, timeout=10)

        # Check if request was successful
        if response.status_code == 200:
            print("✅ Local LLM is working!")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            content = response.json()["choices"][0]["message"]["content"]
            print(f"\nContent: {content}")
            return True
        else:
            print(f"❌ Local LLM returned status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error connecting to local LLM: {e}")
        return False


def test_with_langchain():
    """Test connection using LangChain."""
    print("\nTesting connection using LangChain...")

    try:
        from langchain_openai import ChatOpenAI

        # Create LLM using config
        llm = ChatOpenAI(
            model_name="gpt-4o",
            base_url=LLM_SERVER["base_url"],
            api_key=LLM_SERVER["api_key"],
            temperature=0.7,
        )

        # Test LLM
        response = llm.invoke(
            [{"role": "user", "content": "Say hello in a simple short sentence"}]
        )
        print("✅ LangChain test successful!")
        print(f"Response: {response}")
        return True
    except Exception as e:
        print(f"❌ Error using LangChain: {e}")
        return False


def test_with_openai_sdk():
    """Test connection using OpenAI SDK."""
    print("\nTesting connection using OpenAI SDK...")

    try:
        import openai

        # Configure client using config
        client = openai.OpenAI(
            base_url=LLM_SERVER["base_url"], api_key=LLM_SERVER["api_key"]
        )

        # Test completion
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": "Say hello in a simple short sentence"}
            ],
            temperature=0.7,
        )

        print("✅ OpenAI SDK test successful!")
        print(f"Response: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"❌ Error using OpenAI SDK: {e}")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("LOCAL LLM CONNECTION TEST")
    print("=" * 50)

    # Run all tests
    direct_test = test_local_llm_direct()
    langchain_test = test_with_langchain()
    openai_test = test_with_openai_sdk()

    # Print summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Direct API test: {'✅ PASSED' if direct_test else '❌ FAILED'}")
    print(f"LangChain test: {'✅ PASSED' if langchain_test else '❌ FAILED'}")
    print(f"OpenAI SDK test: {'✅ PASSED' if openai_test else '❌ FAILED'}")

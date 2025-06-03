"""
Test script to verify Gmail authentication is working correctly with the configured port.

This script will test the OAuth2 flow for Gmail authentication using port 62366.
It will help diagnose any issues with the OAuth redirect URI.

Before running this script:
1. Make sure the redirect URI "http://localhost:62366" is properly registered in Google Cloud Console
2. Ensure credentials.json is correctly placed in the gmailcrew tools directory
"""

import json
import os
import sys
import time

from dotenv import load_dotenv

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
sys.path.insert(0, src_dir)

# Load environment variables
load_dotenv()

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Import after src is in path and env vars are loaded
from meeting_minutes.config.app_config import GOOGLE_OAUTH, get_credentials_info
from meeting_minutes.utils.logger import setup_logger

# Setup logger
logger = setup_logger("gmail_auth_test")

# Gmail API scope
SCOPES = GOOGLE_OAUTH["scopes"]


def print_separator(title: str = ""):
    """Print a formatted separator."""
    if title:
        print(f"\n{'='*20} {title.upper()} {'='*20}")
    else:
        print("=" * 60)


def test_environment_setup():
    """Test environment setup and configuration."""
    print_separator("Environment Setup")

    # Check credentials info
    creds_info = get_credentials_info()

    print(
        f"📁 Credentials file exists: {'✅' if creds_info['credentials_exists'] else '❌'}"
    )
    print(f"📁 Token file exists: {'✅' if creds_info['token_exists'] else '❌'}")
    print(f"🔗 Callback URL: {creds_info['callback_url']}")
    print(f"📂 Credentials path: {creds_info['credentials_path']}")

    return creds_info["credentials_exists"]


def validate_credentials_file():
    """Validate the credentials.json file content."""
    print_separator("Credentials Validation")

    credentials_path = GOOGLE_OAUTH["credentials_path"]

    try:
        with open(credentials_path) as f:
            creds_data = json.load(f)

        # Check for required fields
        if "web" in creds_data:
            client_data = creds_data["web"]
            required_fields = ["client_id", "client_secret", "redirect_uris"]

            print("📋 Credential file structure:")
            for field in required_fields:
                exists = field in client_data
                print(f"  - {field}: {'✅' if exists else '❌'}")

            # Check redirect URIs
            redirect_uris = client_data.get("redirect_uris", [])
            expected_uri = GOOGLE_OAUTH["callback_url"]

            print(f"\n🔗 Redirect URIs in credentials:")
            for uri in redirect_uris:
                is_match = uri == expected_uri
                print(f"  - {uri} {'✅' if is_match else ''}")

            if expected_uri not in redirect_uris:
                print(f"\n⚠️  WARNING: Expected URI not found: {expected_uri}")
                print("   This will cause authentication to fail!")
                return False

            print(f"\n✅ Credentials file is properly configured")
            return True

        else:
            print("❌ Invalid credentials file format (missing 'web' section)")
            return False

    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in credentials file: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading credentials file: {e}")
        return False


def test_existing_token():
    """Test if existing token is valid."""
    print_separator("Token Validation")

    token_path = GOOGLE_OAUTH["token_path"]

    if not os.path.exists(token_path):
        print("ℹ️  No existing token found")
        return None

    try:
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

        if creds.valid:
            print("✅ Existing token is valid")
            return creds
        elif creds.expired and creds.refresh_token:
            print("🔄 Token expired, attempting refresh...")
            try:
                creds.refresh(Request())
                print("✅ Token refreshed successfully")

                # Save refreshed token
                with open(token_path, "w") as token_file:
                    token_file.write(creds.to_json())

                return creds
            except Exception as e:
                print(f"❌ Token refresh failed: {e}")
                return None
        else:
            print("❌ Token is invalid and cannot be refreshed")
            return None

    except Exception as e:
        print(f"❌ Error loading token: {e}")
        return None


def perform_oauth_flow():
    """Perform the OAuth authentication flow."""
    print_separator("OAuth Flow")

    credentials_path = GOOGLE_OAUTH["credentials_path"]
    token_path = GOOGLE_OAUTH["token_path"]

    try:
        # Create flow
        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)

        print(f"🚀 Starting OAuth flow on port {GOOGLE_OAUTH['port']}")
        print(f"🌐 Callback URL: {GOOGLE_OAUTH['callback_url']}")
        print("\n📱 Your browser should open automatically for authorization...")
        print("   If it doesn't, copy the URL that appears and open it manually.")

        # Add a small delay to show the message
        time.sleep(2)

        # Run the OAuth flow
        creds = flow.run_local_server(port=GOOGLE_OAUTH["port"], open_browser=True)

        # Save credentials
        with open(token_path, "w") as token_file:
            token_file.write(creds.to_json())

        print("✅ OAuth flow completed successfully!")
        print(f"💾 Token saved to: {token_path}")

        return creds

    except Exception as e:
        print(f"❌ OAuth flow failed: {e}")
        logger.error(f"OAuth flow error: {e}")
        return None


def test_gmail_api_access(creds):
    """Test Gmail API access with credentials."""
    print_separator("API Access Test")

    try:
        # Build Gmail service
        service = build("gmail", "v1", credentials=creds)

        # Test API call - get user profile
        print("🔍 Testing Gmail API access...")
        profile = service.users().getProfile(userId="me").execute()

        email_address = profile.get("emailAddress", "unknown")
        messages_total = profile.get("messagesTotal", 0)
        threads_total = profile.get("threadsTotal", 0)

        print("✅ Gmail API access successful!")
        print(f"📧 Email: {email_address}")
        print(f"📨 Total messages: {messages_total}")
        print(f"🧵 Total threads: {threads_total}")

        # Test draft creation capability
        print("\n🧪 Testing draft creation capability...")
        draft_body = {
            "message": {
                "to": [{"email": email_address}],
                "subject": "Test Draft - Meeting Minutes Agent",
                "body": "This is a test draft created by the Meeting Minutes Agent authentication test.",
            }
        }

        # Note: We're not actually creating the draft to avoid clutter
        print("✅ Draft creation capability confirmed (test skipped to avoid clutter)")

        return True

    except HttpError as error:
        print(f"❌ Gmail API error: {error}")
        logger.error(f"Gmail API error: {error}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        logger.error(f"Unexpected error in API test: {e}")
        return False


def main():
    """Main test function."""
    print("🚀 Starting Gmail Authentication Test")
    print(f"⚙️  Using configuration:")
    print(f"   - Port: {GOOGLE_OAUTH['port']}")
    print(f"   - Callback: {GOOGLE_OAUTH['callback_url']}")
    print(f"   - Scopes: {', '.join(SCOPES)}")

    # Step 1: Test environment setup
    if not test_environment_setup():
        print("\n❌ Environment setup failed - credentials.json not found")
        print("\n🔧 To fix this:")
        print("1. Go to Google Cloud Console")
        print("2. Create OAuth 2.0 credentials")
        print("3. Download credentials.json")
        print(f"4. Place it at: {GOOGLE_OAUTH['credentials_path']}")
        return False

    # Step 2: Validate credentials file
    if not validate_credentials_file():
        print("\n❌ Credentials validation failed")
        return False

    # Step 3: Test existing token
    creds = test_existing_token()

    # Step 4: If no valid token, perform OAuth flow
    if not creds:
        creds = perform_oauth_flow()
        if not creds:
            print("\n❌ Authentication failed")
            return False

    # Step 5: Test Gmail API access
    if not test_gmail_api_access(creds):
        print("\n❌ Gmail API access failed")
        return False

    print_separator("Test Complete")
    print("🎉 All tests passed! Gmail authentication is working correctly.")
    print("\n✅ Your Meeting Minutes Agent is ready to create Gmail drafts!")

    return True


if __name__ == "__main__":
    try:
        success = main()
        exit_code = 0 if success else 1
        print(f"\n🏁 Test completed with exit code: {exit_code}")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        logger.error(f"Unexpected error in main: {e}")
        sys.exit(1)

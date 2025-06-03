"""
Utility script to update the redirect URI in the credentials.json file.

This script will check if the redirect URI in credentials.json matches the configured port,
and update it if necessary.
"""

import json
import os
import sys

from dotenv import load_dotenv

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
sys.path.insert(0, src_dir)

# Load environment variables
load_dotenv()

# Import after src is in path
from meeting_minutes.config.app_config import GOOGLE_OAUTH


def fix_credentials_file():
    """Fix the redirect URI in the credentials.json file."""
    print("=" * 50)
    print("GMAIL CREDENTIALS FIXER")
    print("=" * 50)

    # Get the credentials.json file path
    tools_dir = os.path.join(src_dir, "meeting_minutes", "crews", "gmailcrew", "tools")
    credentials_path = os.path.join(tools_dir, "credentials.json")

    # Check if credentials.json exists
    if not os.path.exists(credentials_path):
        print(f"❌ Error: credentials.json not found at {credentials_path}")
        print("Please download your OAuth credentials from Google Cloud Console first.")
        return False

    # Read current credentials
    try:
        with open(credentials_path) as f:
            creds_data = json.load(f)

        # Get current redirect URIs
        web_config = creds_data.get("web", {})
        redirect_uris = web_config.get("redirect_uris", [])
        js_origins = web_config.get("javascript_origins", [])

        print(f"Current redirect URIs: {redirect_uris}")
        print(f"Current JavaScript origins: {js_origins}")

        # Check if our port is already registered
        expected_uri = GOOGLE_OAUTH["callback_url"]
        expected_origin = f"http://localhost:{GOOGLE_OAUTH['port']}"

        needs_update = False

        # Update redirect URIs if needed
        if expected_uri not in redirect_uris:
            print(f"Adding {expected_uri} to redirect URIs...")
            redirect_uris.append(expected_uri)
            web_config["redirect_uris"] = redirect_uris
            needs_update = True

        # Update JavaScript origins if needed
        if expected_origin not in js_origins:
            print(f"Adding {expected_origin} to JavaScript origins...")
            js_origins.append(expected_origin)
            web_config["javascript_origins"] = js_origins
            needs_update = True

        # Update the credentials file if changes were made
        if needs_update:
            creds_data["web"] = web_config

            # Backup the original file
            backup_path = f"{credentials_path}.bak"
            print(f"Backing up original file to {backup_path}...")
            with open(backup_path, "w") as f:
                json.dump(creds_data, f, indent=4)

            # Write updated credentials
            print("Writing updated credentials.json...")
            with open(credentials_path, "w") as f:
                json.dump(creds_data, f, indent=4)

            print("✅ credentials.json updated successfully!")
            print(
                "\nIMPORTANT: You still need to add this redirect URI in Google Cloud Console:"
            )
            print("1. Go to Google Cloud Console -> Google Auth Platform -> Clients")
            print("2. Edit your OAuth client")
            print(f"3. Add {expected_uri} as an authorized redirect URI")
            print("4. Click Save")
        else:
            print("✅ credentials.json already has the correct redirect URI!")

        return True

    except Exception as e:
        print(f"❌ Error updating credentials.json: {e}")
        return False


if __name__ == "__main__":
    fix_credentials_file()
